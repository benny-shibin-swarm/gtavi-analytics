# GTA VI Launch & Viewership Analytics

An interactive Streamlit dashboard for exploring *Grand Theft Auto VI* sales, livestream audiences, and player reviews during its November 2026 launch. The app combines launch snapshots with an optional live YouTube search.

[Open the dashboard on Streamlit](https://gtavi-analytics.streamlit.app/)

## Explore the dashboard

| Tab | What you can explore |
| --- | --- |
| Downloads & Regions | Switch between pre-orders, day one, opening weekend, and week one. Filter markets by region, console, and edition. View units, retail sales, or modeled attach-rate contributions where available. This tab also tracks pre-order momentum and UK broadband traffic during pre-load. |
| YouTube & Livestreams | Compare watch time by platform, rival games’ daily player counts around launch, and creator watch time, peak concurrency, and average audience size. |
| Age Group Demographics | Compare illustrative age distributions for console players and YouTube viewers. |
| Live YouTube Data Feed | Search videos by views, date, or relevance, then filter by viewing region and duration. An API key is required for search. |
| Franchise & Sentiment | Compare GTA V and GTA VI launch sales and estimated budgets. Upload review data to compare PS5 and Xbox scores and view frequently mentioned keywords. |

## Run locally

Use Python 3.12 or newer. From the repository root, create a virtual environment, install the dependencies, and start Streamlit.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, typically `http://localhost:8501`. On Windows PowerShell, activate the virtual environment with `.venv\Scripts\Activate.ps1` before installing dependencies.

### Enable live YouTube search

The dashboard starts without a key. To use search, enable **YouTube Data API v3** in your Google Cloud project and enter its API key in the **Live YouTube Data Feed** tab. To configure a key for local development, add it to `.streamlit/secrets.toml`.

```toml
YOUTUBE_API_KEY = "your-key-here"
```

Git ignores this file. On Streamlit Community Cloud, use **App settings → Secrets** with the same TOML entry. A configured key lets viewers submit searches against its project quota, so use a dedicated key restricted to YouTube Data API v3 or leave the shared key unset for a public deployment. [Streamlit secrets documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management) · [YouTube Data API documentation](https://developers.google.com/youtube/v3)

### Import player reviews

Download the [GTA VI User Reviews dataset](https://www.kaggle.com/datasets/ektarr/gta-vi-user-reviews) and upload its CSV or ZIP in **Franchise & Sentiment**. Choose the platform, score, and review-text columns if the app needs help identifying them. Scores must be on a 0–10 scale. Keyword counts show how many reviews mention each word.

## Deploy on Streamlit Community Cloud

In Streamlit Community Cloud, select **Create app**, connect the GitHub repository, choose the branch containing the dashboard, and set the main file path to `app.py`. Community Cloud installs packages from `requirements.txt`. For the existing deployment, changes merged into `main` are the deployment source. [Deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

## Data sources and interpretation

- **Sales windows.** The pre-release and day-one headline figures come from Take-Two. The opening-weekend and week-one figures are Alinea estimates. The pre-order trajectory tracks Sensor Tower’s digital estimates separately from Take-Two’s wider pre-release total. [Take-Two](https://ir.take2games.com/node/32701) · [Sensor Tower](https://sensortower.com/grand-theft-auto-VI/sales-tracker) · [Alinea opening weekend](https://alineaanalytics.substack.com/p/gta-6-sells-449m-copies-makes-40b) · [Alinea week one](https://alineaanalytics.substack.com/p/grand-theft-auto-6-a-week-in)
- **Market model.** Regional views apply the dashboard’s geographic weights by console. The edition split assumes a $97 average order at US list prices. The attach-rate map shows each market’s contribution to the estimated global rate in percentage points. Country-level console installed bases are unavailable.
- **Streaming and audience.** The creator chart uses a seven-day YouTube Gaming snapshot. Platform splits and milestone totals come from the dashboard’s existing dataset, and age-group shares are illustrative. [Streams Charts launch-week report](https://streamscharts.com/news/gta6-livestreaming-week-after-launch)
- **Franchise benchmark.** Retail sales and estimated budgets use different accounting bases. GTA V’s $1B+ milestone covers three days, while the GTA VI $4B+ estimate covers four. [Take-Two GTA V results](https://ir.take2games.com/static-files/89147540-5f6a-4c86-bdd6-caeae6ea799a) · [Alinea GTA VI estimate](https://alineaanalytics.substack.com/p/gta-6-sells-449m-copies-makes-40b)

## Project layout

| Path | Purpose |
| --- | --- |
| [`app.py`](app.py) | Dashboard, charts, sales modeling, YouTube search, and review import |
| [`requirements.txt`](requirements.txt) | Python dependencies |
| [`.streamlit/config.toml`](.streamlit/config.toml) | Streamlit theme |
| [`assets/dashboard.css`](assets/dashboard.css) | Dashboard layout and styling |
