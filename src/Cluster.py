import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean

def load_centroids(engagement_path, experience_path):
    """
    Load the engagement and experience centroids from CSV files.
    """
    centroid_engagement = pd.read_csv(engagement_path, index_col='Cluster Name')
    centroid_experience = pd.read_csv(experience_path, index_col='Cluster Name')
    return centroid_engagement, centroid_experience

def calculate_engagement_score(user_data, centroid_engagement, engagement_columns):
    """
    Calculate the engagement score for each user based on the engagement centroids.
    """
    # Extract the centroid values for the "Low Engagement" cluster
    engagement_centroid_values = centroid_engagement.loc['Low Engagement'][engagement_columns].values

    # Calculate the engagement score as the Euclidean distance between the user's engagement metrics and the "Low Engagement" centroid
    user_data['Engagement Score'] = user_data[engagement_columns].apply(lambda row: euclidean(row, engagement_centroid_values), axis=1)
    return user_data

def calculate_experience_score(user_data, centroid_experience, experience_columns):
    """
    Calculate the experience score for each user based on the experience centroids.
    """
    # Extract the centroid values for the "Low-Performance Users" cluster
    experience_centroid = centroid_experience.loc['Low-Performance Users'][experience_columns].values

    # Calculate the experience score as the Euclidean distance between the user's experience metrics and the "Low-Performance Users" centroid
    user_data['Experience Score'] = user_data[experience_columns].apply(lambda row: euclidean(row, experience_centroid), axis=1)
    return user_data

def save_scores(df, output_path):
    """
    Save the DataFrame with the Engagement and Experience scores to a CSV file.
    """
    df.to_csv(output_path, index=False)
    full_file_path = os.path.abspath(output_path)
    return full_file_path
