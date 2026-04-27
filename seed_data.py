"""
seed_data.py — Populates the database with a realistic catalogue of
ingredients and recipes so the app is immediately usable out of the box.
"""

from database import (
    upsert_ingredient, add_recipe, add_recipe_ingredient,
    add_pantry_item, get_ingredient_by_name, is_seeded
)


# ─────────────────────────────────────────────
#  Master ingredient list
#  (name, category, unit, cal, protein, carbs, fat, price/unit)
# ─────────────────────────────────────────────

INGREDIENTS = [
    # Dairy & Eggs
    ("Egg",              "Dairy & Eggs",  "piece",  78,  6.0, 0.6,  5.0, 0.25),
    ("Milk",             "Dairy & Eggs",  "ml",      0.6, 0.03,0.05, 0.03,0.001),
    ("Greek Yogurt",     "Dairy & Eggs",  "g",       1.0, 0.09,0.04, 0.05,0.003),
    ("Butter",           "Dairy & Eggs",  "g",       7.2, 0.01,0.0,  0.81,0.01),
    ("Parmesan",         "Dairy & Eggs",  "g",       4.3, 0.38,0.04, 0.29,0.05),
    ("Mozzarella",       "Dairy & Eggs",  "g",       3.0, 0.22,0.02, 0.22,0.03),
    ("Cheddar",          "Dairy & Eggs",  "g",       4.0, 0.25,0.01, 0.33,0.04),
    ("Heavy Cream",      "Dairy & Eggs",  "ml",      3.4, 0.02,0.03, 0.36,0.004),
    ("Feta Cheese",      "Dairy & Eggs",  "g",       2.6, 0.14,0.04, 0.21,0.03),

    # Meat & Seafood
    ("Chicken Breast",   "Meat & Seafood","g",       1.6, 0.31,0.0,  0.04,0.012),
    ("Ground Beef",      "Meat & Seafood","g",       2.5, 0.26,0.0,  0.15,0.015),
    ("Salmon Fillet",    "Meat & Seafood","g",       2.1, 0.25,0.0,  0.13,0.025),
    ("Shrimp",           "Meat & Seafood","g",       0.9, 0.18,0.0,  0.01,0.020),
    ("Bacon",            "Meat & Seafood","g",       5.4, 0.37,0.01, 0.42,0.018),
    ("Tuna (canned)",    "Meat & Seafood","g",       1.0, 0.23,0.0,  0.01,0.008),

    # Produce — Vegetables
    ("Onion",            "Vegetables",    "g",       0.4, 0.01,0.09, 0.0, 0.002),
    ("Garlic",           "Vegetables",    "g",       1.5, 0.06,0.33, 0.01,0.005),
    ("Tomato",           "Vegetables",    "g",       0.2, 0.01,0.04, 0.0, 0.003),
    ("Cherry Tomatoes",  "Vegetables",    "g",       0.2, 0.01,0.04, 0.0, 0.005),
    ("Spinach",          "Vegetables",    "g",       0.2, 0.03,0.04, 0.0, 0.005),
    ("Bell Pepper",      "Vegetables",    "g",       0.3, 0.01,0.06, 0.0, 0.004),
    ("Broccoli",         "Vegetables",    "g",       0.3, 0.03,0.07, 0.0, 0.003),
    ("Carrot",           "Vegetables",    "g",       0.4, 0.01,0.10, 0.0, 0.002),
    ("Zucchini",         "Vegetables",    "g",       0.2, 0.01,0.03, 0.0, 0.003),
    ("Mushrooms",        "Vegetables",    "g",       0.2, 0.03,0.03, 0.0, 0.008),
    ("Cucumber",         "Vegetables",    "g",       0.2, 0.01,0.04, 0.0, 0.002),
    ("Avocado",          "Vegetables",    "g",       1.6, 0.02,0.09, 0.15,0.008),
    ("Lettuce",          "Vegetables",    "g",       0.1, 0.01,0.03, 0.0, 0.004),
    ("Sweet Potato",     "Vegetables",    "g",       0.9, 0.02,0.21, 0.0, 0.003),
    ("Kale",             "Vegetables",    "g",       0.5, 0.04,0.10, 0.01,0.006),
    ("Corn",             "Vegetables",    "g",       0.9, 0.03,0.21, 0.01,0.002),

    # Produce — Fruit
    ("Banana",           "Fruit",         "piece",  89,  1.1, 23.0, 0.3, 0.20),
    ("Blueberries",      "Fruit",         "g",       0.6, 0.01,0.14, 0.0, 0.010),
    ("Strawberries",     "Fruit",         "g",       0.3, 0.01,0.08, 0.0, 0.008),
    ("Lemon",            "Fruit",         "piece",  17,  0.6, 5.4,  0.2, 0.30),
    ("Lime",             "Fruit",         "piece",  11,  0.2, 3.7,  0.1, 0.25),

    # Grains & Carbs
    ("Spaghetti",        "Grains",        "g",       1.6, 0.06,0.31, 0.01,0.003),
    ("Penne Pasta",      "Grains",        "g",       1.6, 0.06,0.31, 0.01,0.003),
    ("Rice",             "Grains",        "g",       1.3, 0.03,0.28, 0.0, 0.002),
    ("Quinoa",           "Grains",        "g",       1.2, 0.04,0.21, 0.02,0.006),
    ("Oats",             "Grains",        "g",       3.9, 0.17,0.66, 0.07,0.003),
    ("Bread",            "Grains",        "slice",  80,  3.0, 15.0, 1.0, 0.15),
    ("Tortilla Wrap",    "Grains",        "piece",  120, 3.5, 20.0, 3.0, 0.30),
    ("Pizza Dough",      "Grains",        "g",       2.5, 0.07,0.47, 0.03,0.003),
    ("Arborio Rice",     "Grains",        "g",       1.6, 0.03,0.35, 0.0, 0.005),

    # Legumes
    ("Chickpeas",        "Legumes",       "g",       1.6, 0.09,0.27, 0.03,0.003),
    ("Lentils",          "Legumes",       "g",       1.2, 0.09,0.20, 0.0, 0.004),
    ("Black Beans",      "Legumes",       "g",       1.3, 0.09,0.24, 0.01,0.003),

    # Pantry Staples
    ("Olive Oil",        "Pantry",        "ml",      8.8, 0.0, 0.0,  1.0, 0.010),
    ("Soy Sauce",        "Pantry",        "ml",      0.5, 0.08,0.08, 0.0, 0.005),
    ("Tomato Sauce",     "Pantry",        "g",       0.3, 0.01,0.07, 0.01,0.003),
    ("Coconut Milk",     "Pantry",        "ml",      2.3, 0.02,0.03, 0.24,0.005),
    ("Vegetable Broth",  "Pantry",        "ml",      0.1, 0.0, 0.02, 0.0, 0.002),
    ("Honey",            "Pantry",        "g",       3.0, 0.0, 0.82, 0.0, 0.010),
    ("Soy Sauce",        "Pantry",        "ml",      0.5, 0.08,0.08, 0.0, 0.005),
    ("Tahini",           "Pantry",        "g",       5.9, 0.17,0.21, 0.54,0.015),
    ("Flour",            "Pantry",        "g",       3.6, 0.10,0.76, 0.01,0.001),
    ("Sugar",            "Pantry",        "g",       4.0, 0.0, 1.0,  0.0, 0.001),

    # Herbs & Spices
    ("Basil",            "Herbs & Spices","g",       2.2, 0.32,0.26, 0.06,0.020),
    ("Cumin",            "Herbs & Spices","g",       3.7, 0.18,0.44, 0.22,0.010),
    ("Curry Powder",     "Herbs & Spices","g",       3.3, 0.14,0.58, 0.14,0.010),
    ("Paprika",          "Herbs & Spices","g",       2.8, 0.14,0.54, 0.13,0.010),
    ("Oregano",          "Herbs & Spices","g",       2.7, 0.11,0.69, 0.04,0.010),
    ("Cinnamon",         "Herbs & Spices","g",       2.5, 0.04,0.81, 0.01,0.010),
    ("Ginger",           "Herbs & Spices","g",       0.8, 0.02,0.18, 0.01,0.008),
    ("Chili Flakes",     "Herbs & Spices","g",       3.2, 0.12,0.57, 0.17,0.010),
    ("Black Pepper",     "Herbs & Spices","g",       2.5, 0.10,0.64, 0.03,0.010),
    ("Salt",             "Herbs & Spices","g",       0.0, 0.0, 0.0,  0.0, 0.001),

    # Nuts & Seeds
    ("Almonds",          "Nuts & Seeds",  "g",       5.8, 0.21,0.22, 0.50,0.020),
    ("Walnuts",          "Nuts & Seeds",  "g",       6.5, 0.15,0.14, 0.65,0.025),
    ("Chia Seeds",       "Nuts & Seeds",  "g",       4.9, 0.17,0.42, 0.31,0.020),
    ("Sunflower Seeds",  "Nuts & Seeds",  "g",       5.8, 0.21,0.20, 0.51,0.010),
]


