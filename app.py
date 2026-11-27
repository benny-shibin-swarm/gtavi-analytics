import re
from collections import Counter
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


st.set_page_config(
    page_title="GTA VI Launch Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS = Path(__file__).resolve().parent / "assets"
GTA_VI_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/d/d6/Grand_Theft_Auto_VI_logo_%28with_gradient%29.svg"
TAKE_TWO = "https://ir.take2games.com/node/32701"
SENSOR_TOWER = "https://sensortower.com/grand-theft-auto-VI/sales-tracker"
WEEKEND = "https://alineaanalytics.substack.com/p/gta-6-sells-449m-copies-makes-40b"
WEEK_ONE = "https://alineaanalytics.substack.com/p/grand-theft-auto-6-a-week-in"
STREAMS = "https://streamscharts.com/news/gta6-livestreaming-week-after-launch"
KAGGLE = "https://www.kaggle.com/datasets/ektarr/gta-vi-user-reviews"
COLORS = ["#ff2a85", "#00d4ff", "#ff9e5e", "#9b5de5", "#00f5d4"]
SCALE = ["#2b0947", "#9d176c", "#ff2a85", "#ff9e5e"]
CHART_SURFACE = "rgba(0,0,0,0)"
CHART_GRID = "#383438"
PS5 = "PlayStation 5"
XBOX = "Xbox Series X|S"
PHASES = {
    "Pre-orders": (32.5, None, 0.74, "Take-Two units · Sensor Tower platform mix"),
    "Day 1": (None, 3.79, 0.74, "Take-Two retail sales · Sensor Tower platform mix"),
    "Opening weekend": (44.9, 4.0, 33.7 / 44.9, "Alinea estimate · retail sales above $4B"),
    "Week 1": (53.0, 4.7, 0.757, "Alinea estimate"),
}
PRICES = {"Standard": 79.99, "Ultimate": 99.99}
ULTIMATE_SHARE = (97.0 - PRICES["Standard"]) / (PRICES["Ultimate"] - PRICES["Standard"])

st.html(ASSETS / "dashboard.css")


@st.cache_data
def load_public_data():
    regional_df = pd.DataFrame([
        {"Country": "United States", "ISO": "USA", "Region": "North America", "Share_Pct": 32.8, "Copies_M": 17.38, "PS5_M": 12.86, "Xbox_M": 4.52},
        {"Country": "France", "ISO": "FRA", "Region": "Europe", "Share_Pct": 9.0, "Copies_M": 4.77, "PS5_M": 3.82, "Xbox_M": 0.95},
        {"Country": "United Kingdom", "ISO": "GBR", "Region": "Europe", "Share_Pct": 7.3, "Copies_M": 3.87, "PS5_M": 2.86, "Xbox_M": 1.01},
        {"Country": "Germany", "ISO": "DEU", "Region": "Europe", "Share_Pct": 5.1, "Copies_M": 2.70, "PS5_M": 2.16, "Xbox_M": 0.54},
        {"Country": "China (Grey Market)", "ISO": "CHN", "Region": "Asia-Pacific", "Share_Pct": 4.7, "Copies_M": 2.49, "PS5_M": 2.19, "Xbox_M": 0.30},
        {"Country": "Brazil", "ISO": "BRA", "Region": "Latin America", "Share_Pct": 4.2, "Copies_M": 2.23, "PS5_M": 1.74, "Xbox_M": 0.49},
        {"Country": "Spain", "ISO": "ESP", "Region": "Europe", "Share_Pct": 3.8, "Copies_M": 2.01, "PS5_M": 1.65, "Xbox_M": 0.36},
        {"Country": "Canada", "ISO": "CAN", "Region": "North America", "Share_Pct": 3.6, "Copies_M": 1.91, "PS5_M": 1.43, "Xbox_M": 0.48},
        {"Country": "Japan", "ISO": "JPN", "Region": "Asia-Pacific", "Share_Pct": 3.1, "Copies_M": 1.64, "PS5_M": 1.56, "Xbox_M": 0.08},
        {"Country": "Australia", "ISO": "AUS", "Region": "Asia-Pacific", "Share_Pct": 2.5, "Copies_M": 1.33, "PS5_M": 0.98, "Xbox_M": 0.35},
        {"Country": "Rest of World", "ISO": "ROW", "Region": "Global Other", "Share_Pct": 23.9, "Copies_M": 12.67, "PS5_M": 8.87, "Xbox_M": 3.80},
    ])

    streaming_platforms = pd.DataFrame([
        {"Platform": "Twitch", "Hours_Watched_M": 186.71, "Share_Pct": 45.2, "Peak_Concurrent_M": 3.31},
        {"Platform": "YouTube Live", "Hours_Watched_M": 114.95, "Share_Pct": 27.8, "Peak_Concurrent_M": 2.85},
        {"Platform": "Kick", "Hours_Watched_M": 111.37, "Share_Pct": 27.0, "Peak_Concurrent_M": 1.75},
    ])

    milestones = pd.DataFrame([
        {"Event": "Trailer 1 Reveal", "Date": "2023-12-04", "YouTube_Views_M": 302.6, "Stream_Hours_Watched_M": 4.98},
        {"Event": "Trailer 2 Reveal", "Date": "2025-05-06", "YouTube_Views_M": 193.0, "Stream_Hours_Watched_M": 3.08},
        {"Event": "Gameplay Showcase", "Date": "2026-08-27", "YouTube_Views_M": 115.4, "Stream_Hours_Watched_M": 12.21},
        {"Event": "Launch Trailer", "Date": "2026-10-15", "YouTube_Views_M": 87.8, "Stream_Hours_Watched_M": 1.37},
        {"Event": "Launch Day (24h)", "Date": "2026-11-19", "YouTube_Views_M": 3500.0, "Stream_Hours_Watched_M": 125.57},
        {"Event": "Week 1 Cumulative", "Date": "2026-11-26", "YouTube_Views_M": 8900.0, "Stream_Hours_Watched_M": 424.05},
    ])

    age_groups = pd.DataFrame([
        {"Age_Bracket": "Under 18 (Shared/Family)", "YouTube_Viewers_Pct": 16.0, "Est_Console_Players_Pct": 11.5},
        {"Age_Bracket": "18–24", "YouTube_Viewers_Pct": 37.5, "Est_Console_Players_Pct": 34.0},
        {"Age_Bracket": "25–34", "YouTube_Viewers_Pct": 31.0, "Est_Console_Players_Pct": 36.5},
        {"Age_Bracket": "35–44", "YouTube_Viewers_Pct": 11.5, "Est_Console_Players_Pct": 13.5},
        {"Age_Bracket": "45+", "YouTube_Viewers_Pct": 4.0, "Est_Console_Players_Pct": 4.5},
    ])

    return regional_df, streaming_platforms, milestones, age_groups



def plot(fig, height=350):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=16, r=18, t=22, b=18),
        paper_bgcolor=CHART_SURFACE,
        plot_bgcolor=CHART_SURFACE,
        font=dict(color="#f8f9fa"),
        legend=dict(orientation="h", y=1.02, yanchor="bottom"),
    )
    fig.update_xaxes(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID)
    fig.update_yaxes(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID)
    st.plotly_chart(fig, width="stretch", theme=None, config={"displaylogo": False})


