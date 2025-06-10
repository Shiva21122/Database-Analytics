
# Airport Authority Data Analysis Dashboard

This project presents a comprehensive analysis of flight operations, delays, ground processing time, and inferred passenger satisfaction using U.S. airline data from 2014 to 2018. It is designed to help airport authorities gain insights into operational efficiency and passenger experience via a user-friendly Power BI dashboard.

---

## Project Overview

- **Goal**: Deliver actionable insights into flight volumes, delays, and operational performance over five years.
- **Dataset**: [Kaggle – Airline Delay and Cancellation Data (2009–2018)](https://www.kaggle.com/datasets/yuanyuwendymu/airline-delay-and-cancellation-data-2009-2018)
- **Use Case**: Designed to assist airport managers and decision-makers in identifying trends, improving processes, and enhancing customer satisfaction.

---

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| **SQL Server** | Data cleaning and transformation |
| **Power BI** | Dashboard development and visual storytelling |
| **Excel** | Preliminary data exploration and formatting |

---

# Dashboard Features

| Metric | Insight |
|--------|---------|
| **Total Flights** | Year-over-year trends and flight volumes |
| **Delays** | Delay causes, seasonal spikes, and monthly patterns |
| **Ground Processing Time** | Taxi-in, taxi-out, and departure delay durations |
| **Passenger Satisfaction Score** | Estimated via proxy model based on delay and cancellation factors |

---

## Methodology

1. **Data Understanding**: Reviewed all dataset columns and cleaned data types (converted VARCHAR to appropriate types).
2. **Data Cleaning**: Replaced blanks with NULLs, removed unneeded columns, standardized time formats.
3. **Transformation**: Calculated new metrics like ground processing time and proxy satisfaction scores.
4. **Dashboard Development**: Built clear, interactive visualizations using filters and drilldowns in Power BI.

---

## Key Insights

- **2018 saw a sharp rise in flight volume**, likely due to network expansions.
- **Delays peaked in June, July, August, and December**, aligning with holiday travel.
- **Average ground processing time was 59.1 minutes**, consistent with industry norms.
- **Flights delayed >30 minutes had the lowest satisfaction scores**.
- **Airline-caused delays/cancellations were the most damaging to satisfaction**.

---

## Challenges Faced

- Handling inconsistent or missing airport codes
- Estimating satisfaction without direct passenger feedback
- Calculating ground processing time with partial records
- Balancing data volume and dashboard performance

---

## Learning Outcomes

- Gained hands-on experience in **data cleaning and modeling**
- Developed custom KPIs using **proxy metrics and calculated fields**
- Built an end-to-end Power BI dashboard to visualize trends and drive decisions
- Improved skills in **collaborative data analysis and storytelling**

---

## References

- [Kaggle Dataset](https://www.kaggle.com/datasets/yuanyuwendymu/airline-delay-and-cancellation-data-2009-2018)
- [Forbes Article on 2018 Airline Trends](https://www.forbes.com/sites/danielreed/2018/04/04/airlines-subtle-domestic-growth-plans-for-2018-likely-mean-fares-wont-be-rising-this-year/)
- [ANS Performance Data](https://www.ansperformance.eu)

---

## Team Members

Project by students of **Algonquin College – CST2102 Database Analytics**  
**Prajna Ganji**, **Shiva**, **Neetika Upadhyay**, **Maruta Zalane**

---

## Files Included

- `Airport_Dashboard.pbix` – Interactive Power BI dashboard
- `Assignment1_Technical Report.pdf` – Technical report
- `Assignment1_Airport Data Analysis.pdf` – Slide deck

