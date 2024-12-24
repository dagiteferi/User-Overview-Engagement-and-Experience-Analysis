import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scripts.DB_connection import PostgresConnection

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

def preprocess_data(df):
    user_experience_columns = [
        'IMSI', 'Handset Type', 'Handset Manufacturer', 
        'Avg RTT DL (ms)', 'Avg RTT UL (ms)', 
        'Avg Bearer TP DL (kbps)', 'Avg Bearer TP UL (kbps)', 
        'TCP DL Retrans. Vol (Bytes)', 'TCP UL Retrans. Vol (Bytes)'
    ]
    df_user_experience = df[user_experience_columns].copy()
    
    # Clean the data
    df_user_experience.dropna(subset=['IMSI', 'Handset Type'], inplace=True)
    
    # Fill missing values with mean
    for col in ['Avg RTT DL (ms)', 'Avg RTT UL (ms)', 'TCP DL Retrans. Vol (Bytes)', 'TCP UL Retrans. Vol (Bytes)']:
        df_user_experience[col].fillna(df_user_experience[col].mean(), inplace=True)

    # Byte to Megabyte conversion
    byte_columns = ['TCP DL Retrans. Vol (Bytes)', 'TCP UL Retrans. Vol (Bytes)']
    for column in byte_columns:
        df_user_experience[column] = df_user_experience[column] / (1024 * 1024)  # Convert to megabytes
    
    # Milliseconds to seconds conversion
    millisecond_columns = ['Avg RTT DL (ms)', 'Avg RTT UL (ms)']
    for column in millisecond_columns:
        df_user_experience[column] = df_user_experience[column] / 1000  # Convert to seconds
    
    # Rename columns
    df_user_experience.rename(columns=lambda x: x.replace('Bytes', 'Megabytes') if 'Bytes' in x else x, inplace=True)
    df_user_experience.rename(columns=lambda x: x.replace('(ms)', '(s)') if '(ms)' in x else x, inplace=True)
    
    return df_user_experience

def analyze_experience(df_user_experience):
    df_user_experience['Total TCP Retransmission'] = df_user_experience['TCP DL Retrans. Vol (Megabytes)'] + df_user_experience['TCP UL Retrans. Vol (Megabytes)']
    df_user_experience['Total RTT'] = df_user_experience['Avg RTT DL (s)'] + df_user_experience['Avg RTT UL (s)']
    df_user_experience['Total Throughput'] = df_user_experience['Avg Bearer TP DL (kbps)'] + df_user_experience['Avg Bearer TP UL (kbps)']

    st.write("### Top, Bottom, and Most Frequent Values")

    # Top, bottom, and most frequent values for TCP
    st.write("#### TCP Retransmission")
    top_10_tcp = df_user_experience['Total TCP Retransmission'].nlargest(10)
    bottom_10_tcp = df_user_experience['Total TCP Retransmission'].nsmallest(10)
    most_frequent_tcp = df_user_experience['Total TCP Retransmission'].value_counts().head(10)
    st.write("Top 10 TCP Retransmission Values:\n", top_10_tcp)
    st.write("Bottom 10 TCP Retransmission Values:\n", bottom_10_tcp)
    st.write("Most Frequent TCP Retransmission Values:\n", most_frequent_tcp)

    # Top, bottom, and most frequent values for RTT
    st.write("#### RTT Values")
    top_10_rtt = df_user_experience['Total RTT'].nlargest(10)
    bottom_10_rtt = df_user_experience['Total RTT'].nsmallest(10)
    most_frequent_rtt = df_user_experience['Total RTT'].value_counts().head(10)
    st.write("Top 10 RTT Values:\n", top_10_rtt)
    st.write("Bottom 10 RTT Values:\n", bottom_10_rtt)
    st.write("Most Frequent RTT Values:\n", most_frequent_rtt)

    # Top, bottom, and most frequent values for Throughput
    st.write("#### Throughput Values")
    top_10_throughput = df_user_experience['Total Throughput'].nlargest(10)
    bottom_10_throughput = df_user_experience['Total Throughput'].nsmallest(10)
    most_frequent_throughput = df_user_experience['Total Throughput'].value_counts().head(10)
    st.write("Top 10 Throughput Values:\n", top_10_throughput)
    st.write("Bottom 10 Throughput Values:\n", bottom_10_throughput)
    st.write("Most Frequent Throughput Values:\n", most_frequent_throughput)

    # Average throughput per handset type
    st.write("### Average Throughput per Handset Type")
    df_user_experience['Avg Throughput'] = (df_user_experience['Avg Bearer TP DL (kbps)'] + df_user_experience['Avg Bearer TP UL (kbps)']) / 2
    throughput_per_handset = df_user_experience.groupby('Handset Type')['Avg Throughput'].mean().reset_index()
    st.write(throughput_per_handset)

def cluster_experience(df_user_experience):
    # Prepare the data for clustering
    df_user_experience['Total TCP Retransmission'] = df_user_experience['TCP DL Retrans. Vol (Megabytes)'] + df_user_experience['TCP UL Retrans. Vol (Megabytes)']
    df_user_experience['Avg Throughput'] = (df_user_experience['Avg Bearer TP DL (kbps)'] + df_user_experience['Avg Bearer TP UL (kbps)']) / 2
    df_user_experience['Total RTT'] = df_user_experience['Avg RTT DL (s)'] + df_user_experience['Avg RTT UL (s)']

    clustering_data = df_user_experience[['Total TCP Retransmission', 'Avg RTT DL (s)', 'Avg Throughput']].copy()

    # Ensure the columns are numeric
    clustering_data = clustering_data.apply(pd.to_numeric, errors='coerce')

    # Drop any rows with NaN values
    clustering_data = clustering_data.dropna()

    # Standardize the data
    scaler = StandardScaler()
    clustering_data_scaled = scaler.fit_transform(clustering_data)

    # Applying K-Means Clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_user_experience['Cluster'] = kmeans.fit_predict(clustering_data_scaled)

    # Analyze clusters
    numeric_columns = ['Total TCP Retransmission', 'Avg RTT DL (s)', 'Avg Throughput']
    cluster_analysis = df_user_experience.groupby('Cluster')[numeric_columns].mean()

    # Display the clusters' description in a table format
    st.write("### Cluster Analysis")
    st.write(cluster_analysis)

def app():
    st.title('Experience Analytics')
    st.write("This is the experience analytics page.")
    
    df = load_data()
    if not df.empty:
        df_user_experience = preprocess_data(df)
        analyze_experience(df_user_experience)
        cluster_experience(df_user_experience)