def market_breakdown(regions, phase, platform, edition, metric):
    units, revenue, ps5_mix, _ = PHASES[phase]
    editions = {"Standard": 1 - ULTIMATE_SHARE, "Ultimate": ULTIMATE_SHARE}
    console_mix = {PS5: ps5_mix, XBOX: 1 - ps5_mix}
    # Infer global denominators from the approximately 30% opening-weekend rate.
    installed_base = {PS5: 33.7 / 0.30, XBOX: 11.2 / 0.30}
    selected_base = sum(installed_base.values()) if platform == "All consoles" else installed_base[platform]
    frames = []
    for console, column in [(PS5, "PS5_M"), (XBOX, "Xbox_M")]:
        if platform != "All consoles" and platform != console:
            continue
        markets = regions[["Country", "Region", "ISO"]].copy()
        weight = regions[column] / regions[column].sum() * console_mix[console]
        for tier, share in editions.items():
            if edition not in ("All editions", tier):
                continue
            segment = markets.assign(Console=console, Edition=tier)
            if metric == "Units sold":
                segment["Value"] = units * weight * share
            elif metric == "Gross revenue":
                revenue_share = share * PRICES[tier] / 97.0
                segment["Value"] = revenue * weight * revenue_share
            else:
                segment["Value"] = 100 * units * weight * share / selected_base
            frames.append(segment)
    return pd.concat(frames, ignore_index=True)


