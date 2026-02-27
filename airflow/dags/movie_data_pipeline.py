"""
Airflow DAG for the FARAGNY movie data pipeline.

This DAG runs weekly and performs two sequential tasks:
1. Clean the raw movie dataset (clean_data.py)
2. Rebuild the Chroma vector store (update_vectors.py)
"""

from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Import the pipeline functions
from pipelines.clean_data import clean_movies_dataset
from pipelines.update_vectors import refresh_vector_store


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="movie_data_pipeline",
    default_args=default_args,
    description="Weekly pipeline to clean movie data and update vector store",
    schedule_interval="@weekly",
    start_date=days_ago(1),
    catchup=False,
    tags=["faragny", "movies", "etl"],
) as dag:

    clean_data_task = PythonOperator(
        task_id="clean_movie_data",
        python_callable=clean_movies_dataset,
        doc="Cleans the raw Kaggle dataset and exports processed_movies.csv",
    )

    update_vectors_task = PythonOperator(
        task_id="update_vector_store",
        python_callable=refresh_vector_store,
        doc="Rebuilds the Chroma vector store from the processed dataset",
    )

    # Set task dependencies: clean_data runs first, then update_vectors
    clean_data_task >> update_vectors_task
