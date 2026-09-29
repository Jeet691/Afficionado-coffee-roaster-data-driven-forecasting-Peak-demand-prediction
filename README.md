# Afficionado Coffee Roasters — Streamlit Portfolio

Interactive portfolio app for the coffee-roaster analytics project.

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create/activate a virtual environment (recommended).
4. Install dependencies:
   `pip install -r requirements.txt`
5. Start the app:
   `streamlit run app.py`

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload the contents of this project folder.
2. In Streamlit Community Cloud, choose **Create app**.
3. Select your repository, branch, and `app.py` as the main file.
4. Deploy. Keep `requirements.txt`, `data/`, and `assets/` in the repository.

## Pages
Home, Executive Overview, Peak Demand & Operations, Product & Store Analysis,
Hourly Demand Planning, and EDA Report & Resources.

## Data interpretation
The app presents transaction-level results and intraday/hourly demand patterns.
The source data does not contain a genuine calendar date; therefore the app does
not claim validated daily/weekly forecasting or seasonality. The PBIX is provided
as a downloadable artifact; charts in the web app are native Plotly visuals.
