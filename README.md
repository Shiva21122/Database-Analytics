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

- Dashboard: `Dashboards/Airline_Data_2014-2018_Final.pbix`
- Written analysis: `Reports/Technical_Report.pdf` and presentation deck in `Reports/`

## Project Structure

```
us-airline-delays-analysis/
├── Data/            # 2014-2018 BTS CSVs + airline/airport lookups (NOT in GitHub)
├── Dashboards/      # Power BI file (659 MB - NOT in GitHub)
└── Reports/         # Technical report + presentation (PDF/PPTX/DOCX)
```

## ⚠️ Large Files

The raw CSVs (660–850 MB each) and the .pbix (659 MB) exceed GitHub's 100 MB limit and are excluded via `.gitignore`. To reproduce, download On-Time Performance data (2014–2018) from [BTS TranStats](https://www.transtats.bts.gov/) — only the reports are versioned here.

**Tools:** Power BI (large-dataset modeling, Power Query, DAX), BTS open data
