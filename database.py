"""
database.py — SQLite database layer for NutriPlan Pro.
Handles all CRUD operations for every entity in the system.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "nutriplan.db")


# ─────────────────────────────────────────────
#  Connection helper
# ─────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ─────────────────────────────────────────────
#  Schema initialisation
# ─────────────────────────────────────────────

def init_db() -> None:
    """Create all tables if they don't exist yet."""
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    -- Master ingredient catalogue
    CREATE TABLE IF NOT EXISTS ingredients (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
        category    TEXT    NOT NULL DEFAULT 'Other',
        unit        TEXT    NOT NULL DEFAULT 'g',
        calories    REAL    DEFAULT 0,
        protein     REAL    DEFAULT 0,
        carbs       REAL    DEFAULT 0,
        fat         REAL    DEFAULT 0,
        price_per_unit REAL DEFAULT 0.10
    );

    -- User's current pantry
    CREATE TABLE IF NOT EXISTS pantry (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id   INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
        quantity        REAL    NOT NULL DEFAULT 0,
        unit            TEXT    NOT NULL DEFAULT 'g',
        expiry_date     TEXT,           -- ISO date string YYYY-MM-DD
        purchase_date   TEXT    NOT NULL DEFAULT (date('now')),
        location        TEXT    DEFAULT 'Fridge',
        notes           TEXT    DEFAULT ''
    );

    -- Recipe catalogue
    CREATE TABLE IF NOT EXISTS recipes (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL,
        description     TEXT    DEFAULT '',
        category        TEXT    NOT NULL DEFAULT 'Dinner',
        prep_time       INTEGER DEFAULT 10,
        cook_time       INTEGER DEFAULT 20,
        servings        INTEGER DEFAULT 2,
        difficulty      TEXT    DEFAULT 'Medium',
        dietary_tags    TEXT    DEFAULT '',   -- comma-separated: vegetarian,vegan,gluten-free
        instructions    TEXT    DEFAULT '',
        image_emoji     TEXT    DEFAULT '🍽️',
        calories        REAL    DEFAULT 0,
        protein         REAL    DEFAULT 0,
        carbs           REAL    DEFAULT 0,
        fat             REAL    DEFAULT 0,
        fiber           REAL    DEFAULT 0
    );

    -- Ingredients required per recipe
    CREATE TABLE IF NOT EXISTS recipe_ingredients (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id       INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
        ingredient_id   INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
        quantity        REAL    NOT NULL,
        unit            TEXT    NOT NULL DEFAULT 'g'
    );

    -- Weekly meal plan entries
    CREATE TABLE IF NOT EXISTS meal_plans (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_date   TEXT    NOT NULL,   -- YYYY-MM-DD
        meal_type   TEXT    NOT NULL,   -- Breakfast / Lunch / Dinner / Snack
        recipe_id   INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
        servings    INTEGER DEFAULT 1,
        notes       TEXT    DEFAULT ''
    );

    -- Grocery lists
    CREATE TABLE IF NOT EXISTS grocery_lists (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL DEFAULT 'Shopping List',
        created_date    TEXT    NOT NULL DEFAULT (date('now')),
        budget          REAL    DEFAULT 0,
        total_cost      REAL    DEFAULT 0,
        completed       INTEGER DEFAULT 0
    );

    -- Items inside a grocery list
    CREATE TABLE IF NOT EXISTS grocery_items (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        list_id         INTEGER NOT NULL REFERENCES grocery_lists(id) ON DELETE CASCADE,
        ingredient_id   INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
        quantity_needed REAL    NOT NULL,
        unit            TEXT    NOT NULL DEFAULT 'g',
        estimated_price REAL    DEFAULT 0,
        purchased       INTEGER DEFAULT 0,
        added_by        TEXT    DEFAULT 'auto'   -- 'auto' or 'manual'
    );

    -- User preferences & settings
    CREATE TABLE IF NOT EXISTS user_preferences (
        id              INTEGER PRIMARY KEY DEFAULT 1,
        weekly_budget   REAL    DEFAULT 80.0,
        daily_calories  REAL    DEFAULT 2000,
        daily_protein   REAL    DEFAULT 150,
        daily_carbs     REAL    DEFAULT 250,
        daily_fat       REAL    DEFAULT 65,
        dietary_restrictions TEXT DEFAULT '',
        household_size  INTEGER DEFAULT 2
    );

    -- Waste log — items thrown away before being used
    CREATE TABLE IF NOT EXISTS waste_log (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id   INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
        quantity_wasted REAL    NOT NULL,
        unit            TEXT    NOT NULL DEFAULT 'g',
        reason          TEXT    DEFAULT 'Expired',
        logged_date     TEXT    NOT NULL DEFAULT (date('now')),
        estimated_cost  REAL    DEFAULT 0
    );
    """)

    # Ensure default user preferences row exists
    c.execute("""
        INSERT OR IGNORE INTO user_preferences (id) VALUES (1)
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  Ingredients
# ─────────────────────────────────────────────

