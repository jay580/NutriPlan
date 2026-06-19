import streamlit as st
import requests
import pandas as pd
from components.sidebar import render_sidebar

st.set_page_config(page_title="Nutrition Analyzer", page_icon="🔍", layout="wide")

from config import API_BASE_URL

render_sidebar(API_BASE_URL)

st.title("🔍 Nutrition Analyzer")
st.markdown("Enter a meal description (e.g., '2 fried eggs and a banana') to analyze its nutritional content.")

query_input = st.text_area(
    "Meal Description", 
    placeholder="Example:\n2 fried eggs\n1 banana\n100g oats",
    help="Enter each ingredient on a new line or separate them with commas."
)

st.caption("Accepted format: Please enter each ingredient on a new line or separate them with commas. For best results, include quantities (e.g., '1 cup rice', '200g chicken breast').")

if st.button("Analyze Meal"):
    if not query_input:
        st.warning("Please enter a meal description.")
    else:
        # Format query: Spoonacular prefers one ingredient per line.
        query = query_input.replace(",", "\n").replace(" and ", "\n")
        query = "\n".join([line.strip() for line in query.split('\n') if line.strip()])
        
        with st.spinner("Analyzing meal..."):
            try:
                response = requests.post(f"{API_BASE_URL}/api/nutrition/analyze", json={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Meal analyzed successfully!")
                    
                    # Macro metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Calories", f"{data['calories']} kcal")
                    col2.metric("Protein", f"{data['protein']} g")
                    col3.metric("Carbs", f"{data['carbs']} g")
                    col4.metric("Fat", f"{data['fat']} g")
                    
                    st.markdown("---")
                    
                    col_ing, col_micro = st.columns(2)
                    
                    with col_ing:
                        st.subheader("Ingredients Breakdown")
                        for ing in data.get("ingredients", []):
                            st.markdown(f"**{ing.get('name', 'Unknown').title()}** ({ing.get('amount', 0)} {ing.get('unit', '')})")
                            st.markdown(f"- Calories: {ing.get('calories', 0)} kcal, Protein: {ing.get('protein', 0)}g, Carbs: {ing.get('carbs', 0)}g, Fat: {ing.get('fat', 0)}g")
                            
                    with col_micro:
                        st.subheader("Micronutrients Overview")
                        micros = data.get("micronutrients", {})
                        if micros:
                            df_micro = pd.DataFrame([
                                {"Nutrient": k, "Amount": f"{v['amount']} {v['unit']}"} 
                                for k, v in micros.items()
                            ])
                            st.dataframe(df_micro, use_container_width=True)
                        else:
                            st.info("No detailed micronutrient data available.")
                            
                else:
                    st.error(f"Analysis failed: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")
