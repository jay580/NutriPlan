import streamlit as st
import requests
from datetime import date, timedelta
from components.sidebar import render_sidebar

st.set_page_config(page_title="Calorie Tracker", page_icon="📊", layout="wide")

API_BASE_URL = "http://localhost:8000"

render_sidebar(API_BASE_URL)

st.title("📊 Daily Calorie Tracker")
st.markdown("Log your meals daily and track your nutrition intake against your targets.")

# ── Get active profile ──
active_profile = None
if "active_profile_id" in st.session_state:
    try:
        resp = requests.get(f"{API_BASE_URL}/api/diet/profile/{st.session_state.active_profile_id}")
        if resp.status_code == 200:
            active_profile = resp.json()
    except Exception:
        pass

if not active_profile:
    try:
        resp = requests.get(f"{API_BASE_URL}/api/diet/profile")
        if resp.status_code == 200 and resp.json():
            active_profile = resp.json()
            st.session_state.active_profile_id = active_profile["id"]
    except Exception:
        pass

if not active_profile:
    st.warning("⚠️ No profile found. Please create a profile on the Dashboard first.")
    st.stop()

profile_id = active_profile["id"]
target_cal = active_profile.get("target_calories", 2000)
target_pro = active_profile.get("target_protein", 150)

st.info(f"📌 Active Profile: **{active_profile.get('name', 'Default')}** | Target: **{target_cal} kcal** / **{target_pro}g protein**")

st.markdown("---")

# ── Date selector ──
selected_date = st.date_input("📅 Select Date", value=date.today())
date_str = selected_date.strftime("%Y-%m-%d")

# ── Log a meal ──
st.subheader("➕ Log a Meal")
st.caption("Enter your meal description below. The nutrition info will be fetched automatically via Spoonacular API.")
st.caption("💡 Tip: Enter each ingredient on a new line or separate with commas for best results (e.g., '1 cup rice, 100g chicken breast').")

with st.form("log_meal_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        meal_desc = st.text_area(
            "Meal Description",
            placeholder="Example:\n2 fried eggs\n1 banana\n100g oats",
        )
    with col2:
        meal_label = st.selectbox("Meal Type", options=["breakfast", "lunch", "dinner", "snack"])
    
    submitted = st.form_submit_button("Log Meal")
    
    if submitted:
        if not meal_desc.strip():
            st.warning("Please enter a meal description.")
        else:
            # Format: replace commas and 'and' with newlines
            formatted = meal_desc.replace(",", "\n").replace(" and ", "\n")
            formatted = "\n".join([line.strip() for line in formatted.split("\n") if line.strip()])
            
            with st.spinner("Analyzing nutrition via Spoonacular..."):
                try:
                    payload = {
                        "profile_id": profile_id,
                        "meal_description": formatted,
                        "meal_label": meal_label,
                        "date": date_str,
                    }
                    resp = requests.post(f"{API_BASE_URL}/api/tracker/log", json=payload)
                    if resp.status_code == 200:
                        log_data = resp.json()
                        if log_data["calories"] > 0:
                            st.success(
                                f"✅ Logged! {log_data['calories']} kcal | "
                                f"P: {log_data['protein']}g | C: {log_data['carbs']}g | F: {log_data['fat']}g"
                            )
                        else:
                            st.warning("Meal logged but nutrition data couldn't be fetched. Try rephrasing the ingredients.")
                        st.rerun()
                    else:
                        st.error(f"Failed to log meal: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown("---")

# ── Today's Logs ──
st.subheader(f"📋 Meals Logged on {selected_date.strftime('%B %d, %Y')}")

try:
    resp = requests.get(f"{API_BASE_URL}/api/tracker/daily", params={"profile_id": profile_id, "date": date_str})
    if resp.status_code == 200:
        daily_data = resp.json()
        logs = daily_data.get("logs", [])
        total_cal = daily_data.get("total_calories", 0)
        total_pro = daily_data.get("total_protein", 0)
        total_carb = daily_data.get("total_carbs", 0)
        total_fat = daily_data.get("total_fat", 0)

        # Progress bars
        st.markdown("### Daily Progress")
        col_cal, col_pro = st.columns(2)
        with col_cal:
            cal_pct = min(total_cal / target_cal, 1.0) if target_cal > 0 else 0
            st.metric("Calories", f"{total_cal} / {target_cal} kcal")
            st.progress(cal_pct)
        with col_pro:
            pro_pct = min(total_pro / target_pro, 1.0) if target_pro > 0 else 0
            st.metric("Protein", f"{total_pro} / {target_pro} g")
            st.progress(pro_pct)

        col_carb, col_fat = st.columns(2)
        with col_carb:
            st.metric("Carbs", f"{total_carb} g")
        with col_fat:
            st.metric("Fat", f"{total_fat} g")

        st.markdown("---")

        if not logs:
            st.info("No meals logged for this date yet.")
        else:
            LABEL_EMOJI = {
                "breakfast": "🌅",
                "lunch": "🍛",
                "dinner": "🌙",
                "snack": "🥜",
            }
            for log in logs:
                emoji = LABEL_EMOJI.get(log.get("meal_label", ""), "🍽️")
                label = (log.get("meal_label") or "meal").capitalize()
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    with st.expander(f"{emoji} {label}: {log['meal_description'][:60]}... — **{log['calories']} kcal**"):
                        st.write(f"**Protein:** {log['protein']}g | **Carbs:** {log['carbs']}g | **Fat:** {log['fat']}g")
                        st.write(f"**Logged at:** {log['timestamp']}")
                with col_del:
                    if st.button("🗑️", key=f"del_{log['id']}", help="Delete this entry"):
                        try:
                            del_resp = requests.delete(f"{API_BASE_URL}/api/tracker/log/{log['id']}")
                            if del_resp.status_code == 200:
                                st.rerun()
                        except Exception:
                            st.error("Failed to delete.")
    else:
        st.error("Failed to load daily data.")
except Exception as e:
    st.error(f"Error: {str(e)}")
