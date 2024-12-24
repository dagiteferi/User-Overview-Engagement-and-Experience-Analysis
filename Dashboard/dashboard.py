import sys
import os
import streamlit as st

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Dashboard.multiapp import MultiApp
#from Dashboard.overview_page import app as overview_page
from Dashboard.engagement_analysis_page import app as engagement_analysis_page
from Dashboard.experience_analytics_page import app as experience_analytics_page
from scripts.DB_connection import PostgresConnection

# Set page configuration
st.set_page_config(page_title="Dashboard", page_icon="", layout="wide")

# Create the app instance
app = MultiApp()

# Add color styles for buttons and text
st.markdown(
    """
    <style>
    .stButton button {
        background-color: #4CAF50; 
        color: white;
        font-size: 16px;
        margin: 10px 0;
    }
    .stSidebar .css-1d391kg {
        background-color: #F4F4F4;
        border-radius: 5px;
    }
    .stSidebar .css-1d391kg .css-18e3th9 {
        background-color: #2C3E50;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main app page with descriptions only
def main():
    st.title('Main Dashboard')
    st.write("Welcome to the Interactive Dashboard!")
    
    st.markdown("""
        - **Overview Analysis**: Provides general insights about  metrics.
        - **Engagement Analysis**: Explores user engagement patterns in detail.
        - **Experience Analytics**: Analyzes user experience across various metrics.
    """)
    
    st.write("Use the navigation panel on the left to switch between sections.")

# Registering the pages
app.add_app("Main", main)
#app.add_app("Overview Analysis", overview_page)
app.add_app("Engagement Analysis", engagement_analysis_page)
app.add_app("Experience Analytics", experience_analytics_page)

# Running the app
app.run()