def get_all_ingredients() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM ingredients ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ingredient_by_name(name: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM ingredients WHERE name = ? COLLATE NOCASE", (name,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_ingredient(name, category, unit, calories, protein, carbs, fat, price) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO ingredients (name, category, unit, calories, protein, carbs, fat, price_per_unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            category=excluded.category, unit=excluded.unit,
            calories=excluded.calories, protein=excluded.protein,
            carbs=excluded.carbs, fat=excluded.fat,
            price_per_unit=excluded.price_per_unit
    """, (name, category, unit, calories, protein, carbs, fat, price))
    conn.commit()
    ing_id = c.lastrowid or conn.execute(
        "SELECT id FROM ingredients WHERE name=?", (name,)
    ).fetchone()["id"]
    conn.close()
    return ing_id


# ─────────────────────────────────────────────
#  Pantry
# ─────────────────────────────────────────────

def get_pantry() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, i.name, i.category, i.calories, i.protein, i.carbs, i.fat,
               i.price_per_unit
        FROM pantry p
        JOIN ingredients i ON p.ingredient_id = i.id
        ORDER BY p.expiry_date NULLS LAST, i.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_pantry_item(ingredient_id: int, quantity: float, unit: str,
                    expiry_date: Optional[str], location: str, notes: str) -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO pantry (ingredient_id, quantity, unit, expiry_date, location, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ingredient_id, quantity, unit, expiry_date, location, notes))
    conn.commit()
    conn.close()


def update_pantry_item(item_id: int, quantity: float, expiry_date: Optional[str],
                       location: str, notes: str) -> None:
    conn = get_connection()
    conn.execute("""
        UPDATE pantry SET quantity=?, expiry_date=?, location=?, notes=?
        WHERE id=?
    """, (quantity, expiry_date, location, notes, item_id))
    conn.commit()
    conn.close()


def delete_pantry_item(item_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM pantry WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def get_expiring_soon(days: int = 3) -> list:
    """Return pantry items expiring within `days` days."""
    cutoff = (date.today() + timedelta(days=days)).isoformat()
    today_str = date.today().isoformat()
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, i.name, i.category
        FROM pantry p
        JOIN ingredients i ON p.ingredient_id = i.id
        WHERE p.expiry_date IS NOT NULL
          AND p.expiry_date <= ?
          AND p.expiry_date >= ?
        ORDER BY p.expiry_date
    """, (cutoff, today_str)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pantry_ingredient_ids() -> set:
    conn = get_connection()
    rows = conn.execute(
        "SELECT ingredient_id FROM pantry WHERE quantity > 0"
    ).fetchall()
    conn.close()
    return {r["ingredient_id"] for r in rows}


# ─────────────────────────────────────────────
#  Recipes
# ─────────────────────────────────────────────

def get_all_recipes() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recipe_by_id(recipe_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_recipe_ingredients(recipe_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT ri.*, i.name, i.category, i.calories, i.protein, i.carbs, i.fat,
               i.price_per_unit
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE ri.recipe_id = ?
    """, (recipe_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recipe_match_score(recipe_id: int) -> dict:
    """
    Returns how many ingredients the user already has in their pantry
    as a percentage, plus lists of available / missing ingredients.
    """
    pantry_ids = get_pantry_ingredient_ids()
    recipe_ings = get_recipe_ingredients(recipe_id)

    if not recipe_ings:
        return {"score": 0, "available": [], "missing": []}

    available = [r for r in recipe_ings if r["ingredient_id"] in pantry_ids]
    missing   = [r for r in recipe_ings if r["ingredient_id"] not in pantry_ids]
    score     = round(len(available) / len(recipe_ings) * 100)
    return {"score": score, "available": available, "missing": missing}


def add_recipe(name, description, category, prep_time, cook_time, servings,
               difficulty, dietary_tags, instructions, image_emoji,
               calories, protein, carbs, fat, fiber) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO recipes
        (name, description, category, prep_time, cook_time, servings, difficulty,
         dietary_tags, instructions, image_emoji, calories, protein, carbs, fat, fiber)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (name, description, category, prep_time, cook_time, servings, difficulty,
          dietary_tags, instructions, image_emoji, calories, protein, carbs, fat, fiber))
    recipe_id = c.lastrowid
    conn.commit()
    conn.close()
    return recipe_id


def add_recipe_ingredient(recipe_id: int, ingredient_id: int,
                          quantity: float, unit: str) -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
        VALUES (?, ?, ?, ?)
    """, (recipe_id, ingredient_id, quantity, unit))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  Meal Planner
# ─────────────────────────────────────────────

def get_meal_plan_week(start_date: str) -> list:
    """Fetch all meal plan entries for a 7-day window starting at `start_date`."""
    conn = get_connection()
    end_date = (date.fromisoformat(start_date) + timedelta(days=6)).isoformat()
    rows = conn.execute("""
        SELECT mp.*, r.name AS recipe_name, r.image_emoji, r.calories,
               r.protein, r.carbs, r.fat, r.prep_time, r.cook_time, r.category
        FROM meal_plans mp
        LEFT JOIN recipes r ON mp.recipe_id = r.id
        WHERE mp.plan_date BETWEEN ? AND ?
        ORDER BY mp.plan_date, mp.meal_type
    """, (start_date, end_date)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_meal_plan(plan_date: str, meal_type: str,
                  recipe_id: int, servings: int = 1, notes: str = "") -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO meal_plans (plan_date, meal_type, recipe_id, servings, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (plan_date, meal_type, recipe_id, servings, notes))
    conn.commit()
    conn.close()


def delete_meal_plan(entry_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM meal_plans WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  Grocery Lists
# ─────────────────────────────────────────────

def create_grocery_list(name: str, budget: float) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO grocery_lists (name, budget, created_date)
        VALUES (?, ?, date('now'))
    """, (name, budget))
    list_id = c.lastrowid
    conn.commit()
    conn.close()
    return list_id


def get_grocery_lists() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM grocery_lists ORDER BY created_date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_grocery_items(list_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT gi.*, i.name, i.category, i.price_per_unit
        FROM grocery_items gi
        JOIN ingredients i ON gi.ingredient_id = i.id
        WHERE gi.list_id = ?
        ORDER BY i.category, i.name
    """, (list_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_grocery_item(list_id: int, ingredient_id: int, quantity: float,
                     unit: str, estimated_price: float, added_by: str = "auto") -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO grocery_items
        (list_id, ingredient_id, quantity_needed, unit, estimated_price, added_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (list_id, ingredient_id, quantity, unit, estimated_price, added_by))
    conn.commit()
    conn.close()


def toggle_grocery_item(item_id: int, purchased: bool) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE grocery_items SET purchased=? WHERE id=?",
        (1 if purchased else 0, item_id)
    )
    conn.commit()
    conn.close()


def delete_grocery_list(list_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM grocery_lists WHERE id=?", (list_id,))
    conn.commit()
    conn.close()


def generate_grocery_list_from_plan(start_date: str, budget: float) -> int:
    """
    Scan the meal plan for `start_date` week, collect all required ingredients,
    subtract what's already in the pantry, and create a new grocery list.
    Returns the new list id.
    """
    entries = get_meal_plan_week(start_date)
    if not entries:
        return -1

    pantry = {p["ingredient_id"]: p["quantity"] for p in get_pantry()}
    needed: dict[int, dict] = {}   # ingredient_id → {quantity, unit, price}

    for entry in entries:
        if entry["recipe_id"] is None:
            continue
        ings = get_recipe_ingredients(entry["recipe_id"])
        servings_ratio = entry["servings"]
        for ing in ings:
            ing_id = ing["ingredient_id"]
            qty    = ing["quantity"] * servings_ratio
            if ing_id not in needed:
                needed[ing_id] = {"quantity": 0, "unit": ing["unit"],
                                  "price": ing["price_per_unit"], "name": ing["name"]}
            needed[ing_id]["quantity"] += qty

    # Subtract pantry stock
    shortfall = {}
    for ing_id, info in needed.items():
        have = pantry.get(ing_id, 0)
        shortage = info["quantity"] - have
        if shortage > 0:
            shortfall[ing_id] = {**info, "quantity": shortage}

    if not shortfall:
        return -1   # Nothing to buy!

    list_id = create_grocery_list(
        f"Week of {start_date}", budget
    )
    for ing_id, info in shortfall.items():
        est_price = info["quantity"] * info["price"]
        add_grocery_item(list_id, ing_id, info["quantity"],
                         info["unit"], est_price, "auto")

    return list_id


# ─────────────────────────────────────────────
#  Analytics helpers
# ─────────────────────────────────────────────

def get_weekly_nutrition(start_date: str) -> dict:
    """Aggregate nutrition (calories, protein, carbs, fat) across the week."""
    entries = get_meal_plan_week(start_date)
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    daily: dict[str, dict] = {}

    for e in entries:
        d = e["plan_date"]
        if d not in daily:
            daily[d] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        for key in totals:
            val = (e[key] or 0) * e["servings"]
            totals[key] += val
            daily[d][key] += val

    return {"totals": totals, "daily": daily}


def get_waste_stats() -> dict:
    conn = get_connection()
    rows = conn.execute("""
        SELECT SUM(estimated_cost) as total_cost,
               SUM(1) as total_items,
               reason
        FROM waste_log
        WHERE logged_date >= date('now', '-30 days')
        GROUP BY reason
    """).fetchall()
    total = conn.execute(
        "SELECT SUM(estimated_cost) as tc FROM waste_log"
    ).fetchone()
    conn.close()
    return {
        "by_reason": [dict(r) for r in rows],
        "total_wasted": total["tc"] or 0
    }


def log_waste(ingredient_id: int, quantity: float, unit: str,
              reason: str, estimated_cost: float) -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO waste_log (ingredient_id, quantity_wasted, unit, reason, estimated_cost)
        VALUES (?, ?, ?, ?, ?)
    """, (ingredient_id, quantity, unit, reason, estimated_cost))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  User Preferences
# ─────────────────────────────────────────────

def get_preferences() -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_preferences WHERE id=1").fetchone()
    conn.close()
    return dict(row) if row else {}


def update_preferences(weekly_budget, daily_calories, daily_protein,
                       daily_carbs, daily_fat, dietary_restrictions,
                       household_size) -> None:
    conn = get_connection()
    conn.execute("""
        UPDATE user_preferences
        SET weekly_budget=?, daily_calories=?, daily_protein=?,
            daily_carbs=?, daily_fat=?, dietary_restrictions=?,
            household_size=?
        WHERE id=1
    """, (weekly_budget, daily_calories, daily_protein, daily_carbs,
          daily_fat, dietary_restrictions, household_size))
    conn.commit()
    conn.close()


def is_seeded() -> bool:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    conn.close()
    return count > 0