regional_df, streaming_platforms, milestones, age_groups = load_public_data()

with st.sidebar:
    st.image(GTA_VI_LOGO_URL, width=160)
    st.caption("State of Leonida (Nov 2026)")
    st.divider()
    phase = st.radio("Sales window", list(PHASES), index=3)
    platform = st.selectbox("Console Platform View", ["All consoles", PS5, XBOX])
    regions = regional_df["Region"].unique().tolist()
    selected_regions = st.multiselect("Filter Sales by Region", regions, default=regions)

st.markdown(
    f"""
    <div class="vice-hero">
        <div class="vice-hero-text">
            <div class="vice-badge">Welcome to Leonida • Week-1 Global Telemetry</div>
            <h1>Grand Theft Auto VI — Launch & Viewership Analytics</h1>
            <p>
                Interactive market intelligence tracking <strong>regional digital & physical downloads</strong>,
                <strong>PS5 vs. Xbox Series X|S adoption</strong>, <strong>estimated player age demographics</strong>,
                and <strong>live YouTube & livestreaming viewership</strong>.
            </p>
        </div>
        <img class="vice-hero-logo" src="{GTA_VI_LOGO_URL}" alt="Grand Theft Auto VI Logo" />
    </div>
    """,
    unsafe_allow_html=True,
)

units, revenue, _, phase_source = PHASES[phase]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Worldwide units", f"{units:g}M" if units is not None else "Unavailable")
k2.metric(
    "Worldwide retail sales",
    ("$4B+" if phase == "Opening weekend" else f"${revenue:g}B") if revenue is not None else "Unavailable",
)
k3.metric("Week 1 stream watch time", "420.17M hr")
k4.metric("Launch stream peak", "7.91M")
st.caption(f"{phase} sales · {phase_source} | [Streaming data]({STREAMS})")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Downloads & Regions", "YouTube & Livestreams", "Age Group Demographics", "Live YouTube Data Feed",
    "Franchise & Sentiment",
])

