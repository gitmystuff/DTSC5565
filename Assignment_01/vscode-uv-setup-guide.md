# Setting Up VS Code and uv

A one-time setup so everyone has a working local Python environment for
building agents. Do this once — you'll reuse this environment for the
rest of the semester.

---

## Why uv?

`uv` is a fast, all-in-one replacement for pip, venv, and virtual
environment management. Instead of juggling separate tools and commands
to create a virtual environment, install packages, and track what's
installed, `uv` handles all of it with one consistent command-line tool.
It's also dramatically faster than pip at installing packages, which
matters when you're setting up an environment live in class.

---

## Step 1: Install VS Code

1. Go to **code.visualstudio.com** and download the installer for your OS
   (Windows / Mac / Linux)
2. Run the installer, accepting the defaults
3. Open VS Code once to confirm it launches

## Step 2: Install the Python extension

1. In VS Code, click the **Extensions** icon in the left sidebar (four
   squares)
2. Search for **Python** (the official Microsoft one, published by
   "Microsoft")
3. Click **Install**

## Step 3: Install uv

**Mac / Linux** — open a terminal (VS Code has one built in: Terminal →
New Terminal) and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** — open PowerShell and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, **close and reopen your terminal** (this matters —
uv won't be recognized until your terminal reloads its PATH).

## Step 4: Verify the install

```bash
uv --version
```

You should see a version number printed. If you get "command not found,"
see Troubleshooting below.

## Step 5: Create your project folder

Pick a location for your work (e.g., a folder called `agent-assignment`),
then in the terminal:

```bash
mkdir agent-assignment
cd agent-assignment
uv init
```

This creates a small starter project structure, including a
`pyproject.toml` file that tracks your project's dependencies.

## Step 6: Add the packages you'll need

```bash
uv add groq python-dotenv
```

This installs the Groq Python SDK and `python-dotenv` (for loading your
API key from a `.env` file), and automatically creates a `.venv` virtual
environment in your project folder if one doesn't exist yet.

## Step 7: Store your Groq API key safely

Create a file named `.env` in your project folder:

```
GROQ_API_KEY=your_key_here
```

Then create a `.gitignore` file (if you don't already have one) and add:

```
.env
.venv
```

**Do this before your first commit.** This is the step people forget, and
it's the one that causes a key to end up on GitHub.

## Step 8: Open the project in VS Code and select the right interpreter

1. In VS Code, **File → Open Folder**, and open your `agent-assignment`
   folder
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the
   command palette
3. Type **Python: Select Interpreter** and choose the one located inside
   your project's `.venv` folder (it will usually be listed near the top,
   marked as recommended)

## Step 9: Confirm everything works

Create a file called `hello.py` with:

```python
print("Environment is working.")
```

Run it with:

```bash
uv run hello.py
```

You should see the message printed. `uv run` automatically uses your
project's virtual environment — you never need to manually "activate" it.

---

## Troubleshooting

| Problem | Likely fix |
|---|---|
| `uv: command not found` after install | Close and fully reopen your terminal (and VS Code, if the integrated terminal still doesn't see it) |
| VS Code doesn't show your `.venv` interpreter | Run `uv run python -c "print(1)"` once first to make sure the environment is fully created, then re-run "Python: Select Interpreter" |
| `uv add` fails with a permissions error | Make sure you're not inside a system-protected folder (e.g. avoid Program Files on Windows) — use a folder in your user directory |
| Script runs but can't find `GROQ_API_KEY` | Confirm `.env` is in the same folder as your script, and that you're loading it with `load_dotenv()` before reading the variable |
| Windows PowerShell blocks the install script | Right-click PowerShell and "Run as Administrator," or check that script execution isn't fully disabled by your machine's policy |

---

## Quick reference: commands you'll use again

```bash
uv init                 # start a new project
uv add <package>        # install a package into this project
uv run <script.py>      # run a script using this project's environment
uv run python           # start a Python shell in this project's environment
```
