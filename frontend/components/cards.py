import streamlit as st

def render_meal_card(meal: dict):
    title = meal.get("title", "Delicious Meal")
    ready_min = meal.get("readyInMinutes", 30)
    servings = meal.get("servings", 1)
    source_url = meal.get("sourceUrl", "#")
    image_url = meal.get("image_url")
    
    cal = meal.get("calories")
    p_val = meal.get("protein")
    c_val = meal.get("carbs")
    f_val = meal.get("fat")
    
    # Nutritional badges
    nutrition_html = ""
    if cal is not None and cal > 0:
        nutrition_html = f"""
        <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 5px; justify-content: center;">
            <span style="background-color: #e8f5e9; color: #2e7d32; padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold; border: 1px solid #c8e6c9;">🔥 {cal} kcal</span>
            <span style="background-color: #e3f2fd; color: #1565c0; padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold; border: 1px solid #bbdefb;">💪 P: {p_val}</span>
            <span style="background-color: #fff3e0; color: #e65100; padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold; border: 1px solid #ffe0b2;">🍞 C: {c_val}</span>
            <span style="background-color: #ffebee; color: #c62828; padding: 3px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold; border: 1px solid #ffcdd2;">🥑 F: {f_val}</span>
        </div>
        """
    
    card_html = f"""
    <div style="
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px;
        background-color: #ffffff;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        min-height: 400px;
    ">
        <div>
            {f'<img src="{image_url}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 10px; margin-bottom: 12px;" />' if image_url else '<div style="width: 100%; height: 180px; background-color: #f1f5f9; border-radius: 10px; margin-bottom: 12px; display: flex; align-items: center; justify-content: center; color: #64748b; font-weight: 500;">No Image Available</div>'}
            <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.1em; line-height: 1.4; font-weight: 700; text-align: center;">{title}</h4>
            <div style="font-size: 0.85em; color: #64748b; margin-bottom: 10px; display: flex; justify-content: space-around;">
                <span>⏱️ {ready_min} mins</span>
                <span>🍽️ {servings} servings</span>
            </div>
            {nutrition_html}
        </div>
        <div style="margin-top: 20px; text-align: center;">
            <a href="{source_url}" target="_blank" style="
                display: block;
                background-color: #22c55e;
                color: white;
                padding: 10px 16px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 0.85em;
                transition: background-color 0.2s;
                text-align: center;
            ">
                View Full Recipe 📖
            </a>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