with tab1:
    metric_col, edition_col = st.columns(2)
    available_metrics = {
        "Units sold": units is not None,
        "Gross revenue": revenue is not None,
        "Console attach rate": units is not None,
    }
    metric = metric_col.selectbox("Metric", [name for name, available in available_metrics.items() if available])
    edition_options = {"All editions": "All editions"}
    edition_options.update({f"{name} · ${price:.2f}": name for name, price in PRICES.items()})
    edition = edition_options[edition_col.selectbox("Edition", list(edition_options))]
    label = {
        "Units sold": "Units sold (M)",
        "Gross revenue": "Retail sales (USD B)",
        "Console attach rate": "Global attach contribution (pp)",
    }[metric]
    modeled = market_breakdown(regional_df, phase, platform, edition, metric)
    markets = modeled[modeled["Region"].isin(selected_regions)]

    if metric == "Console attach rate":
        rate = modeled["Value"].sum()
        st.metric(f"Estimated global attach rate · {platform}", f"{rate:.1f}%")
        st.caption(
            "Market values show percentage-point contributions to the global attach rate. "
            "The global console bases are inferred from Alinea’s roughly 30% opening-weekend attach rate. "
            "Country-level installed bases are unavailable."
        )
    if markets.empty:
        st.info("Select at least one region to see the market distribution.")
    else:
        countries = markets[markets["ISO"] != "ROW"]
        split = "Edition" if platform != "All consoles" and edition == "All editions" else "Console"
        if countries.empty:
            st.info("Rest of World is available in the regional summary below.")
        else:
            map_col, bar_col = st.columns([1.18, 1])
            country_totals = countries.groupby(["ISO", "Country"], as_index=False)["Value"].sum()
            with map_col:
                st.subheader("Global Download & Sales Distribution")
                fig = px.choropleth(
                    country_totals, locations="ISO", color="Value", hover_name="Country",
                    labels={"Value": label}, color_continuous_scale=SCALE, projection="natural earth",
                )
                fig.update_geos(
                    showframe=False, showcoastlines=True, coastlinecolor="#4a414d",
                    showland=True, landcolor="#241832", bgcolor=CHART_SURFACE,
                )
                plot(fig, 395)
            with bar_col:
                st.subheader("Top Markets by " + ("Edition" if split == "Edition" else "Console Split"))
                bars = countries.groupby(["Country", split], as_index=False)["Value"].sum()
                ranking = country_totals.sort_values("Value")["Country"].tolist()
                plot(px.bar(
                    bars, x="Value", y="Country", color=split, orientation="h", barmode="stack",
                    category_orders={"Country": ranking, split: list(PRICES) if split == "Edition" else [PS5, XBOX]},
                    labels={"Value": label, "Country": ""}, color_discrete_sequence=COLORS,
                    color_discrete_map={PS5: "#0096ff", XBOX: "#2ec4b6"},
                ), 395)

        by_region = markets.groupby("Region", as_index=False)["Value"].sum()
        share_col, table_col = st.columns([1, 1.25])
        with share_col:
            st.subheader("Regional share")
            plot(px.pie(
                by_region, names="Region", values="Value", hole=0.68,
                color_discrete_sequence=COLORS,
            ), 300)
        with table_col:
            st.subheader("Market breakdown")
            table = markets.pivot_table(
                index=["Region", "Country"], columns="Edition", values="Value",
                aggfunc="sum", observed=True,
            ).reset_index()
            visible_editions = [tier for tier in PRICES if tier in table]
            table["Total"] = table[visible_editions].sum(axis=1)
            st.dataframe(
                table[["Country", "Region", *visible_editions, "Total"]]
                .sort_values("Total", ascending=False),
                hide_index=True, height=300,
                column_config={col: st.column_config.NumberColumn(format="%.2f")
                               for col in [*visible_editions, "Total"]},
            )
            st.caption(label)

    st.caption(
        "Regional and edition values are modeled. Each phase uses the dashboard’s existing geographic weights "
        "by console. The edition scenario assumes a $97 average order at US list prices, implying an 85% "
        "Ultimate unit share across all windows. Revenue splits allocate the published phase total by price-weighted "
        "share. The opening-weekend revenue model uses $4B as a floor."
    )
    st.caption(
        f"Sales sources · [Take-Two]({TAKE_TWO}) · [Sensor Tower]({SENSOR_TOWER}) · "
        f"[Alinea opening weekend]({WEEKEND}) · [Alinea week one]({WEEK_ONE})"
    )

    st.divider()
    momentum_col, traffic_col = st.columns(2)
    with momentum_col:
        st.subheader("Pre-order momentum")
        momentum = pd.DataFrame({
            "Date": pd.to_datetime(["2026-10-13", "2026-11-03", "2026-11-10", "2026-11-13", "2026-11-16"]),
            "Units (M)": [6.08, 7.71, 9.69, 12.13, 14.94],
        })
        fig = px.line(momentum, x="Date", y="Units (M)", markers=True, color_discrete_sequence=COLORS)
        fig.add_annotation(x=pd.Timestamp("2026-11-10"), y=9.69, text="Pre-load opens", ax=-35, ay=-42)
        fig.add_scatter(
            x=[pd.Timestamp("2026-11-19")], y=[32.5], mode="markers",
            name="Take-Two pre-release total", marker=dict(color=COLORS[1], size=12, symbol="diamond"),
            hovertemplate="%{y:.1f}M pre-release units<extra></extra>",
        )
        fig.data[0].update(name="Sensor Tower digital estimate", showlegend=True)
        plot(fig)
        st.caption(f"[Sensor Tower digital estimates]({SENSOR_TOWER}) · [Take-Two pre-release total]({TAKE_TWO})")
    with traffic_col:
        st.subheader("UK broadband traffic during pre-load")
        traffic = pd.DataFrame({
            "Window": ["Average Tuesday", "Nov 10 pre-load"],
            "Downstream (PB)": [284.46, 377.98],
        })
        fig = px.bar(
            traffic, x="Window", y="Downstream (PB)", text_auto=".1f",
            color="Window", color_discrete_sequence=[COLORS[1], COLORS[0]],
        )
        fig.update_layout(showlegend=False)
        plot(fig)
        st.caption(
            "Openreach reported 32.9% more downstream traffic. Virgin Media O2 also reported record traffic. "
            "Pre-load storage requirements reached 212 GB on some devices. "
            "[Openreach figures reported by ISPreview](https://www.ispreview.co.uk/index.php/2026/11/"
            "openreach-details-uk-broadband-traffic-impact-from-gta-6-pre-loading.html)"
        )

