from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from typing import List, Dict

# --- Configuration ---
BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"
CSV_FILE_PATH = "/tmp/federal_register_last2days.csv"
TABLE_NAME = "documents"
MYSQL_CONN_ID = "mysql_local"

# XCom Keys
XCOM_KEY_RAW_DATA = "raw_data"
XCOM_KEY_CLEANED_DATA = "cleaned_data"

# --- Helper to build SQLAlchemy connection from Airflow Connection ---
def get_sqlalchemy_engine_from_conn_id(conn_id: str):
    conn = BaseHook.get_connection(conn_id)
    return create_engine(
        f"mysql+pymysql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
    )

# --- Task Functions ---

def fetch_federal_register_data(**context) -> None:
    combined_results = []

    for delta in range(2):
        date_str = (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d")
        print(f"[Fetch] Getting data for: {date_str}")

        params = {
            "conditions[publication_date]": date_str,
            "per_page": 100,
            "order": "newest"
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            combined_results.extend(response.json().get("results", []))
        else:
            print(f"[Fetch] Failed on {date_str}: {response.status_code}")

    context['ti'].xcom_push(key=XCOM_KEY_RAW_DATA, value=combined_results)

def clean_data(**context) -> None:
    raw_data = context['ti'].xcom_pull(task_ids='fetch_data', key=XCOM_KEY_RAW_DATA)
    cleaned = [
        {
            "document_number": item.get("document_number"),
            "title": item.get("title"),
            "doc_type": item.get("type"),
            "publication_date": item.get("publication_date")
        }
        for item in raw_data
    ]
    context['ti'].xcom_push(key=XCOM_KEY_CLEANED_DATA, value=cleaned)

def save_to_csv(**context) -> None:
    cleaned_data = context['ti'].xcom_pull(task_ids='clean_data', key=XCOM_KEY_CLEANED_DATA)
    df = pd.DataFrame(cleaned_data)
    df.to_csv(CSV_FILE_PATH, index=False)
    print(f"[CSV] Saved to {CSV_FILE_PATH}")

def push_to_mysql(**context) -> None:
    cleaned_data = context['ti'].xcom_pull(task_ids='clean_data', key=XCOM_KEY_CLEANED_DATA)
    df = pd.DataFrame(cleaned_data)

    engine = get_sqlalchemy_engine_from_conn_id(MYSQL_CONN_ID)

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        document_number VARCHAR(50),
        title TEXT,
        doc_type VARCHAR(50),
        publication_date DATE
    );
    """

    with engine.begin() as conn:
        conn.execute(text(create_table_sql))

    df.to_sql(TABLE_NAME, con=engine, if_exists='append', index=False)
    print(f"[MySQL] Data inserted into '{TABLE_NAME}' successfully.")

# --- DAG Definition ---

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False
}

with DAG(
    dag_id='federal_register_data_pipeline',
    default_args=default_args,
    description='ETL pipeline for Federal Register API to local MySQL',
    schedule_interval='0 6,18 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['federal_register'],
) as dag:

    fetch_data = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_federal_register_data,
        provide_context=True
    )

    clean_data_task = PythonOperator(
        task_id='clean_data',
        python_callable=clean_data,
        provide_context=True
    )

    save_csv = PythonOperator(
        task_id='save_csv',
        python_callable=save_to_csv,
        provide_context=True
    )

    push_mysql = PythonOperator(
        task_id='push_mysql',
        python_callable=push_to_mysql,
        provide_context=True
    )

    fetch_data >> clean_data_task >> save_csv >> push_mysql
