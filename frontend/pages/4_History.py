import streamlit as st
import requests
import json
from components.sidebar import render_sidebar

st.set_page_config(page_title="History Logs", page_icon="🕒", layout="wide")

API_BASE_URL = "http://localhost:8000"

render_sidebar(API_BASE_URL)

st.title("🕒 Analysis History")

st.subheader("Recent Nutrition Analyses")
try:
    response = requests.get(f"{API_BASE_URL}/api/history/meals")
    if response.status_code == 200:
        meals = response.json()
        if not meals:
            st.info("No meal analysis history found. Use the Nutrition Analyzer to analyze meals.")
        else:
            for meal in meals:
                with st.expander(f"{meal['timestamp'][:10]} - '{meal['query']}' ({meal['calories']} kcal)"):
                    st.write(f"**Protein:** {meal['protein']}g | **Carbs:** {meal['carbs']}g | **Fat:** {meal['fat']}g")
                    st.write("**Ingredients:**", ", ".join([i.get("name", "unknown") for i in meal.get("ingredients", [])]))
    else:
        st.error("Failed to load meal history.")
except Exception as e:
    st.error(f"Error connecting to backend: {str(e)}")