with tab2:
    watch_col, rival_col = st.columns(2)
    with watch_col:
        st.subheader("Watch time by platform")
        plot(px.pie(
            streaming_platforms, names="Platform", values="Hours_Watched_M", hole=0.68,
            color_discrete_sequence=COLORS,
        ))
        st.caption("Platform split from the dashboard’s existing dataset.")
    with rival_col:
        st.subheader("Rival games’ daily active users")
        rivals = pd.DataFrame({
            "Game": ["Call of Duty HQ", "Fortnite", "EA FC 27"],
            "Before launch": [7.5, 17.8, 5.9],
            "At launch": [4.4, 12.8, 4.3],
            "Change": ["−42%", "−28%", "−27%"],
        }).melt(id_vars=["Game", "Change"], var_name="Window", value_name="Daily players (M)")
        plot(px.bar(
            rivals, x="Game", y="Daily players (M)", color="Window", barmode="group",
            text="Daily players (M)", hover_data=["Change"], color_discrete_sequence=[COLORS[1], COLORS[0]],
        ))
        st.caption(f"Estimated change at launch: Call of Duty HQ −42%, Fortnite −28%, EA FC 27 −27%. [Alinea]({WEEKEND})")

    st.subheader("Creator watch time vs. peak audience")
    creators = pd.DataFrame([
        ("Windah Basudara", 3.592470, 170329, 108317),
        ("IShowSpeed", 2.694169, 416690, 128295),
        ("MixiGaming", 1.937039, 84818, 35872),
        ("TheBurntPeanut", 1.628195, 107933, 80076),
        ("LOUD Coringa", 1.361111, 175011, 83761),
    ], columns=["Creator", "Hours watched (M)", "Peak concurrent viewers", "Average viewers"])
    plot(px.scatter(
        creators, x="Hours watched (M)", y="Peak concurrent viewers", size="Average viewers",
        size_max=43, color="Creator", hover_name="Creator", color_discrete_sequence=COLORS,
    ), 395)
    st.caption(
        "Bubble area represents average viewers. This YouTube Gaming snapshot uses one platform and reporting "
        "window for all three measures. "
        "[Streams Charts, seven-day snapshot accessed Nov 27](https://streamscharts.com/channels?game=grand-theft-auto-vi&platform=youtube-gaming)"
    )
    st.subheader("Watch time at launch milestones")
    plot(px.line(
        milestones, x="Event", y="Stream_Hours_Watched_M", markers=True,
        labels={"Event": "", "Stream_Hours_Watched_M": "Hours watched (M)"},
        color_discrete_sequence=COLORS,
    ))
    st.caption("Milestone totals from the dashboard’s existing dataset cover different reporting windows.")

