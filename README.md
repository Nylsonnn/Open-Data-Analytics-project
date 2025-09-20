# 🚦 UK Open Data Analytics Dashboard

An interactive dashboard built with **Dash** and **Plotly** to explore UK road collision open data.  
It lets you filter by year and accident severity, view KPIs, trends, top road types, and plot accident locations on an interactive map.

---

## ✨ Features

-  **Key Metrics (KPIs):** total accidents, average casualties, average vehicles involved  
-  **Monthly accident trends** with interactive line charts  
-  **Top road types** by accident count  
-  **Map view** (sampled points) to explore accident locations  
---

## 🛠 Installation

1. **Clone the repo**  

```bash
git clone https://github.com/yourusername/uk-open-data-analytics.git
cd uk-open-data-analytics
```

2. **Prepare the data**  
Place the CSV accident data files in `app/data/`:

```
app/data/
├─ collisions_2019.csv
├─ collisions_2020.csv
├─ collisions_2021.csv
├─ collisions_2022.csv
├─ collisions_2023.csv
```

3. **Run with Docker Compose**  

```bash
docker-compose up --build
```

This starts:
- A **Postgres DB** (loads CSVs on first run)  
- The **Dash app** on [http://localhost:8050](http://localhost:8050)  

---

## Project Structure

```
.
├─ app/
│  ├─ dashboard.py       # Dash app
│  ├─ load_data.py       # CSV → Postgres loader (chunked)
│  ├─ requirements.txt   # Python dependencies
│  ├─ Dockerfile         # App image
│  └─ data/              # CSV data files
│     ├─ collisions_2019.csv
│     ├─ collisions_2020.csv
│     ├─ collisions_2021.csv
│     ├─ collisions_2022.csv
│     └─ collisions_2023.csv
│
├─ sql/                  # (optional) extra SQL scripts
├─ docker-compose.yml    # Services config
└─ README.md             # ← you’re here
```

---

## Development

If you want to run locally without Docker:

```bash
cd app
pip install -r requirements.txt
python dashboard.py
```

---

## Contributing

Contributions welcome! Feel free to fork, open issues, or submit PRs.  

---

## License

MIT — feel free to use and adapt.  

---

Built with ❤️ using Dash, Plotly, and PostgreSQL 🚀
