# 🤖 AI Agent Guide – PDF Data Dashboard Project

## 📌 Project Overview

This project is a Streamlit-based data analysis dashboard that:

* Converts PDF files into structured data (DataFrame)
* Allows exporting to Excel (XLSX) and CSV
* Provides interactive data analysis and visualization
* Generates semi-automated insights (report)

The goal is to simulate a real Data Analyst workflow:

> Data → Cleaning → Analysis → Visualization → Insight

---

## 🧠 Tech Stack

* Python
* Streamlit
* Pandas
* Plotly
* PDFPlumber
* Statsmodels (for regression in scatter plot)

---

## 📂 Project Structure (current)

* `app.py`: Main Streamlit app (UI + logic)
* `pdf_parser.py`: Extract tables from PDF
* `charts.py`: Chart generation
* `export_utils.py`: Export to CSV/XLSX
* `style.css`: UI styling

---

## 🎯 Coding Principles

### 1. Keep Everything Simple

* Avoid over-engineering
* Prefer readability over clever code

### 2. Do NOT Break Existing Logic

* Do not modify working features unless necessary
* Any improvement must be incremental

### 3. Streamlit Constraints Awareness

* Do NOT wrap multiple `st.*` components with HTML `<div>`
* UI styling should use:

  * single HTML blocks (`st.markdown`)
  * or native Streamlit components

### 4. Reusability

* Extract repeated logic into functions
* Example: `render_report()`

---

## 📊 UI/UX Guidelines

### ✅ Preferred

* Card-based layout using HTML + CSS
* Consistent spacing and structure
* Minimal, subtle animation
* Clear section separation

### ❌ Avoid

* Overuse of animation
* Complex frontend hacks
* Inconsistent UI patterns

---

## 📈 Data Handling Rules

* Always validate DataFrame before processing
* Handle missing values safely
* Avoid hardcoding column names when possible
* Prefer dynamic column selection

---

## 🧾 Insight Generation Rules

* Insights must be:

  * Short
  * Clear
  * Actionable

* Avoid:

  * Generic statements
  * Repetition

* Use:

  * Mean, median, std, skewness
  * Correlation (if applicable)

---

## 🧩 Chart Guidelines

* Use Plotly for interactivity
* Keep charts readable:

  * Avoid overcrowding
  * Use appropriate bin size for histogram
* Do NOT force animation on charts

---

## ⚙️ Dependency Management

* All required packages must be listed in `requirements.txt`
* Current dependencies:

  * streamlit
  * pandas
  * plotly
  * pdfplumber
  * openpyxl
  * statsmodels

---

## 🚫 What the AI Should NOT Do

* Do not introduce breaking changes
* Do not redesign entire architecture without request
* Do not add unnecessary libraries
* Do not complicate UI logic

---

## ✅ What the AI SHOULD Do

* Suggest incremental improvements
* Improve UI consistency
* Optimize code readability
* Help debug errors clearly
* Provide code snippets that can be copy-pasted directly

---

## 🎯 Goal of This Project

Transform this project from:

> "Student assignment"

Into:

> "Professional Data Analyst portfolio project"