with tab3:
    st.subheader("Estimated audience by age")
    age = age_groups.rename(columns={
        "Age_Bracket": "Age group", "Est_Console_Players_Pct": "Console players",
        "YouTube_Viewers_Pct": "YouTube viewers",
    }).melt(id_vars="Age group", var_name="Audience", value_name="Share (%)")
    plot(px.bar(
        age, x="Age group", y="Share (%)", color="Audience", barmode="group",
        color_discrete_sequence=COLORS, text_auto=".1f",
    ), 390)
    st.caption("Illustrative audience estimates from the dashboard’s existing dataset.")


def youtube_results(key, query, order, region, duration):
    base_url = "https://www.googleapis.com/youtube/v3/"
    search = requests.get(base_url + "search", params={
        "part": "snippet", "q": query, "type": "video", "order": order,
        "regionCode": region, "videoDuration": duration, "maxResults": 10, "key": key,
    }, timeout=10)
    search.raise_for_status()
    ids = [item["id"]["videoId"] for item in search.json().get("items", [])]
    if not ids:
        return pd.DataFrame()
    details = requests.get(base_url + "videos", params={
        "part": "snippet,statistics", "id": ",".join(ids), "key": key,
    }, timeout=10)
    details.raise_for_status()
    videos = {item["id"]: item for item in details.json().get("items", [])}
    rows = []
    for video_id in ids:
        if video_id not in videos:
            continue
        snippet = videos[video_id]["snippet"]
        statistics = videos[video_id].get("statistics", {})
        rows.append({
            "Thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
            "Title": snippet["title"],
            "Channel": snippet["channelTitle"],
            "Published": snippet.get("publishedAt", "")[:10],
            "Views": int(statistics["viewCount"]) if "viewCount" in statistics else None,
            "Likes": int(statistics["likeCount"]) if "likeCount" in statistics else None,
            "Watch": f"https://www.youtube.com/watch?v={video_id}",
        })
    return pd.DataFrame(rows)


with tab4:
    st.subheader("Search YouTube")
    try:
        configured_key = st.secrets.get("YOUTUBE_API_KEY", "")
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        configured_key = ""

    durations = {"Any": "any", "Short (<4 min)": "short", "Long (>20 min)": "long"}
    orders = {"Views": "viewCount", "Newest": "date", "Relevance": "relevance"}
    entered_key = ""
    with st.form("youtube_search"):
        query = st.text_input("Search query", "GTA 6 gameplay")
        sort_col, region_col, duration_col = st.columns(3)
        order = sort_col.selectbox("Sort by", list(orders))
        region = region_col.selectbox("Region", ["US", "GB", "BR", "DE", "JP"])
        duration = duration_col.selectbox("Duration", list(durations))
        if not configured_key:
            entered_key = st.text_input("YouTube Data API v3 key", type="password")
        run_search = st.form_submit_button("Search videos", type="primary")

    if run_search:
        st.session_state.pop("youtube_search_result", None)
        key = configured_key or entered_key.strip()
        if not key or not query.strip():
            st.warning("Enter a search query and a YouTube Data API key.")
        else:
            with st.spinner("Searching YouTube…"):
                try:
                    results = youtube_results(key, query.strip(), orders[order], region, durations[duration])
                    st.session_state["youtube_search_result"] = (query.strip(), order, region, duration, results)
                except requests.HTTPError as exc:
                    st.error(
                        f"YouTube returned HTTP {exc.response.status_code}. Check the key, API access and quota."
                    )
                except (requests.RequestException, ValueError, KeyError):
                    st.error("YouTube results could not be loaded. Try again.")
    saved_search = st.session_state.get("youtube_search_result")
    if saved_search is not None:
        saved_query, saved_order, saved_region, saved_duration, results = saved_search
        st.caption(f"{saved_query} · {saved_order} · {saved_region} · {saved_duration}")
        if results.empty:
            st.info("No videos matched this search.")
        else:
            st.dataframe(
                results, hide_index=True,
                column_config={
                    "Thumbnail": st.column_config.ImageColumn("Preview"),
                    "Watch": st.column_config.LinkColumn("Video", display_text="Watch"),
                },
            )
            chart_data = results.dropna(subset=["Views"]).head(8)
            if not chart_data.empty:
                chart_data = chart_data.assign(Result=range(1, len(chart_data) + 1))
                fig = px.bar(
                    chart_data, x="Views", y="Result", orientation="h",
                    hover_data=["Title", "Channel", "Likes"], color_discrete_sequence=COLORS,
                    labels={"Result": "Search rank"},
                )
                fig.update_yaxes(autorange="reversed", dtick=1)
                plot(fig)


