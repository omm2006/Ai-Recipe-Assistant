import os
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from tavily import TavilyClient

# -----------------------------------------------------------------------------
# Configuration & Paths
# -----------------------------------------------------------------------------
load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "recipes.csv"

st.set_page_config(
    page_title="GourmetAI - Smart Recipe & Meal Assistant",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# CSS Design System & Professional Typography
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.02em;
    }

    /* Hero Header Styling */
    .hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
    }
    .hero-container::before {
        content: "";
        position: absolute;
        top: -60%;
        right: -10%;
        width: 380px;
        height: 380px;
        background: radial-gradient(circle, rgba(249, 115, 22, 0.25) 0%, rgba(234, 88, 12, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(120deg, #ffffff 40%, #fdba74 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem 0;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0 0 1.2rem 0;
        max-width: 720px;
        line-height: 1.6;
    }
    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        align-items: center;
    }
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.08);
        color: #e2e8f0;
        border: 1px solid rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(4px);
    }

    /* Engine Status Badges */
    .badge-genai {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }
    .badge-local {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
    }

    /* Recipe Cards */
    .recipe-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.8rem;
        margin-bottom: 1rem;
    }
    .recipe-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-right: 0.4rem;
    }
    .tag-cuisine {
        background: #e0f2fe;
        color: #0369a1;
    }
    .tag-diet {
        background: #dcfce7;
        color: #15803d;
    }
    .tag-diff-easy {
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    .tag-diff-med {
        background: #fefce8;
        color: #854d0e;
        border: 1px solid #fef08a;
    }

    /* Ingredient Chips */
    .chip-matched {
        display: inline-block;
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.84rem;
        font-weight: 500;
        margin: 0.2rem;
    }
    .chip-missing {
        display: inline-block;
        background: #fff7ed;
        color: #c2410c;
        border: 1px solid #ffedd5;
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.84rem;
        font-weight: 600;
        margin: 0.2rem;
    }

    /* Pro Tip Callout */
    .chef-tip-box {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 0 12px 12px 0;
        padding: 0.85rem 1.2rem;
        margin: 1rem 0;
        color: #78350f;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    /* Step Timeline */
    .step-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 0.75rem;
        line-height: 1.5;
    }
    .step-number {
        min-width: 26px;
        height: 26px;
        border-radius: 50%;
        background: #ea580c;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 0.75rem;
        margin-top: 0.15rem;
    }

    /* Metrics Bar */
    .metric-pill {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        text-align: center;
    }
    .metric-pill-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }
    .metric-pill-value {
        font-size: 1.15rem;
        color: #0f172a;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data Models for Structured Output
# -----------------------------------------------------------------------------
class IngredientItem(BaseModel):
    name: str = Field(description="Ingredient name")
    quantity: str = Field(description="Portioned quantity and measurement unit")


class RecipeResult(BaseModel):
    recipe_name: str
    cuisine: str
    dietary_fit: str
    cooking_time_minutes: int
    prep_time_minutes: int = Field(default=10, description="Preparation and chopping time in minutes")
    difficulty: str = Field(default="Easy", description="Difficulty: Easy, Intermediate, or Advanced")
    estimated_calories: int = Field(default=420, description="Estimated calories per serving in kcal")
    servings: int
    why_it_fits: str
    ingredients: list[IngredientItem]
    missing_ingredients: list[str]
    steps: list[str]
    shopping_list: list[str]
    safety_note: str
    chef_tip: str = Field(
        default="Sauté aromatics gently on low heat to maximize flavor extraction.",
        description="Chef's secret technique for enhancing taste and aroma",
    )


class RecommendationResponse(BaseModel):
    recommendations: list[RecipeResult]
    general_note: str


# -----------------------------------------------------------------------------
# Dataset & Preprocessing Helpers
# -----------------------------------------------------------------------------
@st.cache_data
def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        # Safety fallback if file is moved
        return pd.DataFrame([
            {"recipe_name": "Egg Fried Rice", "cuisine": "Asian", "diet": "Non-Vegetarian|Any", "cooking_time_minutes": 20, "ingredients": "rice|egg|onion|garlic|oil|soy sauce"}
        ])
    return pd.read_csv(DATA_PATH)


def normalize(text: str) -> str:
    return (
        str(text)
        .lower()
        .strip()
        .replace("-", " ")
        .replace("_", " ")
    )


def split_ingredients(text: str) -> list[str]:
    return [normalize(x) for x in str(text).split("|") if str(x).strip()]


def local_recipe_candidates(
    df: pd.DataFrame,
    available: list[str],
    cuisine: str,
    diet: str,
    max_time: int,
    servings: int,
) -> pd.DataFrame:
    available_norm = set(normalize(x) for x in available if x.strip())

    rows = []
    for _, row in df.iterrows():
        if cuisine != "Any" and row["cuisine"] != cuisine:
            continue
        if diet != "Any" and diet not in str(row["diet"]).split("|"):
            continue
        if int(row["cooking_time_minutes"]) > max_time:
            continue

        recipe_ingredients = split_ingredients(row["ingredients"])
        matched = sum(
            any(a in ingredient or ingredient in a for a in available_norm)
            for ingredient in recipe_ingredients
            for a in available_norm
        )
        missing = [
            ing for ing in recipe_ingredients
            if not any(a in ing or ing in a for a in available_norm)
        ]
        coverage = matched / max(1, len(recipe_ingredients))

        rows.append({
            "recipe_name": row["recipe_name"],
            "cuisine": row["cuisine"],
            "diet": row["diet"],
            "cooking_time_minutes": int(row["cooking_time_minutes"]),
            "servings": int(servings),
            "ingredients": row["ingredients"],
            "matched_count": matched,
            "coverage": coverage,
            "missing_count": len(missing),
        })

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    return result.sort_values(
        ["coverage", "matched_count", "missing_count"],
        ascending=[False, False, True],
    ).head(5)


# -----------------------------------------------------------------------------
# API Client Resolvers
# -----------------------------------------------------------------------------
def get_gemini_api_key() -> str:
    if st.session_state.get("gemini_key_input"):
        return st.session_state["gemini_key_input"].strip()
    return (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()


def get_tavily_api_key() -> str:
    if st.session_state.get("tavily_key_input"):
        return st.session_state["tavily_key_input"].strip()
    return (os.getenv("TAVILY_API_KEY") or "").strip()


def get_gemini_client():
    key = get_gemini_api_key()
    if not key:
        return None
    return genai.Client(api_key=key)


def get_tavily_client():
    key = get_tavily_api_key()
    if not key:
        return None
    return TavilyClient(api_key=key)


# -----------------------------------------------------------------------------
# Dual-Engine Recommendation Logic
# -----------------------------------------------------------------------------
def generate_local_fallback(
    available: list[str],
    cuisine: str,
    diet: str,
    max_time: int,
    servings: int,
    candidates: pd.DataFrame,
) -> RecommendationResponse:
    available_norm = set(normalize(x) for x in available if x.strip())
    recipes_list = []

    sample_steps = {
        "rice": [
            "Rinse rice/grains thoroughly and prepare your aromatics (dice onions, mince garlic).",
            "Heat cooking oil in a wok or deep skillet over medium-high heat until shimmering.",
            "Add aromatics first; stir-fry for 1 minute until fragrant.",
            "Incorporate protein or vegetables and cook through.",
            "Fold in cooked grains, seasoning with soy sauce, pepper, or salt to taste.",
            "Toss continuously for 2 minutes to distribute heat evenly and serve steaming hot.",
        ],
        "curry": [
            "Wash, peel, and dice all vegetables, aromatics, and proteins.",
            "Heat oil in a heavy-bottomed pot; bloom whole spices over low heat for 30 seconds.",
            "Add diced onions, minced ginger, and garlic; sauté until golden translucent.",
            "Add chopped tomatoes and ground spices; simmer on medium until oil separates from gravy.",
            "Add legumes, paneer, or vegetables along with water; simmer gently until tender and rich.",
            "Finish with fresh herbs, adjust salt, and serve with rice or flatbread.",
        ],
        "pasta": [
            "Bring a generous pot of heavily salted water to a rolling boil; cook pasta until al dente.",
            "Meanwhile, warm olive oil in a wide skillet over medium heat with sliced garlic.",
            "Add vegetables, mushrooms, or sauce base, simmering gently to develop aroma.",
            "Transfer pasta directly into the sauce along with 3 tablespoons of starchy pasta water.",
            "Toss and emulsify vigorously for 60 seconds until a silky sauce coats each strand.",
            "Garnish with freshly cracked black pepper and herbs; serve immediately.",
        ],
        "default": [
            "Wash, chop, and organize all ingredients in mis-en-place bowls.",
            "Preheat a non-stick skillet or pan over medium heat with cooking oil or butter.",
            "Sauté aromatics first to build a solid foundational flavor profile.",
            "Add remaining ingredients in order of density and required cooking time.",
            "Cook until tender and thoroughly heated through, seasoning with salt and pepper to taste.",
            "Plate cleanly and enjoy fresh.",
        ],
    }

    chef_tips_map = {
        "rice": "💡 Chef Tip: For best results in stir-fries, use day-old chilled rice so the grains stay separate and don't turn mushy.",
        "curry": "💡 Chef Tip: Sauté your onions slowly until golden brown; this caramelization creates the rich depth in curries.",
        "pasta": "💡 Chef Tip: Never rinse cooked pasta in water! The natural starches help the sauce cling to every bite.",
        "default": "💡 Chef Tip: Season in layers throughout cooking rather than only at the very end for richer, well-rounded flavors.",
    }

    for _, row in candidates.head(3).iterrows():
        raw_ings = split_ingredients(row["ingredients"])
        missing = [
            ing for ing in raw_ings
            if not any(a in ing or ing in a for a in available_norm)
        ]

        name_lower = row["recipe_name"].lower()
        if "rice" in name_lower or "noodles" in name_lower:
            steps = sample_steps["rice"]
            tip = chef_tips_map["rice"]
            est_cal = 420
        elif any(k in name_lower for k in ["curry", "masala", "dal", "rajma", "chana", "aloo"]):
            steps = sample_steps["curry"]
            tip = chef_tips_map["curry"]
            est_cal = 380
        elif "pasta" in name_lower:
            steps = sample_steps["pasta"]
            tip = chef_tips_map["pasta"]
            est_cal = 490
        else:
            steps = sample_steps["default"]
            tip = chef_tips_map["default"]
            est_cal = 340

        cook_time = int(row["cooking_time_minutes"])
        difficulty = "Easy" if cook_time <= 20 else "Intermediate" if cook_time <= 35 else "Advanced"

        ing_items = [
            IngredientItem(
                name=ing.title(),
                quantity=(
                    f"{servings * 60}g"
                    if any(w in ing for w in ["rice", "pasta", "chickpeas", "lentils", "beans", "paneer"])
                    else f"{servings} unit(s)"
                    if any(w in ing for w in ["egg", "tomato", "onion", "potato", "tortilla", "bread"])
                    else "1-2 tbsp / To taste"
                ),
            )
            for ing in raw_ings
        ]

        recipes_list.append(
            RecipeResult(
                recipe_name=row["recipe_name"],
                cuisine=row["cuisine"],
                dietary_fit=row["diet"].split("|")[0] if "|" in row["diet"] else row["diet"],
                cooking_time_minutes=cook_time,
                prep_time_minutes=10 if cook_time < 25 else 15,
                difficulty=difficulty,
                estimated_calories=est_cal,
                servings=int(servings),
                why_it_fits=(
                    f"Matches {row['matched_count']} of your ingredients "
                    f"({row['coverage']*100:.0f}% match coverage) and fits your {cook_time}-minute time limit."
                ),
                ingredients=ing_items,
                missing_ingredients=[m.title() for m in missing],
                steps=steps,
                shopping_list=[f"{m.title()} (needed for recipe)" for m in missing],
                safety_note="Ensure food reaches safe internal temperature (e.g. 74°C / 165°F for poultry/eggs) and refrigerate leftovers within 2 hours.",
                chef_tip=tip,
            )
        )

    return RecommendationResponse(
        recommendations=recipes_list,
        general_note=(
            "✨ Dishes matched from our curated culinary dataset. "
            "Add your Gemini API Key in the sidebar to unlock personalized AI flavor reasoning!"
        ),
    )


def generate_recommendations(
    available: list[str],
    cuisine: str,
    diet: str,
    max_time: int,
    servings: int,
    candidates: pd.DataFrame,
) -> RecommendationResponse:
    client = get_gemini_client()
    if client is None:
        return generate_local_fallback(
            available, cuisine, diet, max_time, servings, candidates
        )

    candidate_text = candidates.to_dict(orient="records")
    prompt = f"""
You are the AI reasoning and NLP layer of a professional, student-friendly recipe assistant.

USER INPUT
Available ingredients: {available}
Cuisine preference: {cuisine}
Dietary preference: {diet}
Maximum cooking time: {max_time} minutes
Desired servings: {servings}

LOCAL CANDIDATE RECIPES
{json.dumps(candidate_text, indent=2)}

TASK
1. Recommend up to 3 suitable dishes ONLY from the candidate recipes above.
2. Keep cooking time <= {max_time} minutes.
3. Respect dietary and cuisine preferences.
4. Distinguish ingredients the user has from missing ingredients.
5. Provide realistic prep_time_minutes, difficulty (Easy/Intermediate/Advanced), and estimated_calories.
6. Create an actionable shopping list containing only missing items.
7. Give clear step-by-step instructions.
8. Provide a valuable, actionable chef_tip for each dish.
9. Add a short food-safety note.

Return JSON strictly matching the schema.
"""

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RecommendationResponse,
            "system_instruction": (
                "You are an expert culinary assistant. "
                "Be concise, practical, transparent about missing ingredients, "
                "and never claim an ingredient is available unless it appears in the user's provided list."
            ),
        },
    )

    if getattr(response, "parsed", None):
        return response.parsed

    return RecommendationResponse.model_validate_json(response.text)


