# Curation Workstream Dashboard

This project provides a Streamlit-based dashboard for analyzing and visualizing team application usage from CSV logs. It helps managers get a bird's-eye view of work patterns, most used applications, and alerts for non-standard work norms.

## Features
- Total and per-user application usage
- Most used applications
- Work pattern trends (by hour/day)
- Alerts for non-standard work patterns (e.g., low activity, excessive use of non-work apps)

## Setup Instructions

1. Clone or copy this folder to your local machine.
2. Place your CSV log file (e.g., AppUsage_2026-01.csv) in this directory.
3. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## Requirements
- Python 3.8+
- Streamlit
- pandas
- matplotlib or plotly (for charts)

---

For questions or improvements, contact your dashboard maintainer.
