# Dev.to Guardian Agent — The Coral Lookout

A Coral-powered moderation dashboard that:
- pulls Dev.to articles through Coral SQL,
- classifies threats with an optional LLM path and a strong offline fallback,
- presents the feed as a pirate-style personal-agent activity log,
- keeps the Coral source mapping visible for judges.

## Run locally

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

If Coral is available:

```bash
coral source add --file coral/devto_guardian_connector.yaml
coral source lint coral/devto_guardian_connector.yaml
coral sql "SELECT id, title, description, url FROM devto_agent.articles LIMIT 15"
```

## Notes

- The dashboard now uses a pirate-themed personal-agent UI inspired by the Stitch mockup.
- If no API key is set, the scanner uses a deterministic heuristic fallback.
- The app no longer depends on `from google import genai`, which avoids the deployment import error you hit on Railway.
- The sidebar shows the Dev.to article-array mapping, and the active data source here is Dev.to.
