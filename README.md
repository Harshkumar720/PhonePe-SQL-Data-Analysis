# 📊 PhonePe SQL Data Analysis & Visualization

## 📌 Project Overview

This project performs comprehensive **Exploratory Data Analysis (EDA)** on the PhonePe Pulse dataset using **SQL (SQLite)** and **Python**. The goal is to extract meaningful insights from digital payment data, understand user behavior, and analyze transaction trends across India.

---

## 🎯 Problem Statement

With the rapid adoption of digital payments, it is essential to analyze transaction patterns, user engagement, and insurance data to support better decision-making, fraud detection, and targeted business strategies.

---

## 🚀 Objectives

* Analyze transaction volume and value across years, states, and categories
* Study user growth and engagement trends
* Identify top-performing regions and categories
* Derive business insights for strategic improvements
* Replace traditional CSV-based analysis with **SQL-driven analytics**

---

## 🛠️ Tech Stack

* **Python** (Pandas, NumPy)
* **Visualization**: Matplotlib, Seaborn
* **Database**: SQLite (SQL)
* **Environment**: Jupyter Notebook / Google Colab
* **Version Control**: GitHub

---

## 🗂️ Dataset Description

The dataset is sourced from the PhonePe Pulse GitHub repository and consists of structured JSON files categorized into:

* **Aggregated Data**

  * Transactions
  * Users
  * Insurance

* **Map Data**

  * State & district-level insights

* **Top Data**

  * Top states, districts, and pincodes

---

## ⚙️ Project Workflow

### 1️⃣ Data Extraction

* Extracted JSON data from PhonePe repository
* Converted structured data into Pandas DataFrames

### 2️⃣ SQL Integration

* Created SQLite database (`phonepe.db`)
* Stored all cleaned datasets into SQL tables
* Replaced CSV-based workflow with SQL queries

### 3️⃣ Data Wrangling

* Cleaned column names and formats
* Standardized state names
* Converted data types
* Removed duplicates
* Ensured consistency across datasets

### 4️⃣ Data Analysis using SQL

* Used SQL queries for aggregation and transformation
* Applied `GROUP BY`, `JOIN`, `ORDER BY`, and calculations

### 5️⃣ Visualization

* Built **15 analytical charts**:

  * **Univariate Analysis (1–6)**
  * **Bivariate Analysis (7–13)**
  * **Multivariate Analysis (14–15)**

---

## 📊 Key Insights

* Significant growth in digital transactions over time
* Certain states dominate both transaction volume and value
* User engagement (App Opens) strongly correlates with registered users
* High transaction count does not always mean high transaction value
* Category-wise behavior shows varied spending patterns

---

## 💼 Business Use Cases

* Customer segmentation based on transaction behavior
* Fraud detection using abnormal transaction patterns
* Regional marketing optimization
* Product and feature development
* Insurance service enhancement
* Trend forecasting and demand prediction

---

## 🧠 SQL Usage Highlights

* Aggregation using `SUM()`
* Multi-column grouping (`GROUP BY`)
* Ranking using `ORDER BY` + `LIMIT`
* Derived metrics (Average Transaction Value)
* Table joins for multivariate analysis

---

## 📁 Project Structure

```
PhonePe-SQL-Data-Analysis/
│
├── PhonePe_EDA_Project.ipynb   # Main analysis notebook
├── phonepe.db                 # SQLite database
├── README.md                  # Project documentation
```

---

## ▶️ How to Run the Project

1. Clone or download the repository
2. Open the notebook in Jupyter / Colab
3. Ensure `phonepe.db` is in the same directory
4. Run all cells sequentially

---

## 📌 Results

* End-to-end SQL-based data analysis pipeline
* Clear visualization of trends and patterns
* Strong understanding of real-world payment data
* Practical implementation of business analytics

---

## 👨‍💻 Author

**Harsh Kumar**

---

## ⭐ Final Note

This project demonstrates the transition from basic data handling (CSV) to **structured, scalable SQL-based analytics**, making it closer to real-world industry practices.