# ─────────────────────────────────────────────
#  Recipe catalogue
# ─────────────────────────────────────────────

RECIPES = [
    # ── BREAKFAST ──────────────────────────────────────────────────────────
    {
        "name": "Classic Scrambled Eggs",
        "description": "Fluffy, creamy scrambled eggs — the perfect quick breakfast.",
        "category": "Breakfast", "prep_time": 5, "cook_time": 5,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian,gluten-free",
        "image_emoji": "🍳",
        "calories": 320, "protein": 22, "carbs": 4, "fat": 24, "fiber": 0,
        "instructions": (
            "1. Crack eggs into a bowl, add milk, salt and pepper. Beat well.\n"
            "2. Melt butter in a non-stick pan over medium-low heat.\n"
            "3. Pour in egg mixture. Gently stir with a spatula in slow, figure-8 motions.\n"
            "4. Remove from heat while still slightly glossy. Serve immediately."
        ),
        "ingredients": [
            ("Egg", 4, "piece"), ("Milk", 30, "ml"),
            ("Butter", 15, "g"), ("Salt", 2, "g"), ("Black Pepper", 1, "g"),
        ],
    },
    {
        "name": "Overnight Oats",
        "description": "No-cook oats soaked overnight — grab-and-go nutrition.",
        "category": "Breakfast", "prep_time": 5, "cook_time": 0,
        "servings": 1, "difficulty": "Easy",
        "dietary_tags": "vegetarian,vegan",
        "image_emoji": "🥣",
        "calories": 380, "protein": 14, "carbs": 58, "fat": 9, "fiber": 7,
        "instructions": (
            "1. Combine oats, milk (or dairy-free alternative), and chia seeds in a jar.\n"
            "2. Stir in honey and a pinch of cinnamon.\n"
            "3. Seal and refrigerate overnight (at least 6 hours).\n"
            "4. Top with blueberries and a drizzle of honey before serving."
        ),
        "ingredients": [
            ("Oats", 80, "g"), ("Milk", 180, "ml"), ("Chia Seeds", 15, "g"),
            ("Honey", 10, "g"), ("Blueberries", 60, "g"), ("Cinnamon", 2, "g"),
        ],
    },
    {
        "name": "Avocado Toast",
        "description": "Creamy avocado on toasted bread with a lemon kick.",
        "category": "Breakfast", "prep_time": 5, "cook_time": 2,
        "servings": 1, "difficulty": "Easy",
        "dietary_tags": "vegetarian,vegan,dairy-free",
        "image_emoji": "🥑",
        "calories": 310, "protein": 9, "carbs": 28, "fat": 20, "fiber": 8,
        "instructions": (
            "1. Toast bread slices until golden.\n"
            "2. Halve avocado, remove pit, scoop flesh into a bowl.\n"
            "3. Mash with lemon juice, salt and pepper.\n"
            "4. Spread on toast. Top with chili flakes."
        ),
        "ingredients": [
            ("Bread", 2, "slice"), ("Avocado", 150, "g"),
            ("Lemon", 0.5, "piece"), ("Salt", 2, "g"),
            ("Chili Flakes", 1, "g"), ("Black Pepper", 1, "g"),
        ],
    },
    {
        "name": "Banana Pancakes",
        "description": "Fluffy, naturally sweet pancakes with ripe bananas.",
        "category": "Breakfast", "prep_time": 10, "cook_time": 15,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian",
        "image_emoji": "🥞",
        "calories": 420, "protein": 14, "carbs": 72, "fat": 10, "fiber": 3,
        "instructions": (
            "1. Mash banana thoroughly in a bowl.\n"
            "2. Add eggs, flour, milk, and a pinch of salt. Mix into a smooth batter.\n"
            "3. Heat butter in a non-stick pan over medium heat.\n"
            "4. Pour small ladles of batter, cook 2 min per side until golden.\n"
            "5. Serve with honey and sliced strawberries."
        ),
        "ingredients": [
            ("Banana", 2, "piece"), ("Egg", 2, "piece"), ("Flour", 100, "g"),
            ("Milk", 100, "ml"), ("Butter", 20, "g"),
            ("Honey", 20, "g"), ("Strawberries", 80, "g"),
        ],
    },
    {
        "name": "Greek Yogurt Parfait",
        "description": "Layers of creamy yogurt, granola crunch, and fresh berries.",
        "category": "Breakfast", "prep_time": 5, "cook_time": 0,
        "servings": 1, "difficulty": "Easy",
        "dietary_tags": "vegetarian,gluten-free",
        "image_emoji": "🍓",
        "calories": 340, "protein": 20, "carbs": 44, "fat": 8, "fiber": 4,
        "instructions": (
            "1. Spoon half the Greek yogurt into a glass or bowl.\n"
            "2. Add a layer of blueberries and strawberries.\n"
            "3. Sprinkle with oats (toasted) and almonds.\n"
            "4. Repeat layers. Drizzle with honey on top."
        ),
        "ingredients": [
            ("Greek Yogurt", 200, "g"), ("Blueberries", 50, "g"),
            ("Strawberries", 50, "g"), ("Oats", 30, "g"),
            ("Almonds", 15, "g"), ("Honey", 10, "g"),
        ],
    },
    {
        "name": "Smoothie Bowl",
        "description": "A thick, vibrant smoothie bowl packed with antioxidants.",
        "category": "Breakfast", "prep_time": 10, "cook_time": 0,
        "servings": 1, "difficulty": "Easy",
        "dietary_tags": "vegetarian,vegan,gluten-free,dairy-free",
        "image_emoji": "🍇",
        "calories": 390, "protein": 12, "carbs": 65, "fat": 11, "fiber": 9,
        "instructions": (
            "1. Blend frozen banana, blueberries, spinach, and coconut milk until thick.\n"
            "2. Pour into a bowl — it should be thick enough to support toppings.\n"
            "3. Arrange toppings: chia seeds, almonds, and fresh strawberries.\n"
            "4. Serve immediately."
        ),
        "ingredients": [
            ("Banana", 1, "piece"), ("Blueberries", 80, "g"),
            ("Spinach", 30, "g"), ("Coconut Milk", 60, "ml"),
            ("Chia Seeds", 10, "g"), ("Almonds", 15, "g"),
            ("Strawberries", 40, "g"),
        ],
    },

    # ── LUNCH ──────────────────────────────────────────────────────────────
    {
        "name": "Caesar Salad",
        "description": "Crisp romaine lettuce with a classic creamy dressing.",
        "category": "Lunch", "prep_time": 15, "cook_time": 0,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "gluten-free",
        "image_emoji": "🥗",
        "calories": 380, "protein": 24, "carbs": 12, "fat": 26, "fiber": 3,
        "instructions": (
            "1. Chop lettuce into bite-sized pieces.\n"
            "2. Mix tahini, lemon juice, garlic (minced), parmesan, salt and pepper for dressing.\n"
            "3. Toss lettuce with dressing.\n"
            "4. Top with extra parmesan. Serve cold."
        ),
        "ingredients": [
            ("Lettuce", 200, "g"), ("Chicken Breast", 200, "g"),
            ("Parmesan", 40, "g"), ("Lemon", 1, "piece"),
            ("Garlic", 5, "g"), ("Tahini", 20, "g"),
            ("Olive Oil", 20, "ml"), ("Black Pepper", 2, "g"),
        ],
    },
    {
        "name": "Chicken & Avocado Wrap",
        "description": "Grilled chicken, creamy avocado and fresh veggies in a tortilla.",
        "category": "Lunch", "prep_time": 10, "cook_time": 10,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "dairy-free",
        "image_emoji": "🌯",
        "calories": 510, "protein": 38, "carbs": 42, "fat": 20, "fiber": 5,
        "instructions": (
            "1. Season chicken breast with paprika, salt and pepper. Pan-fry until cooked through.\n"
            "2. Slice chicken into strips.\n"
            "3. Mash avocado with lime juice, salt and chili flakes.\n"
            "4. Warm tortillas. Spread avocado, add chicken, lettuce, tomato.\n"
            "5. Roll tightly and serve."
        ),
        "ingredients": [
            ("Chicken Breast", 300, "g"), ("Tortilla Wrap", 2, "piece"),
            ("Avocado", 120, "g"), ("Lime", 1, "piece"),
            ("Lettuce", 60, "g"), ("Tomato", 100, "g"),
            ("Paprika", 3, "g"), ("Olive Oil", 15, "ml"),
        ],
    },
    {
        "name": "Tomato & Lentil Soup",
        "description": "Hearty, warming soup packed with protein and flavour.",
        "category": "Lunch", "prep_time": 10, "cook_time": 30,
        "servings": 4, "difficulty": "Easy",
        "dietary_tags": "vegetarian,vegan,gluten-free,dairy-free",
        "image_emoji": "🍲",
        "calories": 290, "protein": 18, "carbs": 45, "fat": 5, "fiber": 12,
        "instructions": (
            "1. Sauté onion and garlic in olive oil for 5 minutes.\n"
            "2. Add diced tomatoes, tomato sauce, lentils and vegetable broth.\n"
            "3. Season with cumin, paprika, salt and pepper.\n"
            "4. Simmer 25 minutes until lentils are soft.\n"
            "5. Blend half the soup for a creamy-yet-chunky texture. Serve with bread."
        ),
        "ingredients": [
            ("Lentils", 200, "g"), ("Tomato", 300, "g"),
            ("Tomato Sauce", 150, "g"), ("Vegetable Broth", 800, "ml"),
            ("Onion", 120, "g"), ("Garlic", 10, "g"),
            ("Cumin", 5, "g"), ("Paprika", 3, "g"),
            ("Olive Oil", 20, "ml"),
        ],
    },
    {
        "name": "Quinoa Buddha Bowl",
        "description": "Nourishing bowl with quinoa, roasted veggies and tahini drizzle.",
        "category": "Lunch", "prep_time": 15, "cook_time": 25,
        "servings": 2, "difficulty": "Medium",
        "dietary_tags": "vegetarian,vegan,gluten-free,dairy-free",
        "image_emoji": "🥙",
        "calories": 480, "protein": 20, "carbs": 65, "fat": 16, "fiber": 11,
        "instructions": (
            "1. Cook quinoa according to package instructions.\n"
            "2. Toss chickpeas, sweet potato cubes and bell pepper with olive oil, cumin, paprika.\n"
            "3. Roast at 200°C for 20-25 minutes until golden.\n"
            "4. Make dressing: tahini + lemon juice + water + garlic.\n"
            "5. Assemble bowl: quinoa base, roasted veggies, spinach, dressing on top."
        ),
        "ingredients": [
            ("Quinoa", 160, "g"), ("Chickpeas", 160, "g"),
            ("Sweet Potato", 200, "g"), ("Bell Pepper", 150, "g"),
            ("Spinach", 80, "g"), ("Tahini", 30, "g"),
            ("Lemon", 1, "piece"), ("Garlic", 5, "g"),
            ("Olive Oil", 20, "ml"), ("Cumin", 4, "g"), ("Paprika", 3, "g"),
        ],
    },
    {
        "name": "Tuna & Cucumber Salad",
        "description": "A light, refreshing high-protein salad ready in minutes.",
        "category": "Lunch", "prep_time": 10, "cook_time": 0,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "gluten-free,dairy-free",
        "image_emoji": "🥗",
        "calories": 240, "protein": 32, "carbs": 10, "fat": 8, "fiber": 2,
        "instructions": (
            "1. Drain tuna and flake into a bowl.\n"
            "2. Dice cucumber, halve cherry tomatoes.\n"
            "3. Add to tuna with olive oil, lemon juice, salt, pepper.\n"
            "4. Toss gently and serve over lettuce."
        ),
        "ingredients": [
            ("Tuna (canned)", 200, "g"), ("Cucumber", 150, "g"),
            ("Cherry Tomatoes", 100, "g"), ("Lettuce", 80, "g"),
            ("Lemon", 1, "piece"), ("Olive Oil", 15, "ml"),
            ("Salt", 2, "g"), ("Black Pepper", 1, "g"),
        ],
    },
    {
        "name": "Shakshuka",
        "description": "Eggs poached in a spiced tomato and pepper sauce.",
        "category": "Lunch", "prep_time": 10, "cook_time": 20,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian,gluten-free",
        "image_emoji": "🍳",
        "calories": 340, "protein": 20, "carbs": 22, "fat": 18, "fiber": 5,
        "instructions": (
            "1. Sauté onion, bell pepper and garlic in olive oil until soft.\n"
            "2. Add tomatoes, tomato sauce, paprika, cumin, chili flakes.\n"
            "3. Simmer 10 minutes until sauce thickens.\n"
            "4. Make wells in sauce, crack in eggs. Cover and cook 5-8 min.\n"
            "5. Garnish with feta and fresh basil."
        ),
        "ingredients": [
            ("Egg", 4, "piece"), ("Tomato", 400, "g"),
            ("Bell Pepper", 150, "g"), ("Onion", 100, "g"),
            ("Garlic", 10, "g"), ("Feta Cheese", 60, "g"),
            ("Tomato Sauce", 100, "g"), ("Paprika", 5, "g"),
            ("Cumin", 3, "g"), ("Chili Flakes", 2, "g"),
            ("Olive Oil", 20, "ml"), ("Basil", 5, "g"),
        ],
    },

    # ── DINNER ─────────────────────────────────────────────────────────────
    {
        "name": "Spaghetti Bolognese",
        "description": "Classic Italian meat sauce on al-dente spaghetti.",
        "category": "Dinner", "prep_time": 10, "cook_time": 45,
        "servings": 4, "difficulty": "Medium",
        "dietary_tags": "",
        "image_emoji": "🍝",
        "calories": 620, "protein": 38, "carbs": 72, "fat": 18, "fiber": 4,
        "instructions": (
            "1. Brown ground beef in a pan. Set aside.\n"
            "2. Sauté onion, garlic, carrots in olive oil for 8 min.\n"
            "3. Add beef back in, add tomato sauce and tomatoes. Season.\n"
            "4. Simmer on low heat for 30 minutes, stirring occasionally.\n"
            "5. Cook spaghetti al dente. Drain, toss with sauce.\n"
            "6. Serve topped with parmesan."
        ),
        "ingredients": [
            ("Spaghetti", 400, "g"), ("Ground Beef", 500, "g"),
            ("Tomato Sauce", 400, "g"), ("Tomato", 200, "g"),
            ("Onion", 120, "g"), ("Garlic", 15, "g"),
            ("Carrot", 100, "g"), ("Parmesan", 60, "g"),
            ("Olive Oil", 25, "ml"), ("Oregano", 5, "g"),
        ],
    },
    {
        "name": "Grilled Salmon with Rice",
        "description": "Oven-baked salmon with lemon herb rice — simple and nutritious.",
        "category": "Dinner", "prep_time": 10, "cook_time": 25,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "gluten-free,dairy-free",
        "image_emoji": "🐟",
        "calories": 560, "protein": 48, "carbs": 52, "fat": 16, "fiber": 2,
        "instructions": (
            "1. Preheat oven to 200°C.\n"
            "2. Place salmon on baking tray, drizzle with olive oil, lemon juice.\n"
            "3. Season with garlic, salt and pepper. Bake 12-15 min.\n"
            "4. Cook rice. Fluff with fork, mix in lemon zest.\n"
            "5. Serve salmon on rice with steamed broccoli."
        ),
        "ingredients": [
            ("Salmon Fillet", 400, "g"), ("Rice", 200, "g"),
            ("Broccoli", 200, "g"), ("Lemon", 1, "piece"),
            ("Garlic", 8, "g"), ("Olive Oil", 20, "ml"),
            ("Salt", 3, "g"), ("Black Pepper", 2, "g"),
        ],
    },
    {
        "name": "Vegetable Curry",
        "description": "Aromatic coconut vegetable curry — vegan comfort food.",
        "category": "Dinner", "prep_time": 15, "cook_time": 30,
        "servings": 4, "difficulty": "Medium",
        "dietary_tags": "vegetarian,vegan,gluten-free,dairy-free",
        "image_emoji": "🍛",
        "calories": 390, "protein": 14, "carbs": 52, "fat": 16, "fiber": 10,
        "instructions": (
            "1. Sauté onion, garlic and ginger in olive oil for 5 min.\n"
            "2. Add curry powder, cumin, chili flakes — cook 2 min.\n"
            "3. Add chickpeas, sweet potato, bell pepper and coconut milk.\n"
            "4. Pour in vegetable broth, simmer 20 min until potato is tender.\n"
            "5. Add spinach in final 2 min. Serve with rice."
        ),
        "ingredients": [
            ("Chickpeas", 240, "g"), ("Sweet potato", 300, "g"),
            ("Bell Pepper", 150, "g"), ("Spinach", 80, "g"),
            ("Coconut Milk", 400, "ml"), ("Vegetable Broth", 200, "ml"),
            ("Onion", 120, "g"), ("Garlic", 10, "g"),
            ("Ginger", 10, "g"), ("Curry Powder", 15, "g"),
            ("Cumin", 5, "g"), ("Olive Oil", 20, "ml"),
            ("Rice", 200, "g"),
        ],
    },
    {
        "name": "Beef Stir-Fry",
        "description": "Quick wok-fired beef and vegetables in a savory sauce.",
        "category": "Dinner", "prep_time": 15, "cook_time": 10,
        "servings": 2, "difficulty": "Medium",
        "dietary_tags": "dairy-free",
        "image_emoji": "🥘",
        "calories": 490, "protein": 40, "carbs": 38, "fat": 17, "fiber": 4,
        "instructions": (
            "1. Slice beef thinly against the grain. Marinate with soy sauce.\n"
            "2. Prep vegetables: slice bell peppers, broccoli into florets, mince garlic.\n"
            "3. High heat in wok. Cook beef 3 min, remove.\n"
            "4. Add vegetables, garlic, ginger. Stir-fry 4 min.\n"
            "5. Return beef, add remaining soy sauce, toss together. Serve with rice."
        ),
        "ingredients": [
            ("Ground Beef", 300, "g"), ("Broccoli", 200, "g"),
            ("Bell Pepper", 150, "g"), ("Carrot", 100, "g"),
            ("Garlic", 10, "g"), ("Ginger", 8, "g"),
            ("Soy Sauce", 40, "ml"), ("Olive Oil", 20, "ml"),
            ("Rice", 200, "g"),
        ],
    },
    {
        "name": "Mushroom Risotto",
        "description": "Creamy Italian risotto with earthy mushrooms and parmesan.",
        "category": "Dinner", "prep_time": 10, "cook_time": 35,
        "servings": 2, "difficulty": "Hard",
        "dietary_tags": "vegetarian,gluten-free",
        "image_emoji": "🍄",
        "calories": 540, "protein": 18, "carbs": 72, "fat": 20, "fiber": 3,
        "instructions": (
            "1. Sauté onion in olive oil + butter until translucent.\n"
            "2. Add arborio rice, toast 2 min.\n"
            "3. Add white wine (optional), stir until absorbed.\n"
            "4. Add warm broth ladle by ladle, stirring continuously for 25-30 min.\n"
            "5. Meanwhile sauté mushrooms in butter with garlic.\n"
            "6. Fold in mushrooms, parmesan and remaining butter. Season and serve."
        ),
        "ingredients": [
            ("Arborio Rice", 200, "g"), ("Mushrooms", 300, "g"),
            ("Vegetable Broth", 900, "ml"), ("Onion", 80, "g"),
            ("Garlic", 8, "g"), ("Parmesan", 60, "g"),
            ("Butter", 40, "g"), ("Olive Oil", 20, "ml"),
        ],
    },
    {
        "name": "Chicken Tacos",
        "description": "Spicy grilled chicken with fresh salsa in warm tortillas.",
        "category": "Dinner", "prep_time": 15, "cook_time": 15,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "dairy-free",
        "image_emoji": "🌮",
        "calories": 530, "protein": 42, "carbs": 50, "fat": 14, "fiber": 5,
        "instructions": (
            "1. Season chicken with cumin, paprika, chili flakes, salt.\n"
            "2. Pan-fry chicken until cooked. Rest 5 min, slice thin.\n"
            "3. Dice tomato, onion and avocado for salsa. Mix with lime juice.\n"
            "4. Warm tortillas in dry pan.\n"
            "5. Assemble tacos: chicken, salsa, lettuce."
        ),
        "ingredients": [
            ("Chicken Breast", 300, "g"), ("Tortilla Wrap", 4, "piece"),
            ("Avocado", 100, "g"), ("Tomato", 150, "g"),
            ("Onion", 60, "g"), ("Lettuce", 60, "g"),
            ("Lime", 1, "piece"), ("Cumin", 4, "g"),
            ("Paprika", 3, "g"), ("Chili Flakes", 2, "g"),
            ("Olive Oil", 15, "ml"),
        ],
    },
    {
        "name": "Margherita Pizza",
        "description": "Thin-crust Italian pizza with fresh mozzarella and basil.",
        "category": "Dinner", "prep_time": 20, "cook_time": 15,
        "servings": 2, "difficulty": "Medium",
        "dietary_tags": "vegetarian",
        "image_emoji": "🍕",
        "calories": 580, "protein": 24, "carbs": 76, "fat": 20, "fiber": 4,
        "instructions": (
            "1. Preheat oven to 250°C with baking stone or tray inside.\n"
            "2. Roll out pizza dough to thin circles.\n"
            "3. Spread thin layer of tomato sauce. Top with mozzarella.\n"
            "4. Drizzle with olive oil, season with salt.\n"
            "5. Bake 10-12 min until crust is crispy and cheese is bubbly.\n"
            "6. Top with fresh basil leaves and serve immediately."
        ),
        "ingredients": [
            ("Pizza Dough", 350, "g"), ("Tomato Sauce", 150, "g"),
            ("Mozzarella", 200, "g"), ("Basil", 10, "g"),
            ("Olive Oil", 20, "ml"), ("Salt", 3, "g"),
            ("Oregano", 3, "g"),
        ],
    },
    {
        "name": "Pasta Primavera",
        "description": "Fresh seasonal vegetables tossed with pasta and parmesan.",
        "category": "Dinner", "prep_time": 15, "cook_time": 20,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian",
        "image_emoji": "🍝",
        "calories": 490, "protein": 18, "carbs": 74, "fat": 14, "fiber": 6,
        "instructions": (
            "1. Cook penne according to package. Reserve 1 cup pasta water.\n"
            "2. Sauté garlic in olive oil. Add zucchini, bell pepper, cherry tomatoes.\n"
            "3. Cook vegetables 5-7 minutes until tender but still vibrant.\n"
            "4. Add drained pasta, splash of pasta water, parmesan.\n"
            "5. Toss everything together. Season and serve with extra parmesan."
        ),
        "ingredients": [
            ("Penne Pasta", 300, "g"), ("Zucchini", 150, "g"),
            ("Bell Pepper", 120, "g"), ("Cherry Tomatoes", 150, "g"),
            ("Parmesan", 50, "g"), ("Garlic", 10, "g"),
            ("Basil", 8, "g"), ("Olive Oil", 25, "ml"),
        ],
    },
    {
        "name": "Thai Green Curry",
        "description": "Fragrant Thai curry with shrimp in rich coconut sauce.",
        "category": "Dinner", "prep_time": 15, "cook_time": 20,
        "servings": 2, "difficulty": "Medium",
        "dietary_tags": "gluten-free,dairy-free",
        "image_emoji": "🍜",
        "calories": 520, "protein": 34, "carbs": 48, "fat": 22, "fiber": 4,
        "instructions": (
            "1. Sauté garlic and ginger for 2 min.\n"
            "2. Add curry powder and chili flakes, stir 1 min.\n"
            "3. Pour in coconut milk, bring to gentle simmer.\n"
            "4. Add shrimp, bell pepper, zucchini. Cook 5-7 min.\n"
            "5. Add spinach in last 2 min. Serve with rice."
        ),
        "ingredients": [
            ("Shrimp", 300, "g"), ("Coconut Milk", 400, "ml"),
            ("Bell Pepper", 150, "g"), ("Zucchini", 120, "g"),
            ("Spinach", 60, "g"), ("Garlic", 10, "g"),
            ("Ginger", 10, "g"), ("Curry Powder", 20, "g"),
            ("Chili Flakes", 2, "g"), ("Lime", 1, "piece"),
            ("Rice", 200, "g"),
        ],
    },
    {
        "name": "Black Bean Tacos",
        "description": "Hearty vegan tacos packed with seasoned black beans.",
        "category": "Dinner", "prep_time": 10, "cook_time": 15,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian,vegan,dairy-free",
        "image_emoji": "🫘",
        "calories": 460, "protein": 22, "carbs": 68, "fat": 12, "fiber": 16,
        "instructions": (
            "1. Drain and rinse black beans.\n"
            "2. Sauté onion, garlic and bell pepper in olive oil.\n"
            "3. Add beans, cumin, paprika, chili flakes. Cook 8-10 min.\n"
            "4. Mash beans slightly with a fork for texture.\n"
            "5. Warm tortillas. Fill with beans, avocado, tomato, corn."
        ),
        "ingredients": [
            ("Black Beans", 300, "g"), ("Tortilla Wrap", 4, "piece"),
            ("Avocado", 100, "g"), ("Tomato", 120, "g"),
            ("Corn", 80, "g"), ("Onion", 80, "g"),
            ("Garlic", 8, "g"), ("Bell Pepper", 100, "g"),
            ("Cumin", 5, "g"), ("Paprika", 3, "g"),
            ("Chili Flakes", 2, "g"), ("Olive Oil", 15, "ml"),
        ],
    },
    {
        "name": "Grilled Chicken & Veggies",
        "description": "Lean chicken breast with colourful roasted vegetables.",
        "category": "Dinner", "prep_time": 10, "cook_time": 25,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "gluten-free,dairy-free",
        "image_emoji": "🍗",
        "calories": 420, "protein": 48, "carbs": 28, "fat": 12, "fiber": 6,
        "instructions": (
            "1. Preheat oven to 200°C.\n"
            "2. Toss zucchini, bell pepper, cherry tomatoes with olive oil, salt, oregano.\n"
            "3. Roast vegetables 20 min.\n"
            "4. Meanwhile grill chicken breast 6-7 min per side.\n"
            "5. Rest chicken 5 min, slice. Serve with roasted vegetables."
        ),
        "ingredients": [
            ("Chicken Breast", 400, "g"), ("Zucchini", 150, "g"),
            ("Bell Pepper", 150, "g"), ("Cherry Tomatoes", 100, "g"),
            ("Broccoli", 150, "g"), ("Garlic", 8, "g"),
            ("Olive Oil", 25, "ml"), ("Oregano", 4, "g"),
            ("Salt", 3, "g"), ("Black Pepper", 2, "g"),
        ],
    },
    {
        "name": "Kale & Sweet Potato Bowl",
        "description": "Nutrient-dense bowl with roasted sweet potato, kale and quinoa.",
        "category": "Dinner", "prep_time": 15, "cook_time": 30,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian,vegan,gluten-free,dairy-free",
        "image_emoji": "🥬",
        "calories": 440, "protein": 16, "carbs": 72, "fat": 11, "fiber": 12,
        "instructions": (
            "1. Cube sweet potato, toss with olive oil, cumin and paprika.\n"
            "2. Roast at 200°C for 25 min until golden.\n"
            "3. Cook quinoa. Massage kale with olive oil and salt.\n"
            "4. Make dressing: tahini + lemon + water + garlic.\n"
            "5. Assemble bowls: quinoa, roasted sweet potato, kale, dressing."
        ),
        "ingredients": [
            ("Sweet Potato", 300, "g"), ("Quinoa", 160, "g"),
            ("Kale", 120, "g"), ("Tahini", 30, "g"),
            ("Lemon", 1, "piece"), ("Garlic", 5, "g"),
            ("Cumin", 4, "g"), ("Paprika", 3, "g"),
            ("Olive Oil", 25, "ml"),
        ],
    },

    # ── SNACKS ────────────────────────────────────────────────────────────
    {
        "name": "Hummus & Veggies",
        "description": "Homemade hummus with crunchy vegetable sticks for dipping.",
        "category": "Snack", "prep_time": 10, "cook_time": 0,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian,vegan,gluten-free,dairy-free",
        "image_emoji": "🫛",
        "calories": 260, "protein": 12, "carbs": 32, "fat": 10, "fiber": 8,
        "instructions": (
            "1. Blend chickpeas, tahini, lemon juice, garlic, olive oil until smooth.\n"
            "2. Season with cumin and salt. Add water if too thick.\n"
            "3. Serve in a bowl with a drizzle of olive oil and paprika on top.\n"
            "4. Cut carrots, cucumber and bell pepper into sticks for dipping."
        ),
        "ingredients": [
            ("Chickpeas", 200, "g"), ("Tahini", 30, "g"),
            ("Lemon", 1, "piece"), ("Garlic", 5, "g"),
            ("Olive Oil", 20, "ml"), ("Cumin", 3, "g"),
            ("Carrot", 100, "g"), ("Cucumber", 100, "g"),
        ],
    },
    {
        "name": "Almond Energy Balls",
        "description": "No-bake energy balls with oats, almonds and honey.",
        "category": "Snack", "prep_time": 15, "cook_time": 0,
        "servings": 4, "difficulty": "Easy",
        "dietary_tags": "vegetarian,gluten-free",
        "image_emoji": "⚾",
        "calories": 210, "protein": 7, "carbs": 24, "fat": 11, "fiber": 3,
        "instructions": (
            "1. Blend almonds in a food processor until finely chopped.\n"
            "2. Combine with oats, honey, chia seeds and a pinch of cinnamon.\n"
            "3. Mix well — add a splash of water if mixture is too dry.\n"
            "4. Roll into 12 balls. Refrigerate 30 min to set."
        ),
        "ingredients": [
            ("Almonds", 80, "g"), ("Oats", 60, "g"),
            ("Honey", 40, "g"), ("Chia Seeds", 15, "g"),
            ("Cinnamon", 2, "g"),
        ],
    },
    {
        "name": "Caprese Salad",
        "description": "Simple Italian classic — fresh mozzarella, tomato and basil.",
        "category": "Snack", "prep_time": 5, "cook_time": 0,
        "servings": 2, "difficulty": "Easy",
        "dietary_tags": "vegetarian,gluten-free",
        "image_emoji": "🍅",
        "calories": 240, "protein": 14, "carbs": 6, "fat": 18, "fiber": 1,
        "instructions": (
            "1. Slice tomatoes and mozzarella into equal rounds.\n"
            "2. Alternate tomato and mozzarella slices on a plate.\n"
            "3. Tuck fresh basil leaves between layers.\n"
            "4. Drizzle generously with olive oil, season with salt and pepper."
        ),
        "ingredients": [
            ("Tomato", 200, "g"), ("Mozzarella", 150, "g"),
            ("Basil", 10, "g"), ("Olive Oil", 20, "ml"),
            ("Salt", 2, "g"), ("Black Pepper", 1, "g"),
        ],
    },
]


