<div align="center">

# 🚢 TitanicX — Survival Analytics Dashboard

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
<img src="https://img.shields.io/badge/Plotly-6.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge"/>

<br/>

**A premium, fully interactive Streamlit dashboard for automated EDA & Feature Engineering on the RMS Titanic dataset.**  
Built with a clean modular architecture — pure Pandas for all data logic, Plotly for rich visualizations, and a custom dark-theme SaaS design.

<br/>

### 🔗 [▶ Live Demo](https://titanicx.streamlit.app) &nbsp;|&nbsp; [📓 Notebook](./notebooks/TitanicX.ipynb)

<br/>

---

</div>

## ✨ Features at a Glance

| Feature | Details |
|---|---|
| **🧹 Smart Data Cleaning** | Median imputation for `Age`, mode-fill for `Embarked`, binary `has_cabin` flag, `Cabin` column dropped |
| **🔧 Feature Engineering** | `AgeGroup` via `pd.cut()` (Child/Teen/Adult/Senior) + `Title` extracted from `Name` using `.str` chain |
| **🎛 Interactive Sidebar** | Real-time `Pclass` & `Sex` filters with a live stats panel (passengers, survivors, survival %) |
| **📊 4-Tab Dashboard** | Overview · Deep Analysis · AI Insights · Data Explorer |
| **🔥 Pivot Heatmap** | Interactive `pivot_table()` rendered as a colour-scaled Plotly heatmap |
| **🤖 AI Insights Engine** | Confidence-scored insight cards per segment — score derived from sample size + historical policy bias |
| **📥 CSV Download** | One-click download of the full cleaned & enriched dataset |
| **🎨 Premium Dark UI** | Glassmorphism cards, gradient typography, Inter font, micro-animations via custom CSS |

---

## 🏗 Project Architecture

```
TitanicX/
│
├── app.py                    ← Streamlit entry point (pure orchestration)
├── titanic.csv               ← Raw dataset (891 × 12)
├── TitanicX.ipynb            ← Companion Jupyter notebook (manual EDA)
│
├── assets/
│   └── style.css             ← Dark-theme CSS (glassmorphism, gradients, Inter font)
│
├── data/
│   └── loader.py             ← @st.cache_data CSV reader
│
├── processing/
│   └── pipeline.py           ← clean() · engineer_features() · apply_filters()
│
├── analytics/
│   └── aggregations.py       ← All pandas aggregations + AI insights engine
│
└── ui/
    ├── sidebar.py            ← Sidebar filters + live stats panel
    ├── kpi_cards.py          ← 4-column KPI metric row
    ├── charts.py             ← Plotly charts (Overview + Deep Analysis)
    ├── insights.py           ← AI Insights tab
    └── explorer.py           ← Data Explorer + CSV download
```

> **Architecture principle:** `processing/` has zero Streamlit imports · `ui/` has zero pandas compute logic · `app.py` never computes anything.

---

## 📊 Dashboard Tabs

### 📊 Tab 1 — Overview
- **Survival Rate by Gender** — Bar chart (Women 74.2% vs Men 18.9%)
- **Survival Rate by Pclass** — Bar chart (1st 63% → 2nd 47% → 3rd 24%)
- **Pivot Heatmap** — `pivot_table(values='Survived', index='Pclass', columns='Sex', aggfunc='mean')`

### 🔬 Tab 2 — Deep Analysis
- **AgeGroup survival** — Child/Teen/Adult/Senior breakdown
- **Title survival** — Extracted from `Name` using `.str.split()` chain
- **Fare distribution** — Box plot by class (inside `st.expander`)
- **Correlation matrix** — Pearson r for all numeric features

### 🤖 Tab 3 — AI Insights & Scouting Report
Confidence-scored cards for every `(Pclass × Sex)` segment:

```
confidence = min(n / 50, 1.0) × 70     # sample-size score   (0 → 70 pts)
           + 30 if aligns with policy  # historical-bias bonus (0 or 30 pts)
           (capped at 100)
```

| Score | Badge | Meaning |
|---|---|---|
| ≥ 85% | 🟢 HIGH | Large sample + strong historical alignment |
| 60–84% | 🟡 MODERATE | Moderate sample or partial alignment |
| < 60% | 🔴 LOW | Small sample — interpret with caution |

### 📥 Tab 4 — Data Explorer
- Column selector (`st.multiselect`)
- Paginated DataFrame view
- Descriptive statistics expander
- **CSV download button** (cleaned + engineered dataset)

---

## 🧹 Data Pipeline

```python
# 1. Load (cached)
titanic = pd.read_csv("titanic.csv")

# 2. Clean
df["has_cabin"]  = df["Cabin"].notna().astype(int)
df["Age"]        = df["Age"].fillna(df["Age"].median())       # 177 NaNs → median 28
df["Embarked"]   = df["Embarked"].fillna(df["Embarked"].mode()[0])  # 2 NaNs → "S"
df               = df.drop(columns=["Cabin"])                 # 77% missing → dropped

# 3. Feature Engineering
df["AgeGroup"] = pd.cut(df["Age"], bins=[0,12,19,59,120],
                         labels=["Child","Teen","Adult","Senior"])
df["Title"]    = df["Name"].str.split(",").str[1].str.split(".").str[0].str.strip()

# 4. Filter (sidebar-driven)
mask = df["Pclass"].isin(selected_classes) & df["Sex"].isin(selected_genders)
filtered_df = df[mask]
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yousefelgohary/TitanicX.git
cd TitanicX
```

### 2. Install dependencies
```bash
pip install streamlit pandas plotly
```

### 3. Run the dashboard
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🌐 Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (already done ✅)
2. Go to **[share.streamlit.io](https://share.streamlit.io)**
3. Click **"New app"** → connect your GitHub account
4. Select:
   - **Repository:** `yousefelgohary/TitanicX`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **Deploy** — your app will be live in ~60 seconds

> Update the **Live Demo** badge at the top of this README with the deployed URL.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.35 | Web framework & UI components |
| `pandas` | ≥ 2.0 | All data processing & aggregation |
| `plotly` | ≥ 6.0 | Interactive charts & heatmaps |

No scikit-learn. No TensorFlow. Pure pandas EDA.

---

## 📋 Key Findings (Full Dataset)

| Metric | Value |
|---|---|
| Total Passengers | 891 |
| Overall Survival Rate | **38.4%** |
| 1st Class Women Survival | **~96.8%** |
| 3rd Class Men Survival | **~13.5%** |
| Survival Gap (best vs worst) | **83.3 pp** |

> All numbers are dynamically computed — update automatically when filters change.

---

## 🗂 Companion Notebook

[`TitanicX.ipynb`](./notebooks/TitanicX.ipynb) covers the same 10 tasks manually:

1. Explore — `.shape`, `.info()`, `.describe()`, missing value analysis  
2. Select — core column subset  
3. Filter — female 1st-class survivors (n=91)  
4. Sort — top 10 highest fares  
5. AgeGroup — `pd.cut()` with Unknown handling  
6. Handle missing — Age/Cabin/Embarked strategies  
7. Duplicates — check + interpretation  
8. Group & Aggregate — survival rate by Sex and Pclass  
9. Pivot Table — `pivot_table()` with `background_gradient`  
10. Title extraction — `.str.split()` chain + survival rate per title  

---

## 👨‍💻 Author

**Yousef Elgohary**  
ML for Data Science — NTI × Creativa  
Session 3: Pandas · Real-World Practice

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](./LICENSE) for details.

---

<div align="center">

Built with ❤️ using **Streamlit** · **Pandas** · **Plotly**

⭐ If you found this useful, please star the repo!

</div>
