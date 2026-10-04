# 🍳 AI Recipe & Meal Recommendation Assistant

A beginner-friendly LLM / GenAI / NLP bootcamp project based directly on the provided problem statement.

## Problem

Students with limited cooking experience may not know what to prepare from ingredients they already have.

The application accepts:
- Available ingredients
- Cuisine preference
- Cooking-time limit
- Serving size
- Dietary preference

It then:
1. Normalizes the ingredient input.
2. Filters a small synthetic recipe dataset.
3. Uses Gemini for NLP interpretation and structured recipe generation.
4. Identifies missing ingredients.
5. Creates a shopping list.
6. Gives simple step-by-step instructions.
7. Optionally uses Tavily to retrieve additional public recipe information.
8. Presents everything through Streamlit.

## Technology stack

- Python
- Streamlit
- Gemini API / `google-genai`
- Pydantic structured output
- Tavily API / `tavily-python`
- pandas
- Synthetic CSV dataset

## Folder structure

```text
ai_recipe_meal_assistant/
│
├── app.py
├── generate_data.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
└── data/
    └── recipes.csv
```

## Setup on Windows

### 1. Open the project folder

Open PowerShell / CMD in this folder.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

CMD:

```cmd
.venv\Scripts\activate
```

### 4. Install packages

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

Copy `.env.example` to `.env`.

Put your own API keys into:

```text
GEMINI_API_KEY=...
TAVILY_API_KEY=...
```

Do NOT upload `.env` to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

The browser should open the Streamlit application.

## Suggested demo input

```text
rice, onion, tomato, egg, garlic, oil
```

Cuisine:

```text
Indian
```

Diet:

```text
Non-Vegetarian
```

Time:

```text
30 minutes
```

Servings:

```text
2
```

This should demonstrate the complete input → processing → AI → search → response flow.

## What each technology does

### Python
Application logic, data processing, API integration.

### Streamlit
Creates the interactive UI without requiring frontend JavaScript.

### NLP
Ingredient text is normalized and interpreted from the user's natural-language input. Gemini then converts the user's request into a recipe recommendation task.

### Gemini
Generates the final structured recommendations, ingredients, missing ingredients, steps, shopping list, and safety note.

### Pydantic
Defines the expected structured JSON schema for Gemini output. This makes the AI response easier to validate and display reliably.

### Tavily
Optional web-search enrichment for additional public recipe information.

### Synthetic dataset
A small CSV dataset is included because the problem statement explicitly permits synthetic data.

## Responsible AI

This is a prototype, not a food-safety authority. Users should verify:
- allergies
- dietary restrictions
- ingredient labels
- cooking temperatures
- food storage and handling

The app also distinguishes its synthetic local dataset from external Tavily search results.
