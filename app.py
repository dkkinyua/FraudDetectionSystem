import os
import pandas as pd
import joblib
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.express as px

load_dotenv()

# Load trained model
model = joblib.load("jobs/isolation_forest.pkl")

# Connect to DB
engine = create_engine(os.getenv("URL"))

# Load transactions table
df = pd.read_sql_table('transactions', con=engine, schema='shop')

# Load fraud labels table (only confirmed frauds)
fraud_df = pd.read_sql_table('fraud_transactions', con=engine, schema='shop')

# Preprocess like training
device_freq = df["device"].value_counts(normalize=True)
df['device_freq'] = df["device"].map(device_freq)
df["location_change"] = (df["location"] != df["transaction_location"]).astype(int)

# Features
X = df[['amount', 'device_freq', 'location_change']].copy()
X.columns = ['amount', 'device_freq', 'location_change']

# Predictions & scores
df['prediction'] = model.predict(X)
df['anomaly_score'] = model.decision_function(X)
df['anomaly_label'] = df['prediction'].map({1: 'Normal', -1: 'Fraud'})

# Mark known frauds
df['is_known_fraud'] = df['transaction_id'].isin(fraud_df['transaction_id'])

# Assign custom display label
df['display_label'] = df.apply(
    lambda row: "Known Fraud" if row['is_known_fraud'] else row['anomaly_label'],
    axis=1
)

# Streamlit UI
st.title("Fraud Detection Model Results")
st.subheader("IsolationForest Predictions Overview")

# --- Bar chart of fraud vs normal
counts = df['display_label'].value_counts()
st.bar_chart(counts)

# --- Scatter plot visualization with custom colors
color_map = {
    "Normal": "blue",
    "Fraud": "red",
    "Known Fraud": "yellow"
}
fig = px.scatter(
    df,
    x='amount', 
    y='device_freq', 
    color='display_label', 
    color_discrete_map=color_map,
    hover_data=['location', 'transaction_location', 'anomaly_score'],
    title="Transactions by Amount & Device Frequency"
)
st.plotly_chart(fig)

# --- Top 10 suspicious transactions
st.subheader("Top 10 Most Suspicious Transactions")
st.dataframe(df.sort_values(by='anomaly_score').head(10))

# =========================
# UNSUPERVISED PERFORMANCE CHECK
# =========================
st.subheader("Model Performance on Known Frauds")

# Check anomaly scores for known fraud transactions
fraud_matches = df[df['is_known_fraud']]

if not fraud_matches.empty:
    avg_score = fraud_matches['anomaly_score'].mean()
    median_score = fraud_matches['anomaly_score'].median()
    pct_flagged = (fraud_matches['prediction'] == -1).mean() * 100

    st.write(f"Average anomaly score for known frauds: **{avg_score:.4f}**")
    st.write(f"Median anomaly score for known frauds: **{median_score:.4f}**")
    st.write(f"Percentage of known frauds flagged: **{pct_flagged:.2f}%**")

    # Histogram of anomaly scores for all transactions
    st.subheader("Anomaly Score Distribution (All Transactions)")
    fig_hist = px.histogram(df, x='anomaly_score', nbins=50, title="Distribution of Anomaly Scores")
    st.plotly_chart(fig_hist)

    # Histogram for fraud-only transactions
    st.subheader("Anomaly Score Distribution (Known Frauds Only)")
    fig_fraud_hist = px.histogram(fraud_matches, x='anomaly_score', nbins=30, title="Known Frauds Anomaly Score Distribution")
    st.plotly_chart(fig_fraud_hist)
else:
    st.warning("No matching transaction IDs found between fraud_labels and transactions table.")
