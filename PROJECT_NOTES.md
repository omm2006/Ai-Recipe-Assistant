# Bootcamp submission mapping

## Requirement → implementation

| PS requirement | Implementation |
|---|---|
| Conversational recipe assistant | Streamlit Recommendation + Recipe Chat tabs |
| Available ingredients | Sidebar ingredient input |
| Cuisine preference | Cuisine selector |
| Cooking time | Maximum-time slider |
| Serving size | Serving selector |
| Dietary preference | Dietary selector |
| Suitable dishes | Local filtering + Gemini |
| Step-by-step instructions | Gemini structured output |
| Missing ingredients | Gemini output |
| Small shopping list | Gemini output |
| Clear practical format | Streamlit cards, columns, warnings |
| Gemini API | `google-genai` |
| Tavily API | Optional public recipe search |
| Synthetic data | `data/recipes.csv` |
| Beginner-friendly | Simple Python/Streamlit architecture |
| Complete flow | input → NLP → filtering → AI → search → response |

## LLM / GenAI concepts demonstrated

1. Prompt engineering
2. System instructions
3. Structured output
4. Pydantic schema validation
5. Natural-language input interpretation
6. Retrieval/web enrichment
7. Conversational follow-up
8. API integration
9. Responsible AI considerations

## NLP concepts demonstrated

- Text normalization
- Token-like ingredient splitting
- Entity/ingredient matching
- Natural-language preference interpretation
- Query formulation for web search

## Architecture

```text
                    ┌─────────────────────┐
                    │     Streamlit UI    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ NLP preprocessing   │
                    │ ingredient cleanup  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Synthetic CSV       │
                    │ recipe filtering    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Gemini API           │
                    │ structured output   │
                    └──────────┬──────────┘
                               │
                       ┌───────┴────────┐
                       ▼                ▼
                ┌─────────────┐  ┌─────────────┐
                │ Recipe UI   │  │ Tavily      │
                │ + shopping  │  │ web search  │
                └─────────────┘  └─────────────┘
```

## Demo sequence

1. Start Streamlit.
2. Enter ingredients.
3. Choose preferences.
4. Click Recommend.
5. Explain that deterministic filtering narrows the synthetic dataset.
6. Explain that Gemini performs the NLP/GenAI layer and returns validated JSON.
7. Show missing ingredients and shopping list.
8. Open Tavily enrichment.
9. Ask a follow-up in Recipe Chat.
10. Open Dataset & Pipeline to explain the architecture.

## Important limitation

The dataset is synthetic and intentionally small. This is acceptable for the bootcamp prototype because the PS explicitly allows synthetic data. A production system would need a larger curated recipe source, stronger ingredient ontology, allergen handling, source licensing checks, evaluation data, and more robust recipe validation.
