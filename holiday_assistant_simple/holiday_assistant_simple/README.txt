HOLIDAY ASSISTANT AI — SIMPLE VERSION

1. Keep app.py, requirements.txt, and your private .env file in the same folder.
2. Create .env by copying .env.example.
3. Add your newly generated Gemini API key to .env:
   GEMINI_API_KEY="YOUR_NEW_KEY"
   GEMINI_MODEL=gemini-3.5-flash-lite
4. Open the folder in VS Code and run:
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
5. If Gemini is unavailable, click Load Sample Demo in the sidebar. Those examples are pre-written demo content, not live AI results.

Security: Do not share .env or upload it to GitHub. If a key was shared, revoke it in Google AI Studio and create a new one.