def read_reviews(file_bytes):
    stream = BytesIO(file_bytes)
    if not file_bytes.startswith(b"PK"):
        return pd.read_csv(stream, sep=None, engine="python")

    with ZipFile(stream) as archive:
        entries = [
            entry for entry in archive.infolist()
            if entry.filename.lower().endswith(".csv") and not entry.filename.startswith("__MACOSX/")
        ]
        if not entries or sum(entry.file_size for entry in entries) > 40 * 1024 * 1024:
            raise ValueError("Upload one or more CSV files totaling at most 40 MB.")
        frames = []
        for entry in entries:
            with archive.open(entry) as file:
                frame = pd.read_csv(file)
                frame["Source file"] = entry.filename
                frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def prepare_reviews(frame, platform_column, score_column, review_column):
    platforms = frame[platform_column].astype("string").str.lower()
    scores = pd.to_numeric(frame[score_column], errors="coerce")
    reviews = pd.DataFrame({
        "Console": platforms.map(lambda name: (
            PS5 if re.search(r"ps\s*5|playstation\s*5", str(name)) else
            XBOX if "xbox" in str(name) or "xsx" in str(name) else None
        )),
        "Score": scores,
        "Review": frame[review_column].fillna("").astype(str),
    })
    return reviews[reviews["Console"].notna() & reviews["Score"].between(0, 10)]


def review_keywords(text):
    stopwords = set(
        "about after again also because been before being both could even from game games good great have here "
        "into it's just like more much only other over really some than that their them then there these they "
        "this those through very want were what when where which while will with would your gta rockstar review".split()
    )
    counts = Counter()
    for review in text:
        counts.update({word for word in re.findall(r"[^\W\d_]{3,}", review.lower()) if word not in stopwords})
    return pd.DataFrame(counts.most_common(15), columns=["Keyword", "Reviews mentioning keyword"])


