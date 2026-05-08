# 📊 PhonePe SQL Data Analysis & Visualization

## 📌 Project Overview

This project focuses on comprehensive Exploratory Data Analysis (EDA) of the PhonePe Pulse dataset using SQL (SQLite) and Python. The project analyzes large-scale digital payment data to uncover transaction trends, user behavior patterns, regional performance, and business insights across India.

The entire workflow is designed using a SQL-driven analytical approach, replacing traditional CSV-based analysis with a structured and scalable database system.

---

# 🎯 Problem Statement

With the rapid growth of digital payment platforms in India, analyzing transaction data has become essential for understanding customer behavior, regional adoption trends, payment patterns, and user engagement.

This project aims to perform data-driven analysis on PhonePe Pulse data to generate meaningful business insights that can support decision-making, strategic planning, and market analysis.

---

# 🚀 Project Objectives

* Analyze transaction volume and transaction value across years and quarters
* Study category-wise payment behavior
* Identify top-performing states and regions
* Examine user growth and app engagement trends
* Perform SQL-based aggregation and analytical querying
* Build visual insights using interactive and statistical charts
* Transition from CSV-based analysis to scalable SQL analytics

---

# 🛠️ Tech Stack

### Programming & Analysis

* Python
* Pandas
* NumPy

### Database

* SQLite
* SQL Queries

### Visualization

* Matplotlib
* Seaborn
* Plotly

### Dashboard

* Streamlit

### Development Environment

* Jupyter Notebook
* Google Colab
* VS Code

### Version Control

* Git & GitHub

---

# 🗂️ Dataset Description

The dataset is sourced from the official PhonePe Pulse GitHub repository and consists of structured JSON files categorized into multiple sections.

### 1️⃣ Aggregated Data

* Aggregated Transactions
* Aggregated Users
* Aggregated Insurance

### 2️⃣ Map Data

* State-level Data
* District-level Data

### 3️⃣ Top Data

* Top States
* Top Districts
* Top Pincodes

The dataset covers multiple years and quarters, enabling detailed trend analysis and comparative studies.

---

# ⚙️ Project Workflow

## 1️⃣ Data Extraction

* Extracted JSON data from the PhonePe Pulse repository
* Parsed nested JSON structures
* Converted data into structured Pandas DataFrames

---

## 2️⃣ SQL Integration

* Created SQLite database (`phonepe.db`)
* Stored all cleaned datasets into SQL tables
* Replaced CSV workflow with SQL-based querying

### SQL Tables Created

* agg_transaction
* agg_user
* agg_insurance
* map_transaction
* map_user
* map_insurance
* top_transaction
* top_user
* top_insurance

---

## 3️⃣ Data Wrangling

* Standardized column names
* Converted data types
* Cleaned and formatted state names
* Removed duplicate records
* Ensured consistency across all datasets

---

## 4️⃣ SQL-Based Data Analysis

Performed analytical operations using SQL queries such as:

* `SUM()`
* `AVG()`
* `GROUP BY`
* `ORDER BY`
* `LIMIT`
* Aggregation Queries
* Derived Metrics
* Ranking Analysis

---

## 5️⃣ Data Visualization

Built 15 analytical charts for detailed insights:

### 📈 Univariate Analysis

1. Year-wise Total Transaction Amount
2. Category-wise Transaction Amount
3. Quarter-wise Transaction Count
4. Top States by Transaction Amount
5. Top States by Transaction Count
6. Distribution of Transaction Amount

### 📊 Bivariate Analysis

7. Year vs Category-wise Transaction Amount
8. Year vs Transaction Count
9. States vs Average Transaction Value
10. Category vs Average Transaction Value
11. Top States by Registered Users
12. Registered Users vs App Opens
13. Top States by App Opens

### 🔥 Multivariate Analysis

14. Correlation Heatmap of Key Metrics
15. Pair Plot of Key Metrics

---

# 📊 Key Insights

* Digital transactions increased significantly between 2018 and 2024
* Peer-to-peer payments dominate overall transaction volume
* Maharashtra, Karnataka, and Telangana consistently rank among top-performing states
* Registered users strongly correlate with app engagement
* High transaction count does not always indicate high transaction value
* Transaction behavior varies considerably across categories and regions

---

# 💼 Business Use Cases

* Customer segmentation based on payment behavior
* Fraud detection through abnormal transaction patterns
* Regional marketing optimization
* Product and feature enhancement strategies
* User engagement analysis
* Insurance trend analysis
* Demand forecasting and business intelligence

---

# 🧠 SQL Usage Highlights

This project extensively uses SQL for analytical processing:

* Aggregation using `SUM()` and `AVG()`
* Multi-column grouping using `GROUP BY`
* Ranking using `ORDER BY` and `LIMIT`
* Derived metrics calculation
* Comparative analysis across years and states
* SQL-driven data exploration for visualization

---

# 📁 Project Structure

```text
PhonePe-SQL-Data-Analysis/
│
├── data/                          # Dataset files
├── outputs/                       # Generated charts & outputs
├── streamlit_dashboard/           # Streamlit dashboard files
│   ├── app.py
│   ├── requirements.txt
│   └── phonepe.db
│
├── PhonePe_EDA_Project.ipynb      # Main SQL analysis notebook
├── README.md                      # Project documentation
├── report.pdf                     # Project report
└── screenshots/                   # Dashboard screenshots
```

---

# ▶️ How to Run the Project

## 1️⃣ Clone Repository

```bash
git clone <repository-link>
```

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 3️⃣ Run Streamlit Dashboard

```bash
streamlit run app.py
```

---

# 📌 Project Outcomes

* Successfully built a complete SQL-based analytics pipeline
* Performed large-scale payment trend analysis
* Developed interactive visual dashboards
* Generated business insights from real-world digital payment data
* Demonstrated practical implementation of SQL in data analytics workflows

---

# 🌐 Streamlit Dashboard

The project also includes an interactive Streamlit dashboard for real-time data exploration and visualization.

Dashboard Features:

* Interactive filters
* Dynamic charts
* KPI cards
* State-wise analysis
* User analytics
* Transaction insights

---

# 👨‍💻 Author

### Harsh Kumar

Aspiring Data Analyst | SQL Enthusiast | Python Developer

---

# ⭐ Final Note

This project demonstrates the transformation of raw JSON payment data into structured SQL-based analytics and interactive visual insights. It reflects real-world industry practices involving database management, analytical querying, business intelligence, and dashboard development.