# ─────────────────────────────────────────────
#  Starter pantry (demo items)
# ─────────────────────────────────────────────

STARTER_PANTRY = [
    ("Egg",           6,   "piece", 10),   # expires in 10 days
    ("Milk",          500, "ml",    5),
    ("Butter",        100, "g",     14),
    ("Onion",         300, "g",     14),
    ("Garlic",        50,  "g",     21),
    ("Olive Oil",     300, "ml",    None),
    ("Salt",          200, "g",     None),
    ("Black Pepper",  30,  "g",     None),
    ("Tomato",        400, "g",     5),    # expiring soon!
    ("Chicken Breast",300, "g",     2),    # expiring very soon!
    ("Spaghetti",     400, "g",     None),
    ("Tomato Sauce",  400, "g",     None),
    ("Rice",          500, "g",     None),
    ("Oats",          400, "g",     None),
    ("Lemon",         3,   "piece", 14),
    ("Avocado",       2,   "piece", 3),    # expiring soon
    ("Spinach",       150, "g",     2),    # expiring very soon!
    ("Parmesan",      80,  "g",     21),
    ("Chickpeas",     400, "g",     None),
    ("Broccoli",      200, "g",     4),
]


# ─────────────────────────────────────────────
#  Seeder function
# ─────────────────────────────────────────────