with tab5:
    st.subheader("Franchise launch benchmark")
    benchmark = pd.DataFrame([
        ("Day 1 retail sales", "GTA V (2013)", 0.8, 0.0, "$800M+"),
        ("Day 1 retail sales", "GTA VI (2026)", 3.79, 0.0, "$3.79B"),
        ("Day 3 retail sales", "GTA V (2013)", 1.0, 0.0, "$1B+"),
        ("Day 4 retail sales", "GTA VI (2026)", 4.0, 0.0, "$4B+"),
        ("Estimated budget", "GTA V (2013)", 0.265, 0.0, "~$265M"),
        ("Estimated budget", "GTA VI (2026)", 1.0, 0.5, "$1B–$1.5B"),
    ], columns=["Metric", "Title", "USD (B)", "Range above", "Reported value"])
    benchmark["Range below"] = 0
    fig = px.bar(
        benchmark, x="Metric", y="USD (B)", color="Title", barmode="group",
        text="Reported value", error_y="Range above", error_y_minus="Range below",
        color_discrete_sequence=[COLORS[1], COLORS[0]],
        hover_data={"Range above": False, "Range below": False},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(range=[0, 4.65])
    plot(fig, 410)
    st.caption(
        "Retail sales and estimated budgets have different accounting bases. "
        f"[Take-Two GTA V](https://ir.take2games.com/static-files/89147540-5f6a-4c86-bdd6-caeae6ea799a) · "
        f"[Take-Two GTA VI]({TAKE_TWO}) · [Alinea four-day estimate]({WEEKEND})"
    )

    st.divider()
    st.subheader("Player sentiment")
    st.caption(f"Import launch-period Metacritic user reviews from [GTA VI User Reviews on Kaggle]({KAGGLE}).")
    upload = st.file_uploader("Reviews CSV or Kaggle ZIP", type=["csv", "zip"])
    if upload is not None:
        try:
            if upload.size > 40 * 1024 * 1024:
                raise ValueError("Upload a file up to 40 MB.")
            raw_reviews = read_reviews(upload.getvalue())
        except (ValueError, BadZipFile, RuntimeError) as exc:
            st.error(f"Could not import the review file. {exc}")
        else:
            columns = raw_reviews.columns.tolist()
            normalized = {re.sub(r"[^a-z0-9]", "", col.lower()): col for col in columns}
            mapping = st.columns(3)
            chosen = []
            for col, name, aliases in zip(mapping, ["Platform", "User score (0–10)", "Review text"], [
                ["platform", "console", "system", "platformname", "sourcefile"],
                ["userscore", "score", "rating", "reviewscore", "userrating"],
                ["reviewtext", "review", "text", "comment", "reviewbody", "content", "body", "description"],
            ]):
                default = next((normalized[alias] for alias in aliases if alias in normalized), None)
                chosen.append(col.selectbox(name, columns, index=columns.index(default) if default else None))
            if all(chosen) and len(set(chosen)) == 3:
                reviews = prepare_reviews(raw_reviews, *chosen)
                if reviews.empty:
                    st.warning("No PS5 or Xbox reviews with a score between 0 and 10 were found.")
                else:
                    consoles = st.multiselect(
                        "Review platforms", [PS5, XBOX], default=[PS5, XBOX],
                    )
                    reviews = reviews[reviews["Console"].isin(consoles)]
                    if reviews.empty:
                        st.info("Select a platform with reviews in this file.")
                    else:
                        score_col, keyword_col = st.columns(2)
                        with score_col:
                            st.markdown("**User score distribution**")
                            fig = px.histogram(
                                reviews, x="Score", color="Console", barmode="overlay",
                                histnorm="percent", opacity=0.65, color_discrete_sequence=COLORS,
                            )
                            fig.update_traces(xbins=dict(start=-0.5, end=10.5, size=1))
                            fig.update_xaxes(range=[-0.5, 10.5], dtick=1)
                            fig.update_yaxes(title="Share of platform reviews (%)")
                            plot(fig, 370)
                            counts = reviews["Console"].value_counts()
                            st.caption(" · ".join(f"{console}: {count:,} reviews" for console, count in counts.items()))
                        with keyword_col:
                            st.markdown("**Most mentioned review keywords**")
                            keywords = review_keywords(reviews["Review"])
                            if keywords.empty:
                                st.info("The selected reviews contain no usable keywords.")
                            else:
                                plot(px.bar(
                                    keywords.iloc[::-1], x="Reviews mentioning keyword", y="Keyword",
                                    orientation="h", color_discrete_sequence=COLORS,
                                ), 370)
            else:
                st.info("Choose distinct columns for the platform, score and review text.")
