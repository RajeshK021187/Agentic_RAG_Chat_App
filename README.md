
# AI-Powered Chat System with Daily-Updated Data (Agentic RAG System)

## 🔍 What is the Project About?

A chat system where users ask questions, and a smart AI (LLM) answers them using fresh, daily-updated data from a MySQL database. The AI chooses specific tools to get accurate answers based on the query intent.

---

## ⚙️ Components Overview

### 🧱 1. Data Pipeline (Apache Airflow)
- A scheduled **Apache Airflow DAG** runs daily.
- It **downloads, refines, cleans, and inserts** fresh data into MySQL.
- This ensures the AI system always uses the **most recent data**.
- No manual work is needed after setup — the pipeline is fully automated.

### 🤖 2. AI Agent (LLM)
- Uses **predefined tool functions** to securely access MySQL.
- The LLM decides which function/tool to use based on user query intent.

### 🛰️ 3. API Backend (FastAPI)
- FastAPI handles incoming queries from the frontend.
- It interacts with the LLM and returns the response to the UI.

### 💬 4. Frontend Chat (Streamlit)
- A simple chat-based user interface.
- Users enter queries and get context-aware responses powered by LLM and live data.

---

## 🛠️ Technologies Used

- **Python 3.9+**
- **FastAPI** – Async API backend
- **Streamlit** – Chat-based frontend
- **MySQL** – Structured relational database
- **Ollama (e.g., qwen2.5)** – Local LLM
- **Apache Airflow** – Workflow orchestration for data ingestion
- **aiohttp / aiomysql** – Async processing and database access

---

## 🚀 Setup Instructions

### Step 1: Install Python Dependencies

```bash
pip install fastapi uvicorn streamlit mysql-connector-python aiomysql aiohttp apache-airflow
```

### Step 2: Set Up MySQL

- Install MySQL Server.
- Create a database and tables required by the pipeline.
- Insert initial schema using raw SQL files (optional).

### Step 3: Set Up Apache Airflow

Initialize Airflow:

```bash
airflow db init
airflow users create --username admin --password admin --role Admin --email admin@example.com --firstname Admin --lastname User
```

Place your DAG in the `dags/` folder.

Start the scheduler and web server:

```bash
airflow scheduler
airflow webserver
```

The DAG will trigger daily and keep your MySQL data updated automatically.

### Step 4: Run Backend API

```bash
uvicorn main:app --reload
```

### Step 5: Launch Chat UI

```bash
streamlit run app.py
```

---

## 🧠 Summary for Managers

> “This is a fully automated, secure, and cost-effective AI chat system. It combines local AI, structured database access, and a daily-refresh data pipeline using Airflow — ensuring up-to-date, relevant answers in real time.”
