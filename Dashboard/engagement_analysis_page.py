import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from scripts.DB_connection import PostgresConnection
from src.Eda import missing_values_table, convert_bytes_to_megabytes, convert_ms_to_seconds

def load_data():
    # Establishing the database connection
    db = PostgresConnection()
    db.connect()
    if db.conn:
        query = "SELECT * FROM xdr_data"
        result = db.execute_query(query)
        db.close_connection()
        if result:
            df = pd.DataFrame(result, columns=[desc[0] for desc in db.cursor.description])
            return df
        else:
            st.error("No results returned from the query.")
            return pd.DataFrame()
    else:
        st.error("Error: No database connection.")
        return pd.DataFrame()

def preprocess_engagement_data(df):
    user_engagement_columns = [
        'IMSI', 'MSISDN/Number',
        'Dur. (ms)', 'Activity Duration DL (ms)', 'Activity Duration UL (ms)',
        'Total DL (Bytes)', 'Total UL (Bytes)',
        'Social Media DL (Bytes)', 'Social Media UL (Bytes)',
        'YouTube DL (Bytes)', 'YouTube UL (Bytes)',
        'Netflix DL (Bytes)', 'Netflix UL (Bytes)',
        'Google DL (Bytes)', 'Google UL (Bytes)',
        'Email DL (Bytes)', 'Email UL (Bytes)',
        'Gaming DL (Bytes)', 'Gaming UL (Bytes)',
        'Other DL (Bytes)', 'Other UL (Bytes)',
        'Avg RTT DL (ms)', 'Avg RTT UL (ms)',
        'Avg Bearer TP DL (kbps)', 'Avg Bearer TP UL (kbps)'
    ]
    df_user_engagement = df[user_engagement_columns].copy()

    # Clean the data
    df_user_engagement.dropna(subset=['MSISDN/Number'], inplace=True)
    
    # Replace missing values with mean
    mean_rtt_dl = df_user_engagement['Avg RTT DL (ms)'].mean()
    mean_rtt_ul = df_user_engagement['Avg RTT UL (ms)'].mean()
    df_user_engagement['Avg RTT DL (ms)'].fillna(mean_rtt_dl, inplace=True)
    df_user_engagement['Avg RTT UL (ms)'].fillna(mean_rtt_ul, inplace=True)

    # Convert bytes to megabytes
    byte_columns = [
        'Total DL (Bytes)', 'Total UL (Bytes)',
        'Social Media DL (Bytes)', 'Social Media UL (Bytes)',
        'YouTube DL (Bytes)', 'YouTube UL (Bytes)',
        'Netflix DL (Bytes)', 'Netflix UL (Bytes)',
        'Google DL (Bytes)', 'Google UL (Bytes)',
        'Email DL (Bytes)', 'Email UL (Bytes)',
        'Gaming DL (Bytes)', 'Gaming UL (Bytes)',
        'Other DL (Bytes)', 'Other UL (Bytes)'
    ]
    for column in byte_columns:
        if column in df_user_engagement.columns:
            df_user_engagement[column] = df_user_engagement[column].apply(convert_bytes_to_megabytes)

    # Convert milliseconds to seconds
    millisecond_columns_to_convert = [
        'Dur. (ms)',
        'Activity Duration DL (ms)',
        'Activity Duration UL (ms)',
        'Avg RTT DL (ms)',
        'Avg RTT UL (ms)'
    ]
    for column in millisecond_columns_to_convert:
        if column in df_user_engagement.columns:
            df_user_engagement[column] = df_user_engagement[column].apply(convert_ms_to_seconds)

    # Rename columns
    df_user_engagement.rename(columns=lambda x: x.replace('Bytes', 'Megabytes') if 'Bytes' in x else x, inplace=True)
    df_user_engagement.rename(columns=lambda x: x.replace('(ms)', '(s)') if '(ms)' in x else x, inplace=True)
    
    return df_user_engagement

