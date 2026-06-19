#checking workflow

import streamlit as st
import requests
from datetime import date
from components.sidebar import render_sidebar


# Configure page
st.set_page_config(page_title="NutriPlan Dashboard", page_icon="🥗", layout="wide")

from config import API_BASE_URL

render_sidebar(API_BASE_URL)

st.title("🥗 NutriPlan Dashboard")
st.markdown("Welcome to NutriPlan! Manage your profiles, set goals, and track your nutrition.")

# ══════════════════════════════════════════════
# ── PROFILE MANAGEMENT ──
# ══════════════════════════════════════════════
st.subheader("👤 Profile Management")

# Load all profiles
profiles = []
try:
    resp = requests.get(f"{API_BASE_URL}/api/diet/profiles")
    if resp.status_code == 200:
        profiles = resp.json()
except Exception:
    st.error("Could not load profiles from backend.")

# Initialize active profile
if "active_profile_id" not in st.session_state and profiles:
    st.session_state.active_profile_id = profiles[0]["id"]

# ── Profile Switcher ──
if profiles:
    profile_options = {p["id"]: f"{p.get('name', 'Profile')} (ID: {p['id']})" for p in profiles}
    
    current_id = st.session_state.get("active_profile_id", profiles[0]["id"])
    if current_id not in profile_options:
        current_id = profiles[0]["id"]
        st.session_state.active_profile_id = current_id
    
    profile_ids = list(profile_options.keys())
    current_idx = profile_ids.index(current_id) if current_id in profile_ids else 0
    
    selected_id = st.selectbox(
        "Active Profile",
        options=profile_ids,
        index=current_idx,
        format_func=lambda x: profile_options[x],
    )
    
    if selected_id != st.session_state.get("active_profile_id"):
        st.session_state.active_profile_id = selected_id
        st.rerun()

    # Show active profile details
    active_profile = next((p for p in profiles if p["id"] == st.session_state.active_profile_id), None)
    if active_profile:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🎯 Target Calories", f"{active_profile['target_calories']} kcal")
        col2.metric("💪 Target Protein", f"{active_profile['target_protein']} g")
        col3.metric("⚖️ Weight", f"{active_profile['weight']} kg")
        goal_map = {"lose": "Weight Loss 📉", "gain": "Weight Gain 📈", "maintain": "Maintain ⚖️"}
        col4.metric("🏆 Goal", goal_map.get(active_profile["goal"], active_profile["goal"]))

        # Delete profile button
        if len(profiles) > 1:
            if st.button(f"🗑️ Delete Profile: {active_profile.get('name', 'Profile')}", type="secondary"):
                try:
                    del_resp = requests.delete(f"{API_BASE_URL}/api/diet/profile/{active_profile['id']}")
                    if del_resp.status_code == 200:
                        st.success("Profile deleted!")
                        remaining = [p for p in profiles if p["id"] != active_profile["id"]]
                        if remaining:
                            st.session_state.active_profile_id = remaining[0]["id"]
                        else:
                            del st.session_state["active_profile_id"]
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {str(e)}")
        elif len(profiles) == 1:
            st.caption("ℹ️ This is your only profile. Create another before deleting.")
else:
    st.info("💡 No profiles found. Create your first profile below!")

# ══════════════════════════════════════════════
# ── CREATE / UPDATE PROFILE ──
# ══════════════════════════════════════════════
st.markdown("---")
st.subheader("➕ Create New Profile")

with st.form("profile_form"):
    profile_name = st.text_input("Profile Name", value="", placeholder="e.g. My Cutting Plan, Bulk Phase")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=15, max_value=100, value=25)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
        gender = st.selectbox("Gender", options=["male", "female"])
        
    with col2:
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
        activity_level = st.selectbox(
            "Activity Level", 
            options=["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"],
            index=2
        )
        goal = st.selectbox(
            "Goal", 
            options=["lose", "maintain", "gain"],
            index=1
        )
        
    submit = st.form_submit_button("Create Profile")
    
    if submit:
        payload = {
            "name": profile_name or "Default Profile",
            "age": age,
            "gender": gender,
            "weight": weight,
            "height": height,
            "activity_level": activity_level,
            "goal": goal
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/api/diet/profile", json=payload)
            if response.status_code == 200:
                st.success("Profile created successfully!")
                data = response.json()
                st.info(f"Your Target Calories: {data['target_calories']} kcal | Target Protein: {data['target_protein']} g")
                st.session_state.active_profile_id = data["id"]
                st.rerun()
            else:
                st.error(f"Failed to create profile: {response.text}")
        except Exception as e:
            st.error(f"Error connecting to backend: {str(e)}")

# ══════════════════════════════════════════════
# ── CALORIE TRACKING HISTORY ──
# ══════════════════════════════════════════════
if profiles and "active_profile_id" in st.session_state:
    st.markdown("---")
    st.subheader("📊 Calorie Tracking History")
    
    active_id = st.session_state.active_profile_id
    active_p = next((p for p in profiles if p["id"] == active_id), None)
    
    if active_p:
        st.caption(f"Showing history for **{active_p.get('name', 'Profile')}**")
        
        try:
            resp = requests.get(f"{API_BASE_URL}/api/tracker/history", params={"profile_id": active_id, "limit": 14})
            if resp.status_code == 200:
                history = resp.json()
                if not history:
                    st.info("No calorie tracking history yet. Start logging meals on the Calorie Tracker page!")
                else:
                    target_cal = active_p.get("target_calories", 2000)
                    
                    for day in history:
                        day_date = day["date"]
                        total_cal = day["total_calories"]
                        total_pro = day["total_protein"]
                        total_carb = day["total_carbs"]
                        total_fat = day["total_fat"]
                        meal_count = day["meal_count"]
                        
                        cal_pct = int((total_cal / target_cal) * 100) if target_cal > 0 else 0
                        status = "✅" if 80 <= cal_pct <= 120 else ("⚠️" if cal_pct < 80 else "🔴")
                        
                        with st.expander(f"{status} {day_date} — {total_cal} kcal ({cal_pct}% of target) — {meal_count} meals"):
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("Calories", f"{total_cal} kcal")
                            c2.metric("Protein", f"{total_pro} g")
                            c3.metric("Carbs", f"{total_carb} g")
                            c4.metric("Fat", f"{total_fat} g")
            else:
                st.error("Failed to load calorie history.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
