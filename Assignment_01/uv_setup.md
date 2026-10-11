# Setting Up `uv` (and Your Virtual Environment)

`uv` is a fast, modern Python package manager. It replaces the `python -m venv` + `pip install` workflow you may have used before — one tool handles both the virtual environment and the packages inside it. This is what the RAG lab uses.

## 1. Install `uv`

**Mac / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify:**

```bash
uv --version
```

If the command isn't found, close and reopen your terminal (the installer updates your PATH, and existing terminal windows won't see the change until restarted).

## 2. Two Ways to Get a Virtual Environment

### Option A — Automatic (what the RAG lab uses)

If a project already has a `pyproject.toml` (the RAG lab does), you don't create the environment yourself — one command does everything:

```bash
cd deep-learning-rag-agent
uv sync
```

This reads `pyproject.toml`, creates a `.venv` folder in the project directory, and installs every dependency into it. No separate `pip install` needed — `uv sync` is the only command required for this repo.

### Option B — Manual (for your own projects, or general use)

If you're starting a project from scratch with no `pyproject.toml` yet:

```bash
uv venv                 # creates a .venv folder in the current directory
```

Then activate it:

```bash
# Mac / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat
```

Your terminal prompt should now show `(.venv)` at the start of the line — that's your confirmation it's active.

**Install packages into it:**

```bash
uv add pandas scikit-learn        # adds to pyproject.toml AND installs
```

or, for a one-off install without touching `pyproject.toml`:

```bash
uv pip install pandas
```

**Deactivate when you're done:**

```bash
deactivate
```

## 3. Point VS Code at This Environment

After running `uv sync` or `uv venv`, tell VS Code to use it:

1. `Cmd/Ctrl+Shift+P` → **Python: Select Interpreter**
2. Choose the interpreter inside `.venv` (VS Code usually auto-detects and lists it at the top)

See the VS Code setup guide, Step 3, for details.

## 4. Configure the RAG Lab's Environment Variables

After `uv sync` finishes, the RAG lab needs your API keys:

```bash
cp .env.example .env
```

Open `.env` in VS Code and fill in your Groq API key (and Hugging Face token, if deploying to Spaces later). Never commit `.env` to Git — it should already be listed in `.gitignore`, but it's worth checking.

## 5. Verify Everything Is Wired Up

```bash
uv run python -c "import chromadb; import langchain; import langgraph; print('All dependencies OK')"
```

If that prints `All dependencies OK`, your environment is correctly set up.

**Note on `uv run`:** you'll see this prefix a lot instead of just `python`. `uv run` guarantees the command executes inside the project's `.venv`, even if you forgot to activate it manually. When in doubt, prefix with `uv run`.

## Quick Reference

| Command | What it does |
| :--- | :--- |
| `uv sync` | Create/update `.venv` from an existing `pyproject.toml` |
| `uv venv` | Create a blank `.venv` from scratch |
| `uv add <package>` | Add a package to the project and install it |
| `uv pip install <package>` | Install a package without updating `pyproject.toml` |
| `uv run <command>` | Run a command inside the project's `.venv` |
| `source .venv/bin/activate` | Activate the environment manually (Mac/Linux) |
| `deactivate` | Exit the active environment |

## Troubleshooting

| Problem | Fix |
| :--- | :--- |
| `uv: command not found` | Restart your terminal after installing; check PATH was updated |
| `uv sync` fails on a package | Check the error for a missing system dependency (rare); otherwise confirm you're using a supported Python version |
| VS Code doesn't see the `.venv` interpreter | Make sure you ran `uv sync` or `uv venv` **inside** the project folder VS Code has open, then re-run "Python: Select Interpreter" |
| Installed a package but Python says it's missing | You likely installed it outside the activated environment — check for `(.venv)` in your prompt, or just prefix commands with `uv run` |