def group_data(df_user_engagement):
    grouped_df = df_user_engagement.groupby('MSISDN/Number').agg({
        'Dur. (s)': 'sum',
        'Total DL (Megabytes)': 'sum',
        'Total UL (Megabytes)': 'sum',
        'Activity Duration DL (s)': 'sum',
        'Activity Duration UL (s)': 'sum'
    }).reset_index()
    grouped_df['Total Traffic (Megabytes)'] = grouped_df['Total DL (Megabytes)'] + grouped_df['Total UL (Megabytes)']
    return grouped_df

def report_top_customers(df_user_engagement):
    grouped_df = group_data(df_user_engagement)

    top_10_duration = grouped_df.sort_values(by='Dur. (s)', ascending=False).head(10)
    top_10_download = grouped_df.sort_values(by='Total DL (Megabytes)', ascending=False).head(10)
    top_10_upload = grouped_df.sort_values(by='Total UL (Megabytes)', ascending=False).head(10)
    
    st.write("### Top 10 customers by session duration")
    st.write(top_10_duration)
    
    st.write("### Top 10 customers by total download traffic")
    st.write(top_10_download)
    
    st.write("### Top 10 customers by total upload traffic")
    st.write(top_10_upload)
    
    session_frequency = df_user_engagement.groupby('MSISDN/Number').size().reset_index(name='Session Frequency')
    grouped_df = grouped_df.merge(session_frequency, on='MSISDN/Number')
    top_10_session_frequency = grouped_df.sort_values(by='Session Frequency', ascending=False).head(10)
    
    st.write("### Top 10 customers by session frequency")
    st.write(top_10_session_frequency)
    
    return grouped_df

def normalize_and_cluster(grouped_df):
    columns_to_normalize = ['Dur. (s)', 'Total DL (Megabytes)', 'Total UL (Megabytes)', 'Session Frequency']
    scaler = MinMaxScaler()
    grouped_df[columns_to_normalize] = scaler.fit_transform(grouped_df[columns_to_normalize])

    kmeans = KMeans(n_clusters=3, random_state=42)
    grouped_df['Cluster'] = kmeans.fit_predict(grouped_df[columns_to_normalize])
    
    st.write("### Cluster Centers (Centroids)")
    st.write(kmeans.cluster_centers_)
    
    cluster_stats = grouped_df.groupby('Cluster').agg({
        'Dur. (s)': ['min', 'max', 'mean', 'sum'],
        'Total DL (Megabytes)': ['min', 'max', 'mean', 'sum'],
        'Total UL (Megabytes)': ['min', 'max', 'mean', 'sum'],
        'Session Frequency': ['min', 'max', 'mean', 'sum']
    }).reset_index()
    
    st.write("### Cluster Statistics")
    st.write(cluster_stats)
    
    return cluster_stats

def visualize_clusters(cluster_stats):
    plt.figure(figsize=(10, 6))
    plt.bar(cluster_stats['Cluster'], cluster_stats['Total DL (Megabytes)']['mean'], color=['skyblue', 'orange', 'green'])
    plt.title("Average Total Download Traffic per Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Average Total Download Traffic (Megabytes)")
    plt.show()
    
    st.pyplot()

    plt.figure(figsize=(10, 6))
    plt.bar(cluster_stats['Cluster'], cluster_stats['Dur. (s)']['mean'], color=['skyblue', 'orange', 'green'])
    plt.title("Average Session Duration per Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Average Session Duration (seconds)")
    plt.show()
    
    st.pyplot()

def app():
    st.title('Engagement Analysis')
    st.write("This is the engagement analysis page.")

    df = load_data()
    if not df.empty:
        df_user_engagement = preprocess_engagement_data(df)
        grouped_df = report_top_customers(df_user_engagement)
        cluster_stats = normalize_and_cluster(grouped_df)
        visualize_clusters(cluster_stats)
