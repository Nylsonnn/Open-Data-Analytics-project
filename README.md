# 📊 UK Open Data Analytics personal project

A portfolio project given to me by a friend, exploring a large **UK public dataset** (NHS, transport, or crime statistics) and turning raw data into meaningful insights.
I want to try and further my skills and test current knowledge so this holds as a decent middle ground for now.

---

## 🚀 Objectives  
- Ingest and model a UK open dataset into a **Postgres warehouse**.  
- Apply **schema design, indexing, and query optimisation** to improve performance.  
- Build an **interactive dashboard** (Dash/Streamlit) for visualising insights.  
- Share reproducible benchmarks and lessons learned.  

---

## 🛠️ Tech Stack  
- **Database**: Postgres (Dockerised)  
- **Languages**: SQL, Python (Pandas)  
- **Visualisation**: Dash / Streamlit  
- **Containerisation**: Docker + docker-compose  

---

## 📂 Project Structure  
```bash
sql/                 # schema, indexes, benchmark queries  
notebooks/           # exploratory analysis (Jupyter)  
app/                 # dashboard (Dash/Streamlit)  
docker-compose.yml   # container setup  
