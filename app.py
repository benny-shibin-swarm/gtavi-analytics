import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ---------------------------------------------------------
# 1. PAGE CONFIG & VICE CITY NEON THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="GTA VI Launch & Viewership Analytics",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Freely available public-domain / open-license GTA VI graphics on Wikimedia Commons
GTA_VI_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Grand_Theft_Auto_VI_logo_%28with_gradient%29.svg/640px-Grand_Theft_Auto_VI_logo_%28with_gradient%29.svg.png"
LEONIDA_FLAG_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/State_of_Leonida_flag.png/640px-State_of_Leonida_flag.png"

st.markdown(
    """
    <style>
    /* Main layout & dark Vice City gradient accents */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    /* Hero Banner */
    .vice-hero {
        background: linear-gradient(135deg, #140826 0%, #3b0d54 48%, #c92a76 85%, #ff7b54 100%);
        border: 1px solid rgba(255, 110, 199, 0.45);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(201, 42, 118, 0.22);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        flex-wrap: wrap;
    }
    .vice-hero-text h1 {
        color: #ffffff;
        font-size: 2.05rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.45);
    }
    .vice-hero-text p {
        color: #f3d9fa;
        font-size: 1.02rem;
        margin: 0;
        max-width: 720px;
        line-height: 1.5;
    }
    .vice-badge {
        display: inline-block;
        background: rgba(0, 212, 255, 0.18);
        border: 1px solid #00d4ff;
        color: #7ce8ff;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Glassmorphic Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(38, 16, 66, 0.65) 0%, rgba(20, 10, 38, 0.85) 100%);
        border: 1px solid rgba(255, 110, 199, 0.35);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00d4ff;
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] {
        color: #e0aaff !important;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800;
    }

    /* Styled Tabs */
    button[data-baseweb="tab"] {
        font-size: 0.98rem !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. PUBLIC DATASET (Launch Week: Nov 19–26, 2026)
# Sources: Alinea Analytics, Sony, Streams Charts
# ---------------------------------------------------------
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

    top_creators = pd.DataFrame([
        {"Creator": "TheBurntPeanut", "Primary_Platform": "Multi-Platform", "Hours_Watched_M": 3.80, "Peak_Viewers_K": 2180},
        {"Creator": "Alanzoka", "Primary_Platform": "Twitch", "Hours_Watched_M": 3.10, "Peak_Viewers_K": 410},
        {"Creator": "IShowSpeed", "Primary_Platform": "YouTube", "Hours_Watched_M": 2.95, "Peak_Viewers_K": 2040},
        {"Creator": "IlloJuan", "Primary_Platform": "Twitch", "Hours_Watched_M": 2.60, "Peak_Viewers_K": 520},
        {"Creator": "LOUD Coringa", "Primary_Platform": "Twitch", "Hours_Watched_M": 2.15, "Peak_Viewers_K": 1770},
    ])

    age_groups = pd.DataFrame([
        {"Age_Bracket": "Under 18 (Shared/Family)", "YouTube_Viewers_Pct": 16.0, "Est_Console_Players_Pct": 11.5},
        {"Age_Bracket": "18–24", "YouTube_Viewers_Pct": 37.5, "Est_Console_Players_Pct": 34.0},
        {"Age_Bracket": "25–34", "YouTube_Viewers_Pct": 31.0, "Est_Console_Players_Pct": 36.5},
        {"Age_Bracket": "35–44", "YouTube_Viewers_Pct": 11.5, "Est_Console_Players_Pct": 13.5},
        {"Age_Bracket": "45+", "YouTube_Viewers_Pct": 4.0, "Est_Console_Players_Pct": 4.5},
    ])

    return regional_df, streaming_platforms, milestones, top_creators, age_groups


regional_df, streaming_platforms, milestones, top_creators, age_groups = load_public_data()

# ---------------------------------------------------------
# 3. SIDEBAR WITH OFFICIAL LOGO & FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.image(GTA_VI_LOGO_URL, use_container_width=True)
    st.caption("📍 State of Leonida • Launch Intelligence (Nov 2026)")
    st.divider()

    selected_regions = st.multiselect(
        "🌍 Filter Sales by Region",
        options=regional_df["Region"].unique().tolist(),
        default=regional_df["Region"].unique().tolist(),
    )

    platform_filter = st.radio(
        "🎮 Console Platform View",
        options=["All Consoles (53.0M)", "PlayStation 5 (75.7%)", "Xbox Series X|S (24.3%)"],
        index=0,
    )

    st.divider()
    st.subheader("🔴 Live YouTube API")

    try:
        default_key = st.secrets.get("YOUTUBE_API_KEY", "")
    except Exception:
        default_key = ""

    yt_api_key = st.text_input(
        "YouTube Data API v3 Key",
        value=default_key,
        type="password",
        help="Loaded automatically from Streamlit Secrets if configured.",
    )
    yt_query = st.text_input("Live Search Query", value="GTA 6 gameplay")

    st.divider()
    st.image(LEONIDA_FLAG_URL, caption="State of Leonida (Wikimedia Commons)", use_container_width=True)

# Filter regional dataframe
filtered_reg = regional_df[regional_df["Region"].isin(selected_regions)].copy()
if platform_filter == "PlayStation 5 (75.7%)":
    filtered_reg["Active_Copies_M"] = filtered_reg["PS5_M"]
elif platform_filter == "Xbox Series X|S (24.3%)":
    filtered_reg["Active_Copies_M"] = filtered_reg["Xbox_M"]
else:
    filtered_reg["Active_Copies_M"] = filtered_reg["Copies_M"]

# ---------------------------------------------------------
# 4. HERO BANNER & TOP KPI METRICS
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="vice-hero">
        <div class="vice-hero-text">
            <div class="vice-badge">🌴 Welcome to Leonida • Week-1 Global Telemetry</div>
            <h1>Grand Theft Auto VI — Launch & Viewership Analytics</h1>
            <p>
                Interactive market intelligence tracking <strong>regional digital & physical downloads</strong>,
                <strong>PS5 vs. Xbox Series X|S adoption</strong>, <strong>estimated player age demographics</strong>,
                and <strong>live YouTube & livestreaming viewership</strong>.
            </p>
        </div>
        <div>
            <img src="{GTA_VI_LOGO_URL}" width="155" alt="Grand Theft Auto VI Logo" style="filter: drop-shadow(0 6px 18px rgba(0,0,0,0.5));" />
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("💿 Week-1 Units Sold", "53.0M", "+44.9M Opening Weekend")
k2.metric("💵 Gross Launch Revenue", "$4.70B", "$3.79B Day-1 Record")
k3.metric("📡 Livestream Hours Watched", "424.1M hrs", "7.91M Peak Concurrent")
k4.metric("▶️ YouTube Launch-Day Views", "3.50B", "55,000+ Live Channels")

st.write("")

# ---------------------------------------------------------
# 5. DASHBOARD TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Downloads & Regions",
    "📺 YouTube & Livestreams",
    "👥 Age Group Demographics",
    "⚡ Live YouTube Data Feed",
])

# --- TAB 1: REGIONAL DOWNLOADS & PLATFORM SPLIT ---
with tab1:
    col_map, col_bar = st.columns([1.35, 1])

    with col_map:
        st.subheader("Global Download & Sales Distribution (Millions)")
        map_df = filtered_reg[filtered_reg["ISO"] != "ROW"]
        fig_map = px.choropleth(
            map_df,
            locations="ISO",
            color="Active_Copies_M",
            hover_name="Country",
            hover_data={"Share_Pct": True, "PS5_M": True, "Xbox_M": True, "ISO": False},
            color_continuous_scale=["#2b0947", "#9d176c", "#ff2a85", "#ff9e5e"],
            labels={"Active_Copies_M": "Copies (M)"},
        )
        fig_map.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="rgba(255,255,255,0.2)",
                landcolor="rgba(30, 18, 52, 0.8)",
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8f9fa"),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_bar:
        st.subheader("Top Markets by Console Split")
        top_countries = filtered_reg[filtered_reg["ISO"] != "ROW"].sort_values("Copies_M", ascending=True)
        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(
            y=top_countries["Country"],
            x=top_countries["PS5_M"],
            name="PS5 (75.7%)",
            orientation="h",
            marker_color="#0096FF",
        ))
        fig_stack.add_trace(go.Bar(
            y=top_countries["Country"],
            x=top_countries["Xbox_M"],
            name="Xbox Series X|S (24.3%)",
            orientation="h",
            marker_color="#2EC4B6",
        ))
        fig_stack.update_layout(
            barmode="stack",
            xaxis_title="Copies Sold (Millions)",
            margin=dict(l=0, r=10, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8f9fa"),
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    st.divider()
    c_reg_pie, c_reg_table = st.columns([1, 1.4])
    with c_reg_pie:
        st.subheader("Share by Macro-Region")
        region_summary = filtered_reg.groupby("Region", as_index=False)["Active_Copies_M"].sum()
        fig_reg_pie = px.pie(
            region_summary,
            values="Active_Copies_M",
            names="Region",
            hole=0.5,
            color_discrete_sequence=["#ff2a85", "#00d4ff", "#ff9e5e", "#9b5de5", "#00f5d4"],
        )
        fig_reg_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_reg_pie.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8f9fa"),
            showlegend=False,
        )
        st.plotly_chart(fig_reg_pie, use_container_width=True)

    with c_reg_table:
        st.subheader("Regional Sales & Platform Breakdown")
        st.dataframe(filtered_reg, use_container_width=True, hide_index=True)

# --- TAB 2: YOUTUBE & LIVESTREAMS ---
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Week-1 Livestream Hours Watched by Platform")
        fig_donut = px.pie(
            streaming_platforms,
            values="Hours_Watched_M",
            names="Platform",
            hole=0.55,
            color="Platform",
            color_discrete_map={
                "Twitch": "#9146FF",
                "YouTube Live": "#FF0033",
                "Kick": "#53FC18",
            },
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        fig_donut.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8f9fa"),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Top Week-1 Creators (Hours Watched in Millions)")
        fig_creators = px.bar(
            top_creators.sort_values("Hours_Watched_M", ascending=True),
            x="Hours_Watched_M",
            y="Creator",
            color="Primary_Platform",
            orientation="h",
            text="Hours_Watched_M",
            color_discrete_map={
                "Multi-Platform": "#00d4ff",
                "Twitch": "#9146FF",
                "YouTube": "#FF0033",
            },
            labels={"Hours_Watched_M": "Hours Watched (M)"},
        )
        fig_creators.update_traces(texttemplate="%{text:.2f}M", textposition="outside")
        fig_creators.update_layout(
            margin=dict(l=0, r=35, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8f9fa"),
        )
        st.plotly_chart(fig_creators, use_container_width=True)

    st.subheader("Hype-to-Launch Momentum: Stream Hours Watched Across Milestones")
    fig_line = px.area(
        milestones,
        x="Event",
        y="Stream_Hours_Watched_M",
        markers=True,
        text="Stream_Hours_Watched_M",
        labels={"Stream_Hours_Watched_M": "Stream Hours Watched (Millions)"},
    )
    fig_line.update_traces(
        line_color="#ff2a85",
        fillcolor="rgba(255, 42, 133, 0.22)",
        textposition="top center",
    )
    fig_line.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8f9fa"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- TAB 3: AGE GROUP DEMOGRAPHICS ---
with tab3:
    st.subheader("Estimated Age Distribution: Players vs. Video/Stream Viewers")
    st.info(
        "**Data Methodology Note:** Sony PSN and Xbox do not publish raw buyer age logs due to privacy laws "
        "and shared family accounts. This model estimates age brackets by combining **YouTube Gaming audience demographics** "
        "with **console survey proxies** for ESRB Mature (18+) launches."
    )

    col_age_chart, col_age_insights = st.columns([1.6, 1])

    with col_age_chart:
        age_melted = age_groups.melt(
            id_vars="Age_Bracket",
            value_vars=["Est_Console_Players_Pct", "YouTube_Viewers_Pct"],
            var_name="Metric",
            value_name="Percentage",
        )
        age_melted["Metric"] = age_melted["Metric"].replace({
            "Est_Console_Players_Pct": "Est. Console Players (%)",
            "YouTube_Viewers_Pct": "YouTube / Stream Viewers (%)",
        })

        fig_age = px.bar(
            age_melted,
            x="Age_Bracket",
            y="Percentage",
            color="Metric",
            barmode="group",
            text="Percentage",
            color_discrete_sequence=["#ff2a85", "#00d4ff"],
        )
        fig_age.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_age.update_layout(
            yaxis_title="Share of Audience (%)",
            xaxis_title="Age Group",
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8f9fa"),
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col_age_insights:
        st.markdown("#### 🔍 Key Demographic Takeaways")
        st.markdown(
            """
            * **Core Buyer Bracket (25–34):** Accounts for **36.5%** of estimated console buyers—players who grew up with *GTA V* (2013) and now have high console ownership and purchasing power.
            * **Core Viewer Bracket (18–24):** Leads video and livestream consumption at **37.5%**, driving viral clips on YouTube, Twitch, and Kick.
            * **Under-18 Shadow Audience:** Despite the **18+ / M rating**, roughly **16%** of YouTube viewership and **11.5%** of playtime comes from younger audiences watching streams or playing via shared family consoles.
            """
        )

# --- TAB 4: LIVE YOUTUBE DATA API ---
with tab4:
    st.subheader("Live YouTube Video & Viewership Tracker")
    if not yt_api_key:
        st.warning(
            "Enter a **YouTube Data API v3 Key** in the left sidebar to pull real-time video statistics, "
            "thumbnails, views, and engagement metrics directly from YouTube."
        )
    else:
        try:
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                "part": "snippet",
                "q": yt_query,
                "type": "video",
                "order": "viewCount",
                "maxResults": 10,
                "key": yt_api_key,
            }
            search_res = requests.get(search_url, params=search_params, timeout=10).json()

            if "error" in search_res:
                st.error(f"YouTube API Error: {search_res['error']['message']}")
            else:
                video_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]
                stats_url = "https://www.googleapis.com/youtube/v3/videos"
                stats_params = {
                    "part": "snippet,statistics",
                    "id": ",".join(video_ids),
                    "key": yt_api_key,
                }
                stats_res = requests.get(stats_url, params=stats_params, timeout=10).json()

                rows = []
                for v in stats_res.get("items", []):
                    stats = v.get("statistics", {})
                    snippet = v.get("snippet", {})
                    vid_id = v.get("id")
                    thumb = snippet.get("thumbnails", {}).get("medium", {}).get("url", "")
                    rows.append({
                        "Thumbnail": thumb,
                        "Title": snippet.get("title"),
                        "Channel": snippet.get("channelTitle"),
                        "Published": snippet.get("publishedAt", "")[:10],
                        "Views": int(stats.get("viewCount", 0)),
                        "Likes": int(stats.get("likeCount", 0)),
                        "Watch": f"https://www.youtube.com/watch?v={vid_id}",
                    })

                live_df = pd.DataFrame(rows).sort_values("Views", ascending=False)
                st.success(f"Fetched {len(live_df)} live videos for query: **{yt_query}**")

                st.dataframe(
                    live_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Thumbnail": st.column_config.ImageColumn("Preview", width="small"),
                        "Views": st.column_config.NumberColumn("Views", format="%d"),
                        "Likes": st.column_config.NumberColumn("Likes", format="%d"),
                        "Watch": st.column_config.LinkColumn("YouTube Link", display_text="Watch ▶"),
                    },
                )

                fig_live = px.bar(
                    live_df.head(8).sort_values("Views", ascending=True),
                    x="Views",
                    y="Channel",
                    orientation="h",
                    hover_data=["Title", "Likes"],
                    color="Views",
                    color_continuous_scale=["#9d176c", "#ff2a85", "#00d4ff"],
                    title=f"Top Channels by Live View Count ('{yt_query}')",
                )
                fig_live.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#f8f9fa"),
                )
                st.plotly_chart(fig_live, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to fetch YouTube data: {e}")