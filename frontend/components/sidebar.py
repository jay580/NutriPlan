import streamlit as st
import requests
from datetime import date

def render_sidebar(api_base_url: str):
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #4CAF50;'>🥗 NutriPlan</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 0; margin-bottom: 20px;'/>", unsafe_allow_html=True)
        
        # Load active profile
        profile = None
        profile_id = st.session_state.get("active_profile_id")
        
        try:
            if profile_id:
                response = requests.get(f"{api_base_url}/api/diet/profile/{profile_id}")
            else:
                response = requests.get(f"{api_base_url}/api/diet/profile")
            
            if response.status_code == 200 and response.json():
                profile = response.json()
                if not profile_id:
                    st.session_state.active_profile_id = profile["id"]
        except Exception:
            pass
        
        if profile:
            st.markdown(f"### 👤 {profile.get('name', 'Profile')}")
            
            goal_map = {
                "lose": "Weight Loss 📉",
                "gain": "Weight Gain 📈",
                "maintain": "Maintenance ⚖️"
            }
            
            st.markdown(f"**Goal:** {goal_map.get(profile['goal'], profile['goal'].title())}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Calories", f"{profile['target_calories']} kcal")
            with col2:
                st.metric("Protein", f"{profile['target_protein']} g")
            
            # Today's calorie progress
            try:
                today_str = date.today().strftime("%Y-%m-%d")
                resp = requests.get(
                    f"{api_base_url}/api/tracker/daily",
                    params={"profile_id": profile["id"], "date": today_str}
                )
                if resp.status_code == 200:
                    daily = resp.json()
                    total_cal = daily.get("total_calories", 0)
                    target = profile["target_calories"]
                    pct = min(total_cal / target, 1.0) if target > 0 else 0
                    
                    st.markdown("---")
                    st.markdown("**📊 Today's Intake**")
                    st.caption(f"{total_cal} / {target} kcal")
                    st.progress(pct)
            except Exception:
                pass
                    
            with st.expander("Body Metrics"):
                st.write(f"**Age:** {profile['age']} years")
                st.write(f"**Gender:** {profile['gender'].title()}")
                st.write(f"**Weight:** {profile['weight']} kg")
                st.write(f"**Height:** {profile['height']} cm")
                st.write(f"**Activity:** {profile['activity_level'].replace('_', ' ').title()}")
        else:
            st.info("💡 **Setup Profile:** Head to the main page to create your first profile.")
        
        st.markdown("<br><hr/>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 0.8em; color: grey;'>Powered by FastAPI & Spoonacular</p>", unsafe_allow_html=True)
