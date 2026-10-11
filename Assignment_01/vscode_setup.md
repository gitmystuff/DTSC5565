# Setting Up VS Code

VS Code is the editor we'll use for the RAG lab and beyond. This guide gets you from "never opened it" to "ready to code" in about 10 minutes.

## 1. Install VS Code

Download the installer for your OS from **https://code.visualstudio.com** and run it.

- **Windows:** run the `.exe`, accept defaults. During install, check **"Add to PATH"** if offered — this lets you type `code` from a terminal later.
- **Mac:** open the `.zip`, drag `Visual Studio Code.app` into `Applications`.
- **Linux:** use the `.deb`/`.rpm` from the site, or your package manager (e.g. `sudo snap install code --classic`).

**Verify it worked:** open a terminal and run:

```bash
code --version
```

You should see a version number. If you get "command not found" on Mac/Linux, open VS Code, press `Cmd/Ctrl+Shift+P`, type **Shell Command: Install 'code' command in PATH**, run it, then restart your terminal.

## 2. Install the Required Extensions

Open VS Code, click the **Extensions** icon in the left sidebar (or `Cmd/Ctrl+Shift+X`), and install:

| Extension | Publisher | Why you need it |
| :--- | :--- | :--- |
| **Python** | Microsoft | Python language support, linting, debugging |
| **Jupyter** | Microsoft | Run `.ipynb` notebooks directly in VS Code |
| **GitLens** *(optional)* | GitKraken | Richer Git history/blame info inline |

You can also install from the terminal:

```bash
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
```

## 3. Point VS Code at the Right Python Interpreter

This matters once you have a `uv`-managed virtual environment (see the `uv` setup guide). Every time you open a project folder for the first time:

1. Open the Command Palette: `Cmd/Ctrl+Shift+P`
2. Type **Python: Select Interpreter**
3. Choose the one inside your project's `.venv` folder (it'll look like `.venv/bin/python` on Mac/Linux or `.venv\Scripts\python.exe` on Windows)

If you don't see it listed, click **Enter interpreter path** and browse to it manually.

## 4. Open a Project the Right Way

Don't open individual files — open the whole project **folder**:

```bash
cd path/to/your-project
code .
```

The `.` means "this folder." This ensures VS Code's terminal, Python interpreter, and Jupyter kernel all resolve paths correctly relative to the project root — a common source of "why can't it find my file" bugs is opening a single file instead of the folder.

## 5. Quick Sanity Check

1. Open VS Code to any folder
2. Open the built-in terminal: `` Ctrl+` `` (backtick)
3. Run `python --version` — confirms a Python is on PATH
4. Create a file called `test.ipynb`, open it, and confirm VS Code offers to select a kernel

If all four steps work, you're ready.

## Troubleshooting

| Problem | Fix |
| :--- | :--- |
| `code` command not found | Re-run "Shell Command: Install 'code' command in PATH" from the Command Palette |
| Jupyter notebook won't run / no kernel found | Make sure the Jupyter extension is installed and you've selected a Python interpreter (Step 3) |
| Wrong Python version shows up | You likely selected the system Python instead of your project's `.venv` — redo Step 3 |
