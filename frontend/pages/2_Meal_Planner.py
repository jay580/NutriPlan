import streamlit as st
import requests
import pandas as pd
from components.sidebar import render_sidebar

st.set_page_config(page_title="Meal Planner", page_icon="🍱", layout="wide")

from config import API_BASE_URL

render_sidebar(API_BASE_URL)

st.title("🍱 Meal Planner")
st.markdown("Get meal plans tailored to your fitness goals and dietary preferences.")

st.info(
    "💡 **Note:** Because the Spoonacular API does not support traditional Indian meals well, this page is an ongoing "
    "effort to provide custom-curated Indian recipes and database entries for nutrition tracking. While the number of "
    "pre-loaded meals is currently small, we are constantly expanding this list!"
)


# Try to load active profile for auto-recommendation
active_profile = None
if "active_profile_id" in st.session_state:
    try:
        resp = requests.get(f"{API_BASE_URL}/api/diet/profile/{st.session_state.active_profile_id}")
        if resp.status_code == 200:
            active_profile = resp.json()
    except Exception:
        pass

# If no active profile set, try latest
if not active_profile:
    try:
        resp = requests.get(f"{API_BASE_URL}/api/diet/profile")
        if resp.status_code == 200 and resp.json():
            active_profile = resp.json()
            st.session_state.active_profile_id = active_profile["id"]
    except Exception:
        pass

st.markdown("---")

# ── Meal Plan Recommendations ──
st.subheader("📋 Recommended Meal Plans")

PLAN_LABELS = {
    "weight_gain_muscle": "💪 Weight Gain / Muscle Building",
    "weight_loss": "📉 Weight Loss",
    "maintenance": "⚖️ Maintenance",
    "vegan": "🌱 Vegan",
    "vegetarian": "🥬 Vegetarian",
    "eggetarian": "🥚 Eggetarian",
    "high_protein_low_carb": "🥩 High Protein / Low Carb",
}

MEAL_EMOJIS = {
    "breakfast": "🌅",
    "mid-morning snack": "🍎",
    "lunch": "🍛",
    "evening snack": "🥜",
    "dinner": "🌙",
}

def get_meal_emoji(meal_text: str) -> str:
    lower = meal_text.lower()
    for key, emoji in MEAL_EMOJIS.items():
        if lower.startswith(key):
            return emoji
    return "🍽️"

# Auto-recommend based on profile goal
col_goal, col_diet = st.columns(2)
with col_goal:
    goal_options = ["lose", "gain", "maintain"]
    default_goal_idx = 0
    if active_profile and active_profile.get("goal") in goal_options:
        default_goal_idx = goal_options.index(active_profile["goal"])
    selected_goal = st.selectbox("Your Goal", options=goal_options, index=default_goal_idx, format_func=lambda x: {"lose": "🔥 Lose Weight", "gain": "💪 Gain Weight", "maintain": "⚖️ Maintain Weight"}.get(x, x))

with col_diet:
    diet_options = ["None", "vegan", "vegetarian", "eggetarian"]
    selected_diet = st.selectbox("Diet Preference (optional)", options=diet_options)

# Fetch recommended plans
try:
    params = {"goal": selected_goal}
    if selected_diet != "None":
        params["diet"] = selected_diet

    resp = requests.get(f"{API_BASE_URL}/api/meal-planner/recommend", params=params)
    if resp.status_code == 200:
        plans = resp.json()
        if not plans:
            st.info("No meal plans found for this combination.")
        else:
            for plan in plans:
                plan_label = PLAN_LABELS.get(plan["plan_type"], plan["plan_type"].replace("_", " ").title())
                st.markdown(f"### {plan_label}")
                for meal in plan["meals"]:
                    emoji = get_meal_emoji(meal)
                    st.markdown(f"{emoji} {meal}")
                st.markdown("---")
    else:
        st.error("Failed to load meal plans.")
except Exception as e:
    st.error(f"Error connecting to backend: {str(e)}")

# ── Browse All Plans ──
with st.expander("📖 Browse All Available Meal Plans"):
    try:
        resp = requests.get(f"{API_BASE_URL}/api/meal-planner/plans")
        if resp.status_code == 200:
            all_plans = resp.json()
            for plan in all_plans:
                plan_label = PLAN_LABELS.get(plan["plan_type"], plan["plan_type"].replace("_", " ").title())
                st.markdown(f"#### {plan_label}")
                for meal in plan["meals"]:
                    emoji = get_meal_emoji(meal)
                    st.markdown(f"{emoji} {meal}")
                st.markdown("---")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ── Food Database ──
st.markdown("---")
st.subheader("🥗 Food Database")
st.markdown("Browse our curated food database with nutritional information.")

col_search, col_cat, col_diet_filter = st.columns(3)
with col_search:
    search_query = st.text_input("Search Food", placeholder="e.g. Paneer, Oats...")
with col_cat:
    cat_filter = st.selectbox("Category", options=["All", "breakfast", "lunch", "dinner", "snack", "ingredient"])
with col_diet_filter:
    diet_filter = st.selectbox("Diet Filter", options=["All", "vegan", "vegetarian", "eggetarian", "nonveg"])

try:
    params = {}
    if search_query:
        params["search"] = search_query
    if cat_filter != "All":
        params["category"] = cat_filter
    if diet_filter != "All":
        params["diet"] = diet_filter

    resp = requests.get(f"{API_BASE_URL}/api/meal-planner/foods", params=params)
    if resp.status_code == 200:
        foods = resp.json()
        if foods:
            df = pd.DataFrame(foods)
            df = df[["name", "category", "diet", "serving", "calories", "protein", "carbs", "fat"]]
            df.columns = ["Food", "Category", "Diet", "Serving", "Calories", "Protein (g)", "Carbs (g)", "Fat (g)"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No foods found matching your filters.")
    else:
        st.error("Failed to load food database.")
except Exception as e:
    st.error(f"Error connecting to backend: {str(e)}")
