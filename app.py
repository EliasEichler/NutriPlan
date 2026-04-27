"""
app.py — NutriPlan Pro
Smart Meal Planner · Pantry Manager · Grocery Assistant · Nutrition Tracker

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import csv
import io

import database as db
import seed_data as sd

# ─────────────────────────────────────────────────────────────────────────────
#  App configuration
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NutriPlan Pro",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CSS theming
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Global font & background ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a2e1a 0%, #0d1f0d 100%);
    color: white;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 6px 0; }
[data-testid="stSidebar"] .stRadio label:hover { color: #7ec850 !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #f7fdf3;
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid #3d8b37;
}
[data-testid="stMetricValue"] { font-weight: 700; font-size: 26px; color: #1a2e1a; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #3d8b37, #5cb85c);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.4rem 1rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2d6b28, #4a9e4a);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(61,139,55,0.3);
}

/* ── Cards / containers ── */
.recipe-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-left: 5px solid #3d8b37;
    transition: box-shadow 0.2s;
}
.recipe-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.12); }

.alert-warning {
    background: #fff8e1;
    border-radius: 10px;
    padding: 14px 18px;
    border-left: 4px solid #f5c518;
    margin: 6px 0;
}
.alert-danger {
    background: #fff0f0;
    border-radius: 10px;
    padding: 14px 18px;
    border-left: 4px solid #e74c3c;
    margin: 6px 0;
}
.alert-success {
    background: #f0fff4;
    border-radius: 10px;
    padding: 14px 18px;
    border-left: 4px solid #3d8b37;
    margin: 6px 0;
}
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px;
}
.tag-vegetarian  { background:#d4edda; color:#155724; }
.tag-vegan       { background:#d1f0e0; color:#0a4a2a; }
.tag-gluten-free { background:#fce8b2; color:#6b4700; }
.tag-dairy-free  { background:#d6eaff; color:#0d3b6b; }

.match-bar-bg {
    background: #e0e0e0; border-radius: 10px; height: 10px; margin-top: 4px;
}
.match-bar-fill {
    border-radius: 10px; height: 10px;
}

/* ── Meal plan calendar ── */
.meal-slot {
    background: #f7fdf3;
    border: 2px dashed #b5d9a8;
    border-radius: 10px;
    padding: 8px;
    min-height: 60px;
    text-align: center;
}
.meal-slot-filled {
    background: #e8f5e2;
    border: 2px solid #3d8b37;
    border-radius: 10px;
    padding: 8px;
}

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #1a2e1a 0%, #3d8b37 100%);
    color: white;
    padding: 24px 28px;
    border-radius: 16px;
    margin-bottom: 24px;
}
.page-header h1 { color: white !important; margin: 0; font-size: 28px; }
.page-header p  { color: rgba(255,255,255,0.8) !important; margin: 4px 0 0 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Initialise DB on first run
# ─────────────────────────────────────────────────────────────────────────────

db.init_db()
sd.seed_database()


# ─────────────────────────────────────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def tag_html(tag: str) -> str:
    css = {"vegetarian": "tag-vegetarian", "vegan": "tag-vegan",
           "gluten-free": "tag-gluten-free", "dairy-free": "tag-dairy-free"}
    cls = css.get(tag, "tag-vegetarian")
    return f'<span class="tag {cls}">{tag}</span>'


def match_color(score: int) -> str:
    if score >= 80: return "#3d8b37"
    if score >= 50: return "#f5c518"
    return "#e74c3c"


def difficulty_color(d: str) -> str:
    return {"Easy": "#3d8b37", "Medium": "#f5a623", "Hard": "#e74c3c"}.get(d, "#888")


def get_week_dates(start: date) -> list[date]:
    return [start + timedelta(days=i) for i in range(7)]


MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]
CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snack"]
LOCATIONS  = ["Fridge", "Freezer", "Pantry", "Counter", "Cellar"]


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar navigation
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🥗 NutriPlan Pro")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Dashboard",
         "🥑 My Pantry",
         "🍳 Recipes",
         "📅 Meal Planner",
         "🛒 Grocery List",
         "📊 Analytics",
         "⚙️ Settings"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Quick expiry alerts in sidebar
    expiring = db.get_expiring_soon(days=3)
    if expiring:
        st.markdown(f"⚠️ **{len(expiring)} item(s) expiring soon!**")
        for item in expiring[:3]:
            st.markdown(f"  🔴 {item['name']} ({item['expiry_date']})")

    prefs = db.get_preferences()
    st.markdown("---")
    st.markdown(f"💰 Weekly budget: **€{prefs.get('weekly_budget', 80):.0f}**")
    st.markdown(f"👥 Household: **{prefs.get('household_size', 2)} people**")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: Dashboard
# ─────────────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown("""
    <div class="page-header">
        <h1>🏠 Dashboard</h1>
        <p>Your daily meal planning command centre</p>
    </div>
    """, unsafe_allow_html=True)

    today      = date.today()
    week_start = today - timedelta(days=today.weekday())
    prefs      = db.get_preferences()
    pantry     = db.get_pantry()
    expiring   = db.get_expiring_soon(days=3)
    recipes    = db.get_all_recipes()
    week_plan  = db.get_meal_plan_week(week_start.isoformat())

    # ── KPI row ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧊 Pantry Items", len(pantry))
    with col2:
        st.metric("🍽️ Recipes Available", len(recipes))
    with col3:
        meals_this_week = len(week_plan)
        st.metric("📅 Meals Planned", f"{meals_this_week} / 21")
    with col4:
        st.metric("⚠️ Expiring Soon", len(expiring))

    st.markdown("---")

    col_left, col_right = st.columns([1.6, 1])

    # ── Today's meals ──
    with col_left:
        st.subheader(f"📆 Today's Meals — {today.strftime('%A, %d %B %Y')}")
        today_meals = [m for m in week_plan if m["plan_date"] == today.isoformat()]
        if today_meals:
            for meal in today_meals:
                with st.container():
                    st.markdown(f"""
                    <div class="recipe-card">
                        <strong>{meal['image_emoji']} {meal['recipe_name']}</strong>
                        &nbsp;&nbsp;<span style="color:#888">{meal['meal_type']}</span><br>
                        <small>⏱ {(meal['prep_time'] or 0) + (meal['cook_time'] or 0)} min
                        &nbsp;|&nbsp; 🔥 {(meal['calories'] or 0) * meal['servings']} kcal
                        &nbsp;|&nbsp; 💪 {(meal['protein'] or 0) * meal['servings']:.0f}g protein</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-warning">
            📋 No meals planned for today.
            Head to the <strong>Meal Planner</strong> to add some!
            </div>
            """, unsafe_allow_html=True)

        # ── Nutrition summary for today ──
        if today_meals:
            st.subheader("🔥 Today's Nutrition")
            total_cal  = sum((m["calories"] or 0) * m["servings"] for m in today_meals)
            total_pro  = sum((m["protein"]  or 0) * m["servings"] for m in today_meals)
            total_carb = sum((m["carbs"]    or 0) * m["servings"] for m in today_meals)
            total_fat  = sum((m["fat"]      or 0) * m["servings"] for m in today_meals)

            goals = {"Calories": (total_cal, prefs.get("daily_calories", 2000)),
                     "Protein":  (total_pro, prefs.get("daily_protein", 150)),
                     "Carbs":    (total_carb, prefs.get("daily_carbs", 250)),
                     "Fat":      (total_fat, prefs.get("daily_fat", 65))}

            for macro, (val, goal) in goals.items():
                pct = min(val / goal * 100, 100) if goal > 0 else 0
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    color = "#3d8b37" if pct >= 60 else "#f5a623"
                    st.markdown(f"""
                    <small><b>{macro}</b> {val:.0f} / {goal:.0f}</small>
                    <div class="match-bar-bg">
                        <div class="match-bar-fill" style="width:{pct:.0f}%;
                             background:{color}"></div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"<small style='color:#888'>{pct:.0f}%</small>",
                                unsafe_allow_html=True)

    # ── Right column ──
    with col_right:
        # Expiring items
        st.subheader("⚠️ Expiring Soon")
        if expiring:
            for item in expiring:
                days_left = (date.fromisoformat(item["expiry_date"]) - today).days
                severity = "alert-danger" if days_left <= 1 else "alert-warning"
                st.markdown(f"""
                <div class="{severity}">
                    <b>{item['name']}</b> — {item['quantity']:.0f}{item['unit']}<br>
                    <small>Expires: {item['expiry_date']}
                    {'🔴' if days_left <= 1 else '🟡'} ({days_left}d left)</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">✅ Nothing expiring in the next 3 days!</div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Top recipe matches
        st.subheader("🌟 Best Recipe Matches")
        scored = []
        for recipe in recipes[:30]:
            match = db.get_recipe_match_score(recipe["id"])
            scored.append((recipe, match["score"]))
        scored.sort(key=lambda x: x[1], reverse=True)
        for recipe, score in scored[:5]:
            color = match_color(score)
            st.markdown(f"""
            <div style="margin:6px 0; padding:10px 14px; background:#f9f9f9;
                        border-radius:8px; border-left:3px solid {color}">
                <b>{recipe['image_emoji']} {recipe['name']}</b><br>
                <small>Match: <b style="color:{color}">{score}%</b>
                &nbsp;|&nbsp; {recipe['category']}
                &nbsp;|&nbsp; ⏱ {recipe['prep_time']+recipe['cook_time']}min</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        # Waste tip
        st.subheader("♻️ Waste Reduction Tip")
        if expiring:
            names = ", ".join(e["name"] for e in expiring[:3])
            st.info(f"💡 Use **{names}** before they expire. "
                    f"Check Recipes for meals using these ingredients!")
        else:
            st.success("🌿 Great job! No waste risk right now. "
                       "Check back after your next shopping trip.")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: My Pantry
# ─────────────────────────────────────────────────────────────────────────────

def page_pantry():
    st.markdown("""
    <div class="page-header">
        <h1>🥑 My Pantry</h1>
        <p>Track your ingredients, expiry dates, and stock levels</p>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_waste = st.tabs(
        ["📋 Current Pantry", "➕ Add Item", "♻️ Log Waste"]
    )

    # ── View / Edit pantry ──
    with tab_view:
        pantry = db.get_pantry()
        if not pantry:
            st.info("Your pantry is empty! Add items in the **Add Item** tab.")
            return

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            categories = sorted({p["category"] for p in pantry})
            cat_filter = st.selectbox("Filter by Category",
                                      ["All"] + categories, key="pantry_cat")
        with col2:
            loc_filter = st.selectbox("Filter by Location",
                                      ["All"] + LOCATIONS, key="pantry_loc")
        with col3:
            expiry_filter = st.checkbox("⚠️ Show expiring only (≤5 days)", key="pf_exp")

        today_str = date.today().isoformat()

        # Apply filters
        filtered = pantry
        if cat_filter != "All":
            filtered = [p for p in filtered if p["category"] == cat_filter]
        if loc_filter != "All":
            filtered = [p for p in filtered if p["location"] == loc_filter]
        if expiry_filter:
            cutoff = (date.today() + timedelta(days=5)).isoformat()
            filtered = [p for p in filtered
                        if p["expiry_date"] and p["expiry_date"] <= cutoff]

        st.markdown(f"**{len(filtered)}** item(s) shown")

        if not filtered:
            st.info("No items match your filters.")
            return

        # Group by category
        by_cat: dict[str, list] = {}
        for item in filtered:
            by_cat.setdefault(item["category"], []).append(item)

        for cat, items in sorted(by_cat.items()):
            with st.expander(f"**{cat}** ({len(items)} items)", expanded=True):
                for item in items:
                    days_left = None
                    exp_text  = "—"
                    color     = "#888"
                    if item["expiry_date"]:
                        dl = (date.fromisoformat(item["expiry_date"]) - date.today()).days
                        days_left = dl
                        exp_text  = item["expiry_date"]
                        color = "#e74c3c" if dl <= 1 else "#f5a623" if dl <= 3 else "#3d8b37"

                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
                    with c1:
                        st.markdown(f"**{item['name']}**  "
                                    f"<small style='color:#888'>{item['location']}</small>",
                                    unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"{item['quantity']:.1f} {item['unit']}")
                    with c3:
                        label = (f"🔴 {days_left}d" if days_left is not None and days_left <= 1
                                 else f"🟡 {days_left}d" if days_left is not None and days_left <= 3
                                 else f"✅ {exp_text}" if exp_text != "—" else "—")
                        st.markdown(f"<span style='color:{color}'>{label}</span>",
                                    unsafe_allow_html=True)
                    with c4:
                        if st.button("✏️ Edit", key=f"edit_{item['id']}"):
                            st.session_state["editing_pantry"] = item["id"]
                    with c5:
                        if st.button("🗑️ Remove", key=f"del_{item['id']}"):
                            db.delete_pantry_item(item["id"])
                            st.success(f"Removed {item['name']}")
                            st.rerun()

                    # Inline edit form
                    if st.session_state.get("editing_pantry") == item["id"]:
                        with st.form(key=f"editform_{item['id']}"):
                            eq = st.number_input("Quantity", value=float(item["quantity"]),
                                                 min_value=0.0, step=0.5)
                            ee = st.date_input("Expiry date",
                                               value=(date.fromisoformat(item["expiry_date"])
                                                      if item["expiry_date"] else date.today()))
                            el = st.selectbox("Location", LOCATIONS,
                                              index=LOCATIONS.index(item["location"])
                                              if item["location"] in LOCATIONS else 0)
                            en = st.text_input("Notes", value=item["notes"] or "")
                            if st.form_submit_button("💾 Save Changes"):
                                db.update_pantry_item(item["id"], eq,
                                                      ee.isoformat(), el, en)
                                del st.session_state["editing_pantry"]
                                st.rerun()

        # Pantry summary chart
        st.markdown("---")
        st.subheader("📊 Pantry Overview")
        cat_counts = {cat: len(items) for cat, items in by_cat.items()}
        fig = px.pie(values=list(cat_counts.values()),
                     names=list(cat_counts.keys()),
                     color_discrete_sequence=px.colors.qualitative.Set3,
                     hole=0.4)
        fig.update_layout(margin=dict(l=0,r=0,t=20,b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

    # ── Add new item ──
    with tab_add:
        st.subheader("Add New Pantry Item")
        ingredients = db.get_all_ingredients()
        ing_names = [i["name"] for i in ingredients]

        with st.form("add_pantry_form"):
            col1, col2 = st.columns(2)
            with col1:
                ing_name = st.selectbox("Ingredient", ing_names)
                quantity = st.number_input("Quantity", min_value=0.1, value=100.0, step=10.0)
            with col2:
                expiry = st.date_input("Expiry Date (optional)",
                                       value=date.today() + timedelta(days=7))
                use_expiry = st.checkbox("Set expiry date", value=True)

            col3, col4 = st.columns(2)
            with col3:
                location = st.selectbox("Storage Location", LOCATIONS)
            with col4:
                notes = st.text_input("Notes (optional)", "")

            submitted = st.form_submit_button("➕ Add to Pantry")
            if submitted:
                selected_ing = next(i for i in ingredients if i["name"] == ing_name)
                db.add_pantry_item(
                    selected_ing["id"], quantity, selected_ing["unit"],
                    expiry.isoformat() if use_expiry else None,
                    location, notes
                )
                st.success(f"✅ Added {quantity} {selected_ing['unit']} of **{ing_name}** to your pantry!")
                st.rerun()

    # ── Waste log ──
    with tab_waste:
        st.subheader("♻️ Log Wasted Food")
        st.markdown("Track waste to understand your habits and reduce food loss over time.")
        pantry_items = db.get_pantry()
        if not pantry_items:
            st.info("Add pantry items first.")
        else:
            with st.form("waste_form"):
                col1, col2 = st.columns(2)
                with col1:
                    waste_name = st.selectbox("Ingredient",
                                              [p["name"] for p in pantry_items])
                    waste_qty = st.number_input("Quantity Wasted",
                                                min_value=0.1, value=50.0)
                with col2:
                    waste_reason = st.selectbox("Reason",
                        ["Expired", "Spoiled", "Over-cooked", "Disliked", "Other"])
                submitted = st.form_submit_button("🗑️ Log Waste")
                if submitted:
                    item = next(p for p in pantry_items if p["name"] == waste_name)
                    cost = waste_qty * item["price_per_unit"]
                    db.log_waste(item["ingredient_id"], waste_qty,
                                 item["unit"], waste_reason, cost)
                    st.success(f"Logged {waste_qty} {item['unit']} of {waste_name} "
                               f"(~€{cost:.2f} wasted)")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: Recipes
# ─────────────────────────────────────────────────────────────────────────────

def page_recipes():
    st.markdown("""
    <div class="page-header">
        <h1>🍳 Recipe Library</h1>
        <p>Browse recipes and discover what you can cook with your pantry</p>
    </div>
    """, unsafe_allow_html=True)

    recipes = db.get_all_recipes()

    # ── Filters ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("🔍 Search recipes", "")
    with col2:
        cat_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with col3:
        diff_filter = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    with col4:
        diet_options = ["All", "vegetarian", "vegan", "gluten-free", "dairy-free"]
        diet_filter = st.selectbox("Dietary", diet_options)

    match_only = st.checkbox("✨ Show only recipes I can make (≥50% match)", value=False)

    # ── Apply filters ──
    filtered = recipes
    if search:
        filtered = [r for r in filtered
                    if search.lower() in r["name"].lower()
                    or search.lower() in r["description"].lower()]
    if cat_filter != "All":
        filtered = [r for r in filtered if r["category"] == cat_filter]
    if diff_filter != "All":
        filtered = [r for r in filtered if r["difficulty"] == diff_filter]
    if diet_filter != "All":
        filtered = [r for r in filtered
                    if diet_filter in (r["dietary_tags"] or "").split(",")]

    # Add match scores
    scored = []
    for r in filtered:
        match = db.get_recipe_match_score(r["id"])
        scored.append((r, match))

    if match_only:
        scored = [(r, m) for r, m in scored if m["score"] >= 50]

    scored.sort(key=lambda x: x[1]["score"], reverse=True)
    st.markdown(f"**{len(scored)}** recipe(s) found")

    # ── Recipe grid ──
    cols_per_row = 2
    for i in range(0, len(scored), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(scored):
                break
            recipe, match = scored[idx]
            score  = match["score"]
            color  = match_color(score)
            tags   = [t for t in (recipe["dietary_tags"] or "").split(",") if t]
            tags_html = " ".join(tag_html(t) for t in tags)
            d_color = difficulty_color(recipe["difficulty"])

            with col:
                with st.container():
                    st.markdown(f"""
                    <div class="recipe-card">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <span style="font-size:2rem">{recipe['image_emoji']}</span>
                            <span style="font-size:12px;font-weight:700;color:{color};
                                  background:{color}18;padding:4px 10px;border-radius:20px">
                                🎯 {score}% match
                            </span>
                        </div>
                        <h4 style="margin:8px 0 4px">{recipe['name']}</h4>
                        <p style="color:#666;font-size:13px;margin:0 0 8px">{recipe['description']}</p>
                        <div style="font-size:12px;color:#888;margin-bottom:8px">
                            ⏱ {recipe['prep_time']+recipe['cook_time']} min &nbsp;|&nbsp;
                            👥 {recipe['servings']} servings &nbsp;|&nbsp;
                            <span style="color:{d_color};font-weight:600">{recipe['difficulty']}</span>
                        </div>
                        <div style="font-size:12px;margin-bottom:8px">
                            🔥 {recipe['calories']} kcal &nbsp;|&nbsp;
                            💪 {recipe['protein']}g protein &nbsp;|&nbsp;
                            🌾 {recipe['carbs']}g carbs
                        </div>
                        <div>{tags_html}</div>
                        <div class="match-bar-bg" style="margin-top:10px">
                            <div class="match-bar-fill"
                                 style="width:{score}%;background:{color}"></div>
                        </div>
                        <div style="font-size:11px;color:#888;margin-top:3px">
                            {len(match['available'])}/{len(match['available'])+len(match['missing'])} ingredients in pantry
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("📖 See full recipe & ingredients"):
                        sub1, sub2 = st.tabs(["📝 Instructions", "🛒 Ingredients"])
                        with sub1:
                            st.markdown(recipe["instructions"])
                        with sub2:
                            if match["available"]:
                                st.markdown("**✅ In your pantry:**")
                                for ing in match["available"]:
                                    st.markdown(f"  - {ing['name']}: {ing['quantity']} {ing['unit']}")
                            if match["missing"]:
                                st.markdown("**❌ You need to buy:**")
                                for ing in match["missing"]:
                                    est = ing["quantity"] * ing["price_per_unit"]
                                    st.markdown(
                                        f"  - {ing['name']}: {ing['quantity']} {ing['unit']}"
                                        f" (~€{est:.2f})"
                                    )


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: Meal Planner
# ─────────────────────────────────────────────────────────────────────────────

def page_meal_planner():
    st.markdown("""
    <div class="page-header">
        <h1>📅 Meal Planner</h1>
        <p>Plan your weekly meals and track nutritional balance</p>
    </div>
    """, unsafe_allow_html=True)

    # Week navigation
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    col_prev, col_week, col_next = st.columns([1, 4, 1])
    with col_prev:
        if st.button("◀ Prev"):
            st.session_state.week_offset -= 1
    with col_next:
        if st.button("Next ▶"):
            st.session_state.week_offset += 1
    with col_week:
        today      = date.today()
        week_start = today - timedelta(days=today.weekday()) \
                     + timedelta(weeks=st.session_state.week_offset)
        week_end   = week_start + timedelta(days=6)
        st.markdown(f"### 📆 {week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')}")

    week_dates = get_week_dates(week_start)
    plan       = db.get_meal_plan_week(week_start.isoformat())

    # Build a lookup: {(date_str, meal_type): [entries]}
    plan_map: dict[tuple, list] = {}
    for entry in plan:
        key = (entry["plan_date"], entry["meal_type"])
        plan_map.setdefault(key, []).append(entry)

    recipes    = db.get_all_recipes()
    recipe_map = {r["name"]: r["id"] for r in recipes}

    # ── Calendar grid ──
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_cols = st.columns([1.2] + [1] * 7)
    header_cols[0].markdown("**Meal**")
    for i, (d, dn) in enumerate(zip(week_dates, day_names)):
        is_today = d == date.today()
        label = f"**{'📍 ' if is_today else ''}{dn}**\n{d.strftime('%d/%m')}"
        header_cols[i + 1].markdown(label)

    for meal_type in MEAL_TYPES:
        cols = st.columns([1.2] + [1] * 7)
        mt_emoji = {"Breakfast": "🌅", "Lunch": "☀️",
                    "Dinner": "🌙", "Snack": "🍎"}.get(meal_type, "🍽️")
        cols[0].markdown(f"**{mt_emoji} {meal_type}**")

        for i, d in enumerate(week_dates):
            key     = (d.isoformat(), meal_type)
            entries = plan_map.get(key, [])
            with cols[i + 1]:
                if entries:
                    for entry in entries:
                        st.markdown(f"""
                        <div class="meal-slot-filled">
                            <small>{entry['image_emoji']}<br>
                            <b>{entry['recipe_name'][:18]}...</b><br>
                            🔥{(entry['calories'] or 0)*entry['servings']} kcal</small>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("✕", key=f"del_mp_{entry['id']}",
                                     help="Remove this meal"):
                            db.delete_meal_plan(entry["id"])
                            st.rerun()
                else:
                    st.markdown("""
                    <div class="meal-slot">
                        <small style="color:#aaa">—</small>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Add meal form ──
    col_form, col_nutri = st.columns([1.2, 1])

    with col_form:
        st.subheader("➕ Add a Meal")
        with st.form("add_meal_form"):
            col1, col2 = st.columns(2)
            with col1:
                meal_date = st.date_input("Date", value=date.today(),
                                          min_value=week_start, max_value=week_end)
                meal_type = st.selectbox("Meal Type", MEAL_TYPES)
            with col2:
                recipe_name = st.selectbox("Recipe", [r["name"] for r in recipes])
                servings    = st.number_input("Servings", min_value=1,
                                              max_value=10, value=1)
            notes = st.text_input("Notes (optional)", "")

            if st.form_submit_button("📌 Add to Plan"):
                r_id = recipe_map[recipe_name]
                db.add_meal_plan(meal_date.isoformat(), meal_type,
                                 r_id, servings, notes)
                st.success(f"✅ Added {recipe_name} on {meal_date.strftime('%A')}!")
                st.rerun()

    # ── Weekly nutrition summary ──
    with col_nutri:
        st.subheader("📊 Weekly Nutrition")
        nutrition = db.get_weekly_nutrition(week_start.isoformat())
        totals    = nutrition["totals"]
        daily     = nutrition["daily"]
        prefs     = db.get_preferences()

        if daily:
            days_with_data = list(daily.keys())
            fig = go.Figure()
            macros = {
                "Calories": ("calories", "#FF6B6B"),
                "Protein":  ("protein",  "#4ECDC4"),
                "Carbs":    ("carbs",    "#45B7D1"),
                "Fat":      ("fat",      "#96CEB4"),
            }
            for macro, (key, color) in macros.items():
                y_vals = [daily.get(d, {}).get(key, 0)
                          for d in [dd.isoformat() for dd in week_dates]]
                fig.add_trace(go.Bar(
                    name=macro,
                    x=[dd.strftime("%a") for dd in week_dates],
                    y=y_vals,
                    marker_color=color,
                    opacity=0.8,
                ))
            fig.update_layout(
                barmode="group",
                legend=dict(orientation="h", y=-0.2),
                margin=dict(l=0, r=0, t=10, b=60),
                height=300,
                plot_bgcolor="white",
                yaxis=dict(title="Amount"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Week totals vs goals
            days_planned = len(days_with_data)
            if days_planned:
                st.markdown(f"**Total this week ({days_planned} days planned):**")
                c1, c2 = st.columns(2)
                c1.metric("🔥 Calories", f"{totals['calories']:.0f} kcal",
                          delta=f"Goal: {prefs.get('daily_calories',2000)*7:.0f}")
                c2.metric("💪 Protein", f"{totals['protein']:.0f}g",
                          delta=f"Goal: {prefs.get('daily_protein',150)*7:.0f}g")
        else:
            st.info("Plan some meals to see your nutrition breakdown.")

    # ── Auto-generate grocery list button ──
    st.markdown("---")
    st.subheader("🛒 Generate Grocery List")
    st.markdown("Auto-generates a list of what you need to buy based on your meal plan "
                "minus what's already in your pantry.")
    col_gen1, col_gen2 = st.columns(2)
    with col_gen1:
        budget = st.number_input("Your shopping budget (€)",
                                 value=float(db.get_preferences().get("weekly_budget", 80)),
                                 min_value=0.0, step=5.0)
    with col_gen2:
        if st.button("🛒 Generate Smart Grocery List", use_container_width=True):
            list_id = db.generate_grocery_list_from_plan(
                week_start.isoformat(), budget
            )
            if list_id == -1:
                st.success("🎉 Your pantry covers everything! Nothing to buy.")
            else:
                items = db.get_grocery_items(list_id)
                total = sum(i["estimated_price"] for i in items)
                st.success(
                    f"✅ Generated a grocery list with **{len(items)} items** "
                    f"(~€{total:.2f}). Visit the Grocery List page to view it!"
                )


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: Grocery List
# ─────────────────────────────────────────────────────────────────────────────

def page_grocery():
    st.markdown("""
    <div class="page-header">
        <h1>🛒 Grocery List</h1>
        <p>Smart shopping lists organised by store section</p>
    </div>
    """, unsafe_allow_html=True)

    lists = db.get_grocery_lists()
    prefs = db.get_preferences()

    col_lists, col_detail = st.columns([1, 2])

    with col_lists:
        st.subheader("📋 Shopping Lists")

        # Create new list manually
        with st.expander("➕ Create New List"):
            with st.form("new_list_form"):
                list_name   = st.text_input("List name", "My Shopping List")
                list_budget = st.number_input(
                    "Budget (€)", value=float(prefs.get("weekly_budget", 80)),
                    min_value=0.0
                )
                if st.form_submit_button("Create"):
                    db.create_grocery_list(list_name, list_budget)
                    st.rerun()

        if not lists:
            st.info("No lists yet. Generate one from the Meal Planner or create one above.")
        else:
            for lst in lists:
                items = db.get_grocery_items(lst["id"])
                bought = sum(1 for i in items if i["purchased"])
                total_cost = sum(i["estimated_price"] for i in items)
                pct = int(bought / len(items) * 100) if items else 0

                with st.container():
                    st.markdown(f"""
                    <div style="background:#f8f8f8;border-radius:10px;
                                padding:12px 16px;margin:6px 0;
                                border-left:4px solid {'#3d8b37' if pct==100 else '#f5a623'}">
                        <b>{lst['name']}</b><br>
                        <small style="color:#888">{lst['created_date']} &nbsp;|&nbsp;
                        {bought}/{len(items)} bought &nbsp;|&nbsp; ~€{total_cost:.2f}</small>
                        <div class="match-bar-bg" style="margin-top:6px">
                            <div class="match-bar-fill"
                                 style="width:{pct}%;background:#3d8b37"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("👁️ View", key=f"view_lst_{lst['id']}"):
                            st.session_state["active_list"] = lst["id"]
                    with btn_col2:
                        if st.button("🗑️ Delete", key=f"del_lst_{lst['id']}"):
                            db.delete_grocery_list(lst["id"])
                            if st.session_state.get("active_list") == lst["id"]:
                                del st.session_state["active_list"]
                            st.rerun()

    # ── Detail view ──
    with col_detail:
        active_id = st.session_state.get("active_list")
        if not active_id:
            st.info("👈 Select a list on the left to view details.")
            return

        active_list = next((l for l in lists if l["id"] == active_id), None)
        if not active_list:
            return

        items = db.get_grocery_items(active_id)
        total_est = sum(i["estimated_price"] for i in items)
        bought_cost = sum(i["estimated_price"] for i in items if i["purchased"])
        budget = active_list["budget"]

        st.subheader(f"🛒 {active_list['name']}")

        # Budget bar
        pct_spent = min(bought_cost / budget * 100, 100) if budget > 0 else 0
        color = "#e74c3c" if pct_spent > 90 else "#f5a623" if pct_spent > 70 else "#3d8b37"
        st.markdown(f"""
        <div style="background:#f5f5f5;border-radius:10px;padding:14px 18px;margin-bottom:14px">
            <b>Budget: €{budget:.2f}</b> &nbsp;|&nbsp;
            Estimated: <b>€{total_est:.2f}</b> &nbsp;|&nbsp;
            In cart: <b style="color:{color}">€{bought_cost:.2f}</b>
            <div class="match-bar-bg" style="margin-top:8px;height:14px">
                <div class="match-bar-fill"
                     style="width:{pct_spent:.0f}%;background:{color};height:14px"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Export button
        if items:
            csv_data = io.StringIO()
            writer = csv.writer(csv_data)
            writer.writerow(["Item", "Category", "Quantity", "Unit", "Est. Price (€)", "Purchased"])
            for item in items:
                writer.writerow([
                    item["name"], item["category"],
                    f"{item['quantity_needed']:.1f}", item["unit"],
                    f"{item['estimated_price']:.2f}",
                    "Yes" if item["purchased"] else "No"
                ])
            st.download_button(
                "📥 Export to CSV",
                csv_data.getvalue(),
                file_name=f"{active_list['name'].replace(' ','_')}.csv",
                mime="text/csv",
            )

        # Items grouped by store category
        by_cat: dict[str, list] = {}
        for item in items:
            by_cat.setdefault(item["category"], []).append(item)

        all_checked = all(i["purchased"] for i in items) if items else False
        if all_checked and items:
            st.success("🎉 All items purchased! Great shopping trip!")

        for cat, cat_items in sorted(by_cat.items()):
            bought_in_cat = sum(1 for i in cat_items if i["purchased"])
            with st.expander(f"**{cat}** ({bought_in_cat}/{len(cat_items)})", expanded=True):
                for item in cat_items:
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        checked = st.checkbox(
                            f"{'~~' if item['purchased'] else ''}{item['name']}"
                            f"{'~~' if item['purchased'] else ''}",
                            value=bool(item["purchased"]),
                            key=f"chk_{item['id']}",
                        )
                        if checked != bool(item["purchased"]):
                            db.toggle_grocery_item(item["id"], checked)
                            st.rerun()
                    with c2:
                        st.markdown(f"{item['quantity_needed']:.1f} {item['unit']}")
                    with c3:
                        st.markdown(f"€{item['estimated_price']:.2f}")

        # Add manual item
        st.markdown("---")
        with st.expander("➕ Add item manually"):
            ingredients = db.get_all_ingredients()
            with st.form(f"add_item_{active_id}"):
                col1, col2 = st.columns(2)
                with col1:
                    man_ing = st.selectbox("Ingredient",
                                           [i["name"] for i in ingredients])
                with col2:
                    man_qty = st.number_input("Quantity", min_value=0.1, value=100.0)
                if st.form_submit_button("Add"):
                    ing = next(i for i in ingredients if i["name"] == man_ing)
                    price = man_qty * ing["price_per_unit"]
                    db.add_grocery_item(active_id, ing["id"], man_qty,
                                        ing["unit"], price, "manual")
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: Analytics
# ─────────────────────────────────────────────────────────────────────────────

def page_analytics():
    st.markdown("""
    <div class="page-header">
        <h1>📊 Analytics</h1>
        <p>Budget tracking, nutrition trends and waste insights</p>
    </div>
    """, unsafe_allow_html=True)

    tab_budget, tab_nutrition, tab_waste = st.tabs(
        ["💰 Budget", "🥦 Nutrition", "♻️ Waste"]
    )

    prefs = db.get_preferences()

    # ── Budget tab ──
    with tab_budget:
        st.subheader("💰 Weekly Budget Analysis")
        lists = db.get_grocery_lists()

        if not lists:
            st.info("No grocery lists yet. Create one to track spending.")
        else:
            # Build spending data per list
            list_names, budgets, spents = [], [], []
            for lst in lists[:8]:  # last 8 lists
                items   = db.get_grocery_items(lst["id"])
                spent   = sum(i["estimated_price"] for i in items)
                budgets.append(lst["budget"])
                spents.append(spent)
                list_names.append(lst["name"][:20])

            fig_b = go.Figure()
            fig_b.add_trace(go.Bar(name="Budget", x=list_names,
                                   y=budgets, marker_color="#3d8b37", opacity=0.7))
            fig_b.add_trace(go.Bar(name="Estimated Cost", x=list_names,
                                   y=spents, marker_color="#FF6B6B", opacity=0.8))
            fig_b.update_layout(
                barmode="group", legend=dict(orientation="h"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=350, plot_bgcolor="white",
            )
            st.plotly_chart(fig_b, use_container_width=True)

            # Category breakdown for latest list
            latest_list = lists[0]
            items = db.get_grocery_items(latest_list["id"])
            if items:
                st.subheader(f"📦 Spending Breakdown — {latest_list['name']}")
                by_cat = {}
                for item in items:
                    by_cat.setdefault(item["category"], 0)
                    by_cat[item["category"]] += item["estimated_price"]

                fig_pie = px.pie(
                    values=list(by_cat.values()),
                    names=list(by_cat.keys()),
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    hole=0.45,
                )
                fig_pie.update_layout(margin=dict(l=0,r=0,t=20,b=0), height=320)
                st.plotly_chart(fig_pie, use_container_width=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            total_budget = sum(budgets)
            total_spent  = sum(spents)
            savings      = total_budget - total_spent
            with col1:
                st.metric("Total Budgeted", f"€{total_budget:.2f}")
            with col2:
                st.metric("Total Estimated Cost", f"€{total_spent:.2f}")
            with col3:
                st.metric("Estimated Savings", f"€{savings:.2f}",
                          delta="under budget" if savings >= 0 else "over budget",
                          delta_color="normal" if savings >= 0 else "inverse")

    # ── Nutrition tab ──
    with tab_nutrition:
        st.subheader("🥦 Nutritional Trends")

        # Multi-week overview
        weeks_data = []
        for offset in range(-3, 1):  # Last 4 weeks
            today = date.today()
            ws = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
            nut = db.get_weekly_nutrition(ws.isoformat())
            if nut["totals"]["calories"] > 0:
                weeks_data.append({
                    "week": ws.strftime("%d %b"),
                    **nut["totals"]
                })

        if weeks_data:
            df = pd.DataFrame(weeks_data)
            fig_n = go.Figure()
            macro_colors = {"calories": "#FF6B6B", "protein": "#4ECDC4",
                            "carbs": "#45B7D1", "fat": "#96CEB4"}
            for macro, color in macro_colors.items():
                if macro in df.columns:
                    fig_n.add_trace(go.Scatter(
                        x=df["week"], y=df[macro],
                        mode="lines+markers",
                        name=macro.capitalize(),
                        line=dict(color=color, width=2),
                        marker=dict(size=8),
                    ))
            fig_n.update_layout(
                legend=dict(orientation="h"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=320, plot_bgcolor="white",
            )
            st.plotly_chart(fig_n, use_container_width=True)

            # Current week vs goals
            st.subheader("🎯 Current Week vs. Daily Goals")
            today  = date.today()
            ws     = today - timedelta(days=today.weekday())
            weekly = db.get_weekly_nutrition(ws.isoformat())
            daily  = weekly["daily"]
            days   = len(daily) if daily else 1

            goals  = {
                "Calories (kcal)": (
                    weekly["totals"]["calories"] / days,
                    prefs.get("daily_calories", 2000)
                ),
                "Protein (g)": (
                    weekly["totals"]["protein"] / days,
                    prefs.get("daily_protein", 150)
                ),
                "Carbs (g)": (
                    weekly["totals"]["carbs"] / days,
                    prefs.get("daily_carbs", 250)
                ),
                "Fat (g)": (
                    weekly["totals"]["fat"] / days,
                    prefs.get("daily_fat", 65)
                ),
            }

            for macro, (actual, goal) in goals.items():
                pct = min(actual / goal * 100, 130) if goal > 0 else 0
                color = "#3d8b37" if 80 <= pct <= 110 else "#f5a623"
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.markdown(f"""
                    <b>{macro}</b> — avg {actual:.0f} / goal {goal:.0f}<br>
                    <div class="match-bar-bg">
                        <div class="match-bar-fill"
                             style="width:{min(pct,100):.0f}%;background:{color}"></div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"**{pct:.0f}%**")
                with col_c:
                    status = ("✅" if 80 <= pct <= 110
                              else "⬇️ Low" if pct < 80 else "⬆️ High")
                    st.markdown(status)
        else:
            st.info("Plan meals across multiple weeks to see trends.")

    # ── Waste tab ──
    with tab_waste:
        st.subheader("♻️ Food Waste Analysis")
        waste = db.get_waste_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("💸 Total Value Wasted", f"€{waste['total_wasted']:.2f}")
        with col2:
            by_reason = waste["by_reason"]
            if by_reason:
                top_reason = max(by_reason, key=lambda x: x["total_cost"] or 0)
                st.metric("🏆 Top Waste Reason",
                          top_reason["reason"] if top_reason else "—")

        if by_reason:
            fig_w = px.bar(
                x=[r["reason"] for r in by_reason],
                y=[r["total_cost"] or 0 for r in by_reason],
                labels={"x": "Reason", "y": "Wasted Value (€)"},
                color_discrete_sequence=["#e74c3c"],
            )
            fig_w.update_layout(
                margin=dict(l=0, r=0, t=20, b=0),
                height=300, plot_bgcolor="white",
            )
            st.plotly_chart(fig_w, use_container_width=True)

            # Practical advice
            st.markdown("---")
            st.subheader("💡 Waste Reduction Tips")
            tips = [
                "🛒 **Buy less, more often** — smaller, frequent shops reduce spoilage.",
                "📅 **Check expiry dates** weekly and plan meals around expiring items.",
                "❄️ **Freeze before it expires** — most ingredients freeze well.",
                "📝 **Stick to your meal plan** — unplanned meals cause pantry waste.",
                "🍲 **Make soup** — almost any combination of vegetables works in soup!",
            ]
            for tip in tips:
                st.markdown(tip)
        else:
            st.success("🌱 No waste logged yet — keep it up!")
            st.markdown("Use the **Pantry → Log Waste** tab to track food you throw away.")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE: Settings
# ─────────────────────────────────────────────────────────────────────────────

def page_settings():
    st.markdown("""
    <div class="page-header">
        <h1>⚙️ Settings & Profile</h1>
        <p>Configure your nutritional goals, dietary restrictions and budget</p>
    </div>
    """, unsafe_allow_html=True)

    prefs = db.get_preferences()

    st.subheader("👤 Household & Budget")
    with st.form("settings_form"):
        col1, col2 = st.columns(2)
        with col1:
            household = st.number_input(
                "Household size (people)",
                min_value=1, max_value=20,
                value=prefs.get("household_size", 2)
            )
            weekly_budget = st.number_input(
                "Weekly food budget (€)",
                min_value=0.0, step=5.0,
                value=float(prefs.get("weekly_budget", 80))
            )
        with col2:
            diet_options = ["None", "vegetarian", "vegan", "gluten-free", "dairy-free"]
            curr_diet = prefs.get("dietary_restrictions", "")
            diet_restriction = st.multiselect(
                "Dietary Restrictions",
                diet_options[1:],
                default=[d for d in curr_diet.split(",") if d in diet_options]
            )

        st.subheader("🎯 Daily Nutrition Goals")
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            cal_goal = st.number_input(
                "Calories (kcal)", min_value=1000, max_value=5000, step=100,
                value=int(prefs.get("daily_calories", 2000))
            )
        with col4:
            pro_goal = st.number_input(
                "Protein (g)", min_value=20, max_value=500, step=10,
                value=int(prefs.get("daily_protein", 150))
            )
        with col5:
            carb_goal = st.number_input(
                "Carbs (g)", min_value=50, max_value=700, step=10,
                value=int(prefs.get("daily_carbs", 250))
            )
        with col6:
            fat_goal = st.number_input(
                "Fat (g)", min_value=10, max_value=300, step=5,
                value=int(prefs.get("daily_fat", 65))
            )

        if st.form_submit_button("💾 Save Settings"):
            db.update_preferences(
                weekly_budget, cal_goal, pro_goal, carb_goal, fat_goal,
                ",".join(diet_restriction), household
            )
            st.success("✅ Settings saved!")

    # Info / about
    st.markdown("---")
    st.subheader("ℹ️ About NutriPlan Pro")
    st.markdown("""
    **NutriPlan Pro** is an intelligent meal planning system designed to help households:

    - 🥑 **Reduce food waste** by matching meals to pantry inventory
    - 💰 **Save money** with smart grocery list generation and budget tracking
    - 🥦 **Eat healthier** with nutritional goal tracking and macro dashboards
    - 📅 **Plan efficiently** with a full weekly meal calendar

    **Tech stack:** Python · Streamlit · SQLite · Pandas · Plotly

    *Built as a group project for the Programming course at Nova SBE.*
    """)

    # Quick stats
    st.markdown("---")
    st.subheader("📈 Quick Database Stats")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Recipes", len(db.get_all_recipes()))
    col2.metric("Ingredients", len(db.get_all_ingredients()))
    col3.metric("Pantry Items", len(db.get_pantry()))
    col4.metric("Grocery Lists", len(db.get_grocery_lists()))


# ─────────────────────────────────────────────────────────────────────────────
#  Router
# ─────────────────────────────────────────────────────────────────────────────

if   "Dashboard"    in page: page_dashboard()
elif "Pantry"       in page: page_pantry()
elif "Recipes"      in page: page_recipes()
elif "Meal Planner" in page: page_meal_planner()
elif "Grocery"      in page: page_grocery()
elif "Analytics"    in page: page_analytics()
elif "Settings"     in page: page_settings()
