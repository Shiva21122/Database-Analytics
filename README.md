# US Airline Flight Delays Analysis (2014–2018)

Power BI analysis of ~30 million US domestic flight records (3.5 GB across five annual files), identifying delay patterns by airline, airport, route, and season.

## 1. Business Question

Which airlines, airports, and time periods have the worst delay and cancellation performance in the US (2014–2018), and what should travelers and operators expect by route and season?

## 2. Research

- Source: US Bureau of Transportation Statistics (BTS) On-Time Performance data, 2014–2018, plus airline and airport reference tables
- Scale: five annual CSVs of 660–850 MB each (~3.5 GB total) modeled in Power BI

## 3. Data Types

Flight dates (time series), carrier/airport codes (categorical, joined to reference tables), delay minutes by cause (numeric), cancellation flags (boolean).

## 4. Data Cleaning

- Joined flight facts to `US_Airlines.xlsx` and `US_Airports.xlsx` dimension tables
- Handled cancelled/diverted flights and null delay values in Power Query
- Aggregations and DAX measures for on-time %, average delay by cause, and YoY trends

## 5. Results

- **Interactive Streamlit dashboard**: `app.py` — trends, airline rankings, an airport delay map, best-time-to-fly heatmaps, and delay-cause breakdowns, powered by pre-computed aggregates so it runs fast and deploys anywhere
- Power BI dashboard: `Dashboards/Airline_Data_2014-2018_Final.pbix`
- Written analysis: `Reports/Technical_Report.pdf` and presentation deck in `Reports/`

## Project Structure

```
us-airline-delays-analysis/
├── app.py                        # Streamlit dashboard (runs off aggregates/)
├── scripts/
│   └── build_aggregates.py      # One-time reduction of 30M rows → summary tables
├── aggregates/                  # Small summary CSVs (committed - powers the app)
├── Data/                        # 2014-2018 BTS CSVs + lookups (NOT in GitHub)
├── Dashboards/                  # Power BI file (659 MB - NOT in GitHub)
├── Reports/                     # Technical report + presentation (PDF/PPTX/DOCX)
└── requirements.txt
```

## How to Run the App

```bash
pip install -r requirements.txt
streamlit run app.py                      # uses committed aggregates/
# to rebuild aggregates from raw BTS data (requires Data/ CSVs):
python scripts/build_aggregates.py
```

## ⚠️ Large Files

The raw CSVs (660–850 MB each) and the .pbix (659 MB) exceed GitHub's 100 MB limit and are excluded via `.gitignore`. To reproduce, download On-Time Performance data (2014–2018) from [BTS TranStats](https://www.transtats.bts.gov/) — only the reports are versioned here.

**Tools:** Power BI (large-dataset modeling, Power Query, DAX), BTS open data
