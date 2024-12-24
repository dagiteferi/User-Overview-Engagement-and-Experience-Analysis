import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os

def preprocess_experience_metrics(df_cleaned, experience_metrics_descriptive):
    # Drop rows with missing values in the selected columns
    df_experience = df_cleaned[list(experience_metrics_descriptive.keys())].dropna()
    
    # Standardize the data
    scaler = StandardScaler()
    experience_metrics_scaled = scaler.fit_transform(df_experience)
    
    # Convert scaled data back to a DataFrame for reference
    df_experience_scaled = pd.DataFrame(experience_metrics_scaled, columns=experience_metrics_descriptive.values())
    
    return df_experience_scaled, scaler

def perform_kmeans_clustering(df_experience_scaled, n_clusters):
    # Perform k-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df_experience_scaled['Experience Group'] = kmeans.fit_predict(df_experience_scaled)
    
    return df_experience_scaled, kmeans

def map_cluster_names(df_experience_scaled, cluster_names):
    # Add descriptive cluster names
    df_experience_scaled['Experience Group Name'] = df_experience_scaled['Experience Group'].map(cluster_names)
    
    return df_experience_scaled

def save_centroids(kmeans, scaler, experience_metrics_descriptive, cluster_names, file_path):
    # Retrieve the centroids in the scaled space
    centroids_scaled = kmeans.cluster_centers_
    
    # Inverse transform the centroids to the original scale
    centroids_original = scaler.inverse_transform(centroids_scaled)
    
    # Create a DataFrame to store centroids with descriptive cluster names
    centroid_experience = pd.DataFrame(centroids_original, columns=experience_metrics_descriptive.values())
    centroid_experience['Cluster Name'] = [cluster_names[i] for i in range(len(centroids_original))]
    
    # Set 'Cluster Name' as the index for easier referencing
    centroid_experience.set_index('Cluster Name', inplace=True)
    
    # Save the centroid_experience DataFrame to a CSV file
    centroid_experience.to_csv(file_path, index=True)
    
    return centroid_experience, os.path.abspath(file_path)

def describe_clusters(df_cleaned, experience_metrics_descriptive, cluster_names):
    # Brief description of each cluster based on the average of experience metrics
    cluster_description = df_cleaned.groupby('Experience Group Name')[list(experience_metrics_descriptive.keys())].mean()
    cluster_description.columns = experience_metrics_descriptive.values()
    
    # Print the cluster descriptions
    descriptions = []
    for group_name in cluster_description.index:
        description = ( f"\n{group_name}:\n" "This group of users tends to have the following network experience characteristics:\n" f"- Average Downlink Round-Trip Time: {cluster_description.loc[group_name, 'Average Downlink Round-Trip Time (s)']:.2f} s\n" f"- Average Uplink Round-Trip Time: {cluster_description.loc[group_name, 'Average Uplink Round-Trip Time (s)']:.2f} s\n" f"- Average Downlink Throughput: {cluster_description.loc[group_name, 'Average Downlink Throughput (kbps)']:.2f} kbps\n" f"- Average Uplink Throughput: {cluster_description.loc[group_name, 'Average Uplink Throughput (kbps)']:.2f} kbps\n" f"- Downlink TCP Retransmission Volume: {cluster_description.loc[group_name, 'Downlink TCP Retransmission Volume (Megabytes)']:.2f} Megabytes\n" f"- Uplink TCP Retransmission Volume: {cluster_description.loc[group_name, 'Uplink TCP Retransmission Volume (Megabytes)']:.2f} Megabytes\n" )
        descriptions.append(description)
    
    return cluster_description, descriptions
