# GMD PROJECT - MY SYMPTOMS

##  How to Launch the Website


- `pip install -r requirements.txt`
- Run **Elasticsearch 8.17.2** with **Docker**
- Execute the indexing scripts 
- Create a `.env` file with your `OPENAI_API_KEY`
- Start the Flask server: `python3 app.py`

(To preview the interface and features: open `diapo.pdf`)

## Description

This project acts as a mediator between multiple medical databases to identify:

- Probable **causes** of symptoms (diseases or side effects)
- Possible **treatments**
- All enhanced with intelligent filters like:
  - `AND` / `OR` logic between symptoms
  - Wildcard support (e.g., `head*`)
  - Data **sources**, **scoring**, and **statistics**
  - Modern **user interface** with visual enhancements

## WOW Factor – AI Assistance

A built-in AI chatbot powered by an LLM (Language Model) helps the user **analyze results**.

- It can ask relevant medical questions
- It remembers the conversation context
- It eventually gives a **likely diagnosis and treatment**
- All based strictly on the results 
## Documentation

For full technical details, data mappings, and screenshots, see `diapo.pdf`