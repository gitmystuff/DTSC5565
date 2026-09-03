# Getting API Keys: Groq & Hugging Face

A one-time setup, done now so it's not a bottleneck when we reach the agents stage of the course.

---

## Why these two, and why now

| Provider | What it's good for | When you'll use it |
|---|---|---|
| **Groq** | Free tier, very fast inference on open models (Llama, etc.) — good for low-latency, programmatic calls | Agents stage — anywhere code needs to call a model repeatedly in a loop |
| **Hugging Face** | Free tier — model/dataset access, hosting, and the `transformers`/`huggingface_hub` ecosystem | Any week you pull a specific open model or dataset rather than calling a hosted API |

Tests and context/specs (this week and next) don't require either — you can do that work directly in a chat interface. Agents do, because a script needs to call the model on its own, not through a person typing in a chat window.

---

## Getting a Groq API key

1. Go to **console.groq.com**
2. Sign up / log in (GitHub or Google login is fastest)
3. In the left sidebar, click **API Keys**
4. Click **Create API Key**, give it a name (e.g., `cs5565-<yourname>`)
5. **Copy the key immediately** — Groq only shows it once. If you lose it, delete it and create a new one.
6. Store it somewhere safe (see Storing Your Keys Safely, below) — do **not** paste it directly into a notebook cell or commit it to GitHub

Free tier notes: Groq's free tier has generous rate limits for experimentation but is still a shared, metered resource — don't hammer it with tight loops during testing.

---

## Getting a Hugging Face access token

1. Go to **huggingface.co** and sign up / log in
2. Click your profile icon (top right) → **Settings**
3. In the left sidebar, click **Access Tokens**
4. Click **Create new token**
5. Choose a token type:
   - **Read** — sufficient for downloading models/datasets (this is what most of you will need)
   - **Write** — only needed if you're uploading/publishing something to the Hub
6. Name it (e.g., `cs5565-<yourname>`), create it, and **copy it immediately**
7. Store it the same way as your Groq key — never hard-code it

---

## Storing your keys safely

This matters — it's also a preview of the security engineering chapter later in the course (Ch13). A leaked API key in a public GitHub repo gets scraped and abused within minutes.

**In Google Colab:**
- Click the **key icon** in the left sidebar (Secrets)
- Add a new secret, name it (e.g., `GROQ_API_KEY`), paste the value
- Toggle "Notebook access" on
- In code, retrieve it with:
  ```python
  from google.colab import userdata
  groq_key = userdata.get('GROQ_API_KEY')
  ```
- This keeps the key out of the notebook file itself, so it's safe even if you share or submit the notebook

**Outside Colab (local project or anything headed to GitHub):**
- Create a file named `.env` in your project folder:
  ```
  GROQ_API_KEY=your_key_here
  HUGGINGFACE_TOKEN=your_key_here
  ```
- Add `.env` to a `.gitignore` file **before your first commit** — this is the step people forget, and it's the one that causes leaks:
  ```
  .env
  ```
- Load it in Python with `python-dotenv`:
  ```python
  from dotenv import load_dotenv
  import os
  load_dotenv()
  groq_key = os.getenv("GROQ_API_KEY")
  ```

**Never do this:**
- Paste a key directly into a code cell or `.py` file
- Commit a `.env` file to GitHub, even in a private repo
- Share a key over Slack, email, or in a shared doc

If a key is ever accidentally exposed, **revoke/delete it immediately** on the provider's site and generate a new one — don't just remove it from the file and hope nobody saw it.

---

## Quick checklist

- [ ] Groq account created
- [ ] Groq API key generated and saved securely (not in a notebook cell)
- [ ] Hugging Face account created
- [ ] Hugging Face access token generated and saved securely
- [ ] `.env` added to `.gitignore` (if working outside Colab)
- [ ] Test call made to confirm each key works