def seed_database() -> None:
    """
    Insert all ingredient, recipe and starter-pantry data.
    Safe to call multiple times — uses ON CONFLICT DO NOTHING logic via is_seeded().
    """
    if is_seeded():
        return   # Already done

    from datetime import date, timedelta

    # 1. Insert ingredients
    ing_id_map: dict[str, int] = {}
    for row in INGREDIENTS:
        name, category, unit, cal, pro, carb, fat, price = row
        ing_id = upsert_ingredient(name, category, unit, cal, pro, carb, fat, price)
        ing_id_map[name.lower()] = ing_id

    def _get_id(name: str) -> int:
        """Look up ingredient id — case-insensitive."""
        key = name.lower()
        if key in ing_id_map:
            return ing_id_map[key]
        # Fallback: query DB (handles slight name variations)
        from database import get_ingredient_by_name
        ing = get_ingredient_by_name(name)
        if ing:
            return ing["id"]
        raise KeyError(f"Ingredient not found: {name}")

    # 2. Insert recipes + recipe_ingredients
    for r in RECIPES:
        recipe_id = add_recipe(
            r["name"], r["description"], r["category"],
            r["prep_time"], r["cook_time"], r["servings"],
            r["difficulty"], r["dietary_tags"], r["instructions"],
            r["image_emoji"],
            r["calories"], r["protein"], r["carbs"], r["fat"], r["fiber"]
        )
        for ing_name, qty, unit in r["ingredients"]:
            try:
                ing_id = _get_id(ing_name)
                add_recipe_ingredient(recipe_id, ing_id, qty, unit)
            except KeyError:
                pass   # skip missing ingredients gracefully

    # 3. Seed a starter pantry
    for name, qty, unit, days_to_expiry in STARTER_PANTRY:
        try:
            ing_id = _get_id(name)
            expiry = (
                (date.today() + timedelta(days=days_to_expiry)).isoformat()
                if days_to_expiry is not None else None
            )
            add_pantry_item(ing_id, qty, unit, expiry, "Fridge", "")
        except KeyError:
            pass
