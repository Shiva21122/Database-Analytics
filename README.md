# Database-Analytics

#Airport Authority Data Analysis 

Project Overview:-
This project presents an analysis of U.S. domestic flight operations from 2014 to 2018, focusing on flight volumes, delays, ground processing times, and passenger satisfaction. The objective is to provide actionable insights to airport management using data visualization. An interactive dashboard was developed using Power BI to make the data exploration intuitive and informative.

Dataset:-
The dataset used for this project is Kaggle’s Airline Delay and Cancellation Data (2009–2018). It contains millions of flight records, capturing detailed information about flight timings, delays, cancellations, and causes. For our analysis, we focused on data from 2014 to 2018 to observe patterns and trends over time.

Objectives:-
The key goals of this analysis were to:
1. Examine the total number of flights and their year-over-year growth,
2. Identify seasonal and cause-based delay trends,
3. Measure ground processing time efficiency,
4. Estimate passenger satisfaction using a calculated proxy score (since direct feedback was not available),
5. And present all insights in a clean and user-friendly Power BI dashboard.

Methodology:-
The data was first cleaned and transformed in SQL Server. All columns were assigned the correct data types, missing values were handled, and calculated fields were added—such as ground processing time, which was derived from Taxi-In, Taxi-Out, and Delay columns. A proxy satisfaction score (1 to 5 scale) was created based on operational delays, cancellations, and causes. Finally, we developed an interactive Power BI dashboard with filters, cards, line charts, and drill-down options.

Key Insights:-
Our analysis revealed a sharp increase in total flights in 2018 compared to previous years, likely due to economic growth and expansion of airline networks. Delay patterns showed consistent peaks during summer and December holiday periods. The average ground processing time across all flights was 59.1 minutes, which aligns well with industry standards. Airline-related cancellations and delays were found to have the most negative impact on passenger satisfaction, especially when delays exceeded 30 minutes.

Challenges:-
We faced several challenges during the project. The dataset lacked direct customer feedback, so we created a proxy satisfaction model using operational data. Many airport codes were missing or inconsistent, requiring manual correction. Time formats were also not standardized, and some flights lacked delay reason data. Working with a multi-year, high-volume dataset added to the complexity, especially during data merging and transformation stages.

Outcome:-
Despite these challenges, the final dashboard offers a comprehensive and user-friendly view of the key performance indicators for airport operations. It empowers stakeholders to explore trends, detect performance gaps, and optimize decisions during peak travel seasons. This project demonstrates how historical operational data can be used to derive meaningful insights, even in the absence of direct customer feedback.

Project Details:-
Course: CST2102 – Database Analytics
Institution: Algonquin College
Instructor: Yasser Jafer
Team Members: Prajna Ganji, Shiva Shiva, Neetika Upadhyay, Maruta Zalane
Date: March 7, 2025
Tools: SQL Server, Power BI
Data Source: Kaggle – Airline Delay and Cancellation Data
