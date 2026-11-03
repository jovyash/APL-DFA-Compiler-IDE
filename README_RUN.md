Authors: KKadiedra Salmon, Joievelle Leslie

# Running the Integrated DFA Project

This version connects Member 1's lexer, Member 2's syntax parser,
Member 3's semantic analysis, and the existing GUI and diagram renderer.

## First-time setup on Windows

Install Python. Open this folder in VS Code, then select
Terminal → New Terminal.

Run each command separately, pressing Enter after each:

```powershell
py -m venv .venv_windows
.\.venv_windows\Scripts\python.exe -m pip install ply streamlit graphviz
```

## Start the application

From this project folder, run:

```powershell
.\.venv_windows\Scripts\python.exe -m streamlit run app.py
```

Open the Local URL printed in the terminal.
Keep the terminal open while using the application.
Press Ctrl+C in the terminal to stop it.

The setup commands are needed only once per computer.
Use the start command whenever you want to run the application.

## Checks completed during integration

- Valid default multiline description displayed a diagram.
- Valid inline description displayed a diagram.
- Missing closing brace produced a syntax error with line and column.
- Undeclared start state produced Semantic Error E03.

## Items for group review

- Table-header validation needs to be reconciled between the parser
  and semantic stage.
- Identical duplicate transitions currently produce a warning;
  the project instructions require duplicates to be rejected.
- test_semantic.py currently imports the original parser from compiler.py.
  It does not test the integrated syntax_parser.py pipeline.

Read README_Member2.txt, README_semantic.md, and README_CHANGES.md
for stage-specific explanations. Some commands and integration notes
in those earlier documents refer to previous versions.