def tavily_recipe_search(recipe_name: str, cuisine: str):
    client = get_tavily_client()
    if client is None:
        return []

    query = f"{recipe_name} {cuisine} recipe cooking method ingredients"
    try:
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=3,
            include_answer=False,
        )
        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "Recipe source"),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            })
        return results
    except Exception:
        return []


# -----------------------------------------------------------------------------
# Main Application UI
# -----------------------------------------------------------------------------

# Hero Banner
has_gemini = bool(get_gemini_api_key())
engine_badge = (
    '<span class="badge-genai">● Gemini 2.5 Flash Active</span>'
    if has_gemini
    else '<span class="badge-local">● Local Curated Engine Active</span>'
)

st.markdown(
    f"""
    <div class="hero-container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
            <div>
                <h1 class="hero-title">🍳 GourmetAI Assistant</h1>
                <p class="hero-subtitle">
                    Transform the ingredients already in your pantry into restaurant-worthy, healthy meals.
                    Powered by NLP text normalization, deterministic recipe filtering, and Google Gemini GenAI.
                </p>
                <div class="hero-badges">
                    <span class="hero-pill">⚡ 30-Min Quick Prep</span>
                    <span class="hero-pill">🛒 Zero-Waste Shopping List</span>
                    <span class="hero-pill">📊 Nutritional Estimates</span>
                    <span class="hero-pill">🎓 Student-Friendly</span>
                </div>
            </div>
            <div style="text-align:right;">
                {engine_badge}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sidebar: Controls, Presets & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    with st.expander("🔑 API Key Configuration", expanded=not has_gemini):
        st.caption("Provide your keys here or configure them in `.env`.")
        st.text_input(
            "Google Gemini API Key",
            type="password",
            key="gemini_key_input",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Free key from https://aistudio.google.com/. If empty, local engine runs without errors.",
        )
        st.text_input(
            "Tavily Search API Key (Optional)",
            type="password",
            key="tavily_key_input",
            value=os.getenv("TAVILY_API_KEY", ""),
            help="Optional for real-time web recipe enrichment.",
        )

    st.markdown("---")
    st.markdown("### ⚡ Quick Ingredient Presets")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🍚 Student Classic", use_container_width=True):
            st.session_state["default_ingredients"] = "rice, egg, onion, garlic, oil, soy sauce"
            st.session_state["default_cuisine"] = "Asian"
    with col_p2:
        if st.button("🌿 Indian Veg", use_container_width=True):
            st.session_state["default_ingredients"] = "chickpeas, tomato, onion, garlic, ginger, oil, cumin"
            st.session_state["default_cuisine"] = "Indian"

    st.markdown("### 🧑‍🍳 Your Meal Preferences")
    initial_ingredients = st.session_state.get(
        "default_ingredients", "rice, onion, tomato, egg, garlic, oil"
    )
    available_text = st.text_area(
        "Available ingredients in your kitchen",
        value=initial_ingredients,
        help="Type any ingredients you have, separated by commas.",
        height=100,
    )

    df_dataset = load_dataset()
    cuisine_options = ["Any"] + sorted(df_dataset["cuisine"].unique().tolist())
    default_cuisine_index = (
        cuisine_options.index(st.session_state["default_cuisine"])
        if "default_cuisine" in st.session_state and st.session_state["default_cuisine"] in cuisine_options
        else 0
    )
    cuisine = st.selectbox("Cuisine preference", cuisine_options, index=default_cuisine_index)

    diet = st.selectbox(
        "Dietary requirement",
        ["Any", "Vegetarian", "Non-Vegetarian", "Vegan"],
    )

    max_time = st.slider(
        "Max total cooking time (minutes)",
        min_value=10,
        max_value=90,
        value=35,
        step=5,
    )

    servings = st.number_input(
        "Servings",
        min_value=1,
        max_value=8,
        value=2,
        step=1,
    )

    use_tavily = st.checkbox(
        "Enrich with Tavily web recipes",
        value=True,
    )

    recommend_button = st.button(
        "✨ Recommend My Meals",
        type="primary",
        use_container_width=True,
    )

# -----------------------------------------------------------------------------
# Execution Trigger
# -----------------------------------------------------------------------------
if recommend_button:
    available = [x.strip() for x in available_text.split(",") if x.strip()]
    candidates = local_recipe_candidates(
        df_dataset, available, cuisine, diet, max_time, int(servings)
    )

    if candidates.empty:
        st.error(
            "⚠️ No recipes in the database matched all strict filters. "
            "Try increasing the maximum cooking time or setting Cuisine/Diet to 'Any'."
        )
    else:
        with st.spinner("🧑‍🍳 Matching pantry items, analyzing flavors, and formulating recipes..."):
            try:
                result = generate_recommendations(
                    available, cuisine, diet, max_time, int(servings), candidates
                )
                st.session_state["last_result"] = result
                st.session_state["last_input"] = {
                    "available": available,
                    "cuisine": cuisine,
                    "diet": diet,
                    "max_time": max_time,
                    "servings": int(servings),
                    "use_tavily": use_tavily,
                }
            except Exception as exc:
                st.error(f"Generation encountered an issue: {exc}")

# -----------------------------------------------------------------------------
# Tabs Layout
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🍽️ Recommended Dishes",
    "💬 Chef AI Chat",
    "📊 Dataset & Architecture",
    "🥗 Nutrition & Pantry Guide",
])

# -----------------------------------------------------------------------------
# Tab 1: Recommendations
# -----------------------------------------------------------------------------
with tab1:
    if "last_result" not in st.session_state:
        st.info(
            "👋 **Ready to cook?** Select your preferences in the sidebar and click "
            "**'✨ Recommend My Meals'** to generate customized recipes tailored to your pantry!"
        )

        # Quick preview of features
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                """
                <div class="metric-pill">
                    <div style="font-size:1.8rem;">🧂</div>
                    <div style="font-weight:700; margin-top:0.4rem;">Smart Inventory Match</div>
                    <div style="color:#64748b; font-size:0.85rem; margin-top:0.2rem;">
                        Identifies exact matches vs missing ingredients to eliminate food waste.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
                <div class="metric-pill">
                    <div style="font-size:1.8rem;">⏱️</div>
                    <div style="font-weight:700; margin-top:0.4rem;">Time-Bounded Prep</div>
                    <div style="color:#64748b; font-size:0.85rem; margin-top:0.2rem;">
                        Filters dishes strictly within your available schedule and skill level.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                """
                <div class="metric-pill">
                    <div style="font-size:1.8rem;">🛒</div>
                    <div style="font-weight:700; margin-top:0.4rem;">Targeted Shopping List</div>
                    <div style="color:#64748b; font-size:0.85rem; margin-top:0.2rem;">
                        Automatically isolates missing items into a quick one-click grocery list.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        result = st.session_state["last_result"]
        saved = st.session_state["last_input"]

        st.success(result.general_note)

        for idx, recipe in enumerate(result.recommendations, start=1):
            diff_class = (
                "tag-diff-easy"
                if recipe.difficulty == "Easy"
                else "tag-diff-med"
            )

            with st.container(border=True):
                # Header row
                col_h1, col_h2 = st.columns([3, 1])
                with col_h1:
                    st.markdown(
                        f"""
                        <div style="display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap;">
                            <h3 style="margin:0; font-size:1.5rem;">{idx}. {recipe.recipe_name}</h3>
                            <span class="recipe-tag tag-cuisine">{recipe.cuisine}</span>
                            <span class="recipe-tag tag-diet">{recipe.dietary_fit}</span>
                            <span class="recipe-tag {diff_class}">{recipe.difficulty}</span>
                        </div>
                        <p style="color:#475569; margin-top:0.4rem; font-size:0.95rem;">
                            <strong>Why it fits:</strong> {recipe.why_it_fits}
                        </p>
                        """,
                        unsafe_allow_html=True,
                    )

                # Key Metrics Strip
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Prep Time", f"{recipe.prep_time_minutes} min")
                m2.metric("Cook Time", f"{recipe.cooking_time_minutes} min")
                m3.metric("Total Time", f"{recipe.prep_time_minutes + recipe.cooking_time_minutes} min")
                m4.metric("Servings", f"{recipe.servings} people")
                m5.metric("Est. Calories", f"~{recipe.estimated_calories} kcal")

                st.markdown("---")

                # Ingredients & Shopping List
                c_ing, c_shop = st.columns(2)
                with c_ing:
                    st.markdown("#### 🧂 Required Ingredients")
                    user_avail_norm = set(normalize(x) for x in saved["available"])
                    for item in recipe.ingredients:
                        is_avail = any(
                            normalize(a) in normalize(item.name) or normalize(item.name) in normalize(a)
                            for a in user_avail_norm
                        )
                        if is_avail:
                            st.markdown(
                                f'<span class="chip-matched">✓ {item.name} ({item.quantity})</span>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f'<span class="chip-missing">+ {item.name} ({item.quantity})</span>',
                                unsafe_allow_html=True,
                            )

                with c_shop:
                    st.markdown("#### 🛒 Grocery Checklist")
                    if recipe.shopping_list:
                        for s_item in recipe.shopping_list:
                            st.checkbox(s_item, key=f"shop_{idx}_{s_item}")
                    else:
                        st.success("🎉 You already have 100% of the required ingredients!")

                # Step-by-Step Instructions
                st.markdown("#### 👨‍🍳 Step-by-Step Instructions")
                for s_num, step in enumerate(recipe.steps, start=1):
                    st.markdown(
                        f"""
                        <div class="step-item">
                            <div class="step-number">{s_num}</div>
                            <div>{step}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Chef's Secret Tip
                st.markdown(
                    f"""
                    <div class="chef-tip-box">
                        <strong>🧑‍🍳 Chef's Secret:</strong> {recipe.chef_tip}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.caption(f"🛡️ **Food Safety Note:** {recipe.safety_note}")

                # Optional Tavily Web Results
                if saved.get("use_tavily"):
                    with st.expander("🌐 Additional Web Recipes & Inspiration (Tavily)"):
                        with st.spinner("Searching verified culinary web sources..."):
                            sources = tavily_recipe_search(recipe.recipe_name, recipe.cuisine)
                        if not sources:
                            st.caption(
                                "Tavily search is inactive. Add a valid TAVILY_API_KEY to fetch live web articles."
                            )
                        else:
                            for src in sources:
                                st.markdown(f"**[{src['title']}]({src['url']})**")
                                st.caption(src["content"][:400] + "...")

# -----------------------------------------------------------------------------
# Tab 2: Interactive Chef AI Chat
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("💬 Interactive Culinary Chat Assistant")
    st.caption(
        "Ask questions directly about your recommended dish: request spice adjustments, "
        "substitute ingredients, or get beginner cooking techniques."
    )

    # Quick Suggestion Chips
    st.markdown("**Quick Prompts:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    quick_query = None
    with qc1:
        if st.button("🌶️ Make it Spicier", use_container_width=True):
            quick_query = "How can I make this dish spicier and bolder in flavor?"
    with qc2:
        if st.button("🔄 Swap Ingredients", use_container_width=True):
            quick_query = "What common kitchen items can I substitute for the missing ingredients?"
    with qc3:
        if st.button("⏱️ Quick 15-Min Version", use_container_width=True):
            quick_query = "How can I speed up cooking to finish within 15 minutes?"
    with qc4:
        if st.button("🥗 Side Dish Ideas", use_container_width=True):
            quick_query = "What easy side dish or drink pairs best with this meal?"

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_question = st.chat_input("Ask a culinary question...") or quick_query

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        client = get_gemini_client()

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            if client is None:
                fallback_answer = (
                    f"💬 **Culinary Advice on '{user_question}':**\n\n"
                    "• **Flavor Adjustments:** Start with small increments (1/4 tsp) of spices like chili flakes, cumin, or pepper, tasting as you cook.\n"
                    "• **Substitutions:** Almost all aromatics (garlic, onion) can be swapped with dried powders or shallots. Acidic balance can come from lemon or vinegar.\n\n"
                    "💡 *Note: To activate real-time Gemini AI chat for deep conversational reasoning, add your **GEMINI_API_KEY** in the sidebar settings.*"
                )
                st.markdown(fallback_answer)
                st.session_state.chat_history.append({"role": "assistant", "content": fallback_answer})
            else:
                last_rec_context = (
                    st.session_state["last_result"].model_dump_json(indent=2)
                    if "last_result" in st.session_state
                    else "No prior recommendations generated yet."
                )
                chat_prompt = f"""
You are a friendly, expert culinary chef helping a student cook a meal.

CURRENT RECOMMENDATIONS CONTEXT:
{last_rec_context}

USER QUESTION:
{user_question}

Provide actionable, practical cooking advice in concise markdown bullet points.
"""
                try:
                    with st.spinner("Chef is formulating advice..."):
                        response = client.models.generate_content(
                            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                            contents=chat_prompt,
                        )
                        reply = response.text
                        st.markdown(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                except Exception as exc:
                    st.error(f"Chat error: {exc}")

# -----------------------------------------------------------------------------
# Tab 3: Dataset Analytics & Architecture
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📊 Dataset Distribution & Algorithmic Pipeline")

    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.markdown("#### Recipes by Cuisine")
        cuisine_chart = (
            alt.Chart(df_dataset)
            .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
            .encode(
                x=alt.X("count():Q", title="Total Recipes"),
                y=alt.Y("cuisine:N", sort="-x", title="Cuisine"),
                color=alt.Color("cuisine:N", legend=None, scale=alt.Scale(scheme="tableau10")),
                tooltip=["cuisine", "count()"],
            )
            .properties(height=260)
        )
        st.altair_chart(cuisine_chart, use_container_width=True)

    with c_g2:
        st.markdown("#### Average Cooking Times (Minutes)")
        time_chart = (
            alt.Chart(df_dataset)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("cuisine:N", title="Cuisine"),
                y=alt.Y("mean(cooking_time_minutes):Q", title="Average Time (min)"),
                color=alt.Color("cuisine:N", legend=None, scale=alt.Scale(scheme="category10")),
                tooltip=["cuisine", "mean(cooking_time_minutes):Q"],
            )
            .properties(height=260)
        )
        st.altair_chart(time_chart, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🔄 Dual-Engine Architecture")
    st.code(
        """
  User Input (Ingredients, Cuisine, Dietary, Max Time, Servings)
                             │
                             ▼
                 [Text Normalization & NLP]
              (Tokenize, strip, lowercase, match)
                             │
                             ▼
              [Deterministic Dataset Filtering]
           (Candidate scoring: coverage, match count)
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
       [If Gemini API Key]          [If No API Key]
     Google Gemini 2.5 Flash       Local Curated Engine
   (Structured Pydantic JSON)     (Deterministic synthesis)
              │                             │
              └──────────────┬──────────────┘
                             ▼
     [Interactive Streamlit Cards, Metrics & Chat]
        """,
        language="text",
    )

    st.markdown("#### 📋 Complete Synthetic Dataset")
    st.dataframe(df_dataset, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# Tab 4: Nutrition & Student Pantry Guide
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("🥗 Nutrition & Student Pantry Essentials")

    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.markdown(
            """
            ### 🥦 Healthy Plate Guidelines
            - **50% Vegetables & Fruits:** Include tomatoes, spinach, carrots, onions, and bell peppers for vitamins and minerals.
            - **25% Complex Carbohydrates:** Brown rice, whole-grain pasta, oats, and potatoes provide sustained energy for study sessions.
            - **25% Lean Protein:** Eggs, paneer, lentils, chickpeas, and chicken for muscle repair and satiety.
            - **Healthy Fats:** Use minimal olive oil or mustard oil for essential fatty acids.
            """
        )
    with col_n2:
        st.markdown(
            """
            ### 🥫 Top 8 Pantry Essentials to Stock
            1. **Cooking Oil:** Neutral vegetable oil or olive oil.
            2. **Aromatics:** Fresh onions and garlic heads (last weeks without refrigeration).
            3. **Canned/Dry Legumes:** Chickpeas, black beans, red kidney beans, and yellow lentils.
            4. **Long-Grain Rice & Pasta:** Reliable carbohydrate foundations.
            5. **Basic Spices:** Salt, black pepper, turmeric, cumin, and chili flakes.
            6. **Eggs:** Versatile, high-protein, and cook in under 10 minutes.
            7. **Soy Sauce / Vinegar:** Instantly elevates basic stir-fries.
            8. **Tomatoes:** Canned or fresh for curries and sauces.
            """
        )
