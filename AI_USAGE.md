# AI Usage Documentation

## Tools Used

- ChatGPT used as primary assistant for installation instructions, Flask routes, SQL, and UI

## Key Prompts

1. "How to install Flask and mysql-connector on Mac?"
2. "What Python files act like package.json for listing dependencies?"
3. "Make the UI look more professional"

## What Worked Well

- Fast first drafts for REST-style Flask handlers
- Clear explanations of MySQL **JSON** columns and how they map to Python/Flask responses
- Practical, step-by-step help when diagnosing environment and connection problems (credentials, host, database name)

## What I Modified

- Renamed variables and aligned SQL with my real table/column names
- Separated database connection in `database.py` and raw SQL in a dedicated `queries.py` module instead of embedding long strings only in `app.py`
- Ran tests for API endpoints using Postman
- Refined UI copy, layout, and styling beyond the first AI suggestion so it matched my goals

## Lessons Learned

- AI is useful for simplifying concepts
- It's helpful to have previous Fullstack experience
- I treat AI output as draft code: I review and test it
- Short specific prompts are better than long vague questions
