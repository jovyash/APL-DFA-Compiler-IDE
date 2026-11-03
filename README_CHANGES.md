# Changes Made to the Original Project Files

**Author:** Michael Wright (2005335) | Member 3 (Semantic Analysis)

This file lists every change made on top of the original `app.py`, `compiler.py`, `parsetab.py` and `parser.out`.
Items marked **MAC-ONLY** were added while setting up the project on a Mac. **Other group members can ignore them or defer them.** They are not needed for the project to work on other systems.

---

## At a glance

| File | Status | Needed by everyone? |
|---|---|---|
| `semantic.py` | **New** | Yes, this is the semantic analysis stage |
| `test_semantic.py` | **New** | Optional, a test script |
| `app.py` | **Modified** (2 changes) | Change 1: yes. Change 2: **MAC-ONLY** |
| `compiler.py` | **Modified** (small, additive) | Recommended; see below |
| `requirements.txt` | **New** | **Mostly MAC-ONLY**; see below |
| `parsetab.py`, `parser.out` | Not edited by hand | Regenerated automatically by PLY; ignore |

The grammar rules and the lexer are **not** changed. Only the parser's bookkeeping was touched, as described below.

---

## 1. `semantic.py` (new file)

The semantic analysis stage. It takes the dictionary returned by `parse_dfa_code()` and checks that the DFA makes sense (undeclared states, nondeterminism, missing transitions, etc.). It returns `(issues, symbol_table)`.

For the full list of error and warning codes (E01 to E12, W01 to W06), the scope and binding rules, and the API, see **`README_semantic.md`**.

---

## 2. `app.py` (modified)

### Change 1: semantic stage integration (everyone)

- Added `from semantic import analyze`.
- Replaced the old inline checks (start state and final states in Q only) with a call to `analyze(parsed_ast)`.
- The app now shows:
  - semantic **errors** in red, with an error count. The diagram is not rendered if there are any.
  - **warnings** in yellow. The diagram still renders.
  - a collapsible **symbol table** panel.
- The diagram-drawing code is unchanged.

### Change 2: launcher block at the bottom (MAC-ONLY, ignore or defer)

```python
if __name__ == '__main__':
    if not st.runtime.exists():
        import sys
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
```

> **MAC-ONLY. Teammates can ignore this.**
> It lets the app be started with `python app.py` instead of `streamlit run app.py`. It was added because of the Mac setup, where the `streamlit` command wasn't found. It does nothing when the app is started the normal way, so it is harmless to leave in. It can also be deleted without affecting anything else.
> Everyone else should just run: `streamlit run app.py`

---

## 3. `compiler.py` (modified, small and additive)

No grammar rules, tokens or lexer rules were changed. Two additions:

1. Both places where `dfa_data` is created gain two keys:
   ```python
   "table_header": None, "table_leftover": []
   ```
2. `p_table_def` now saves the table header and any leftover row tokens, which it previously computed and then discarded:
   ```python
   dfa_data["table_header"] = all_ids[:num_sigma]
   dfa_data["table_leftover"] = matrix[len(matrix) - (len(matrix) % row_len):] if len(matrix) % row_len else []
   ```

**Why:** `semantic.py` needs these to detect a table header that doesn't match Σ (E10) and an incomplete table row (E11). Without this change the app still runs. Those two checks are simply skipped.

**For the author of `compiler.py` (Joievelle Leslie):** this does not change how anything is parsed, and `parsetab.py` / `parser.out` do not need regenerating by hand. Please don't overwrite these lines if you edit `compiler.py`.

---

## 4. `requirements.txt` (new file)

> **MAC-ONLY. Teammates can ignore this or defer it.**
> This file was generated from the Mac setup, so it pins exact versions of every package installed there (streamlit, pandas, numpy, pyarrow, and so on). Those exact versions may not install on another operating system or Python version.

**What everyone actually needs** is just three packages:

```
pip install streamlit graphviz ply
```

If `pip install -r requirements.txt` fails on your machine, skip the file and run the line above instead.

**Not covered by any pip command:** the Graphviz program itself (`dot`) must be installed separately for diagrams to draw. Download it from graphviz.org (tick "add to PATH" on Windows), or use `brew install graphviz` on a Mac.

---

## 5. `test_semantic.py` (new file, optional)

Runs `analyze()` on 9 test inputs (valid programs plus each kind of semantic error) and prints the results.

```
python test_semantic.py
```

---

## Quick summary for teammates

- **Need to do:** add `semantic.py`, and use the updated `app.py` (Change 1) and `compiler.py`.
- **Safe to ignore:** the `if __name__ == '__main__':` block in `app.py` and the pinned `requirements.txt`, both **MAC-ONLY**.
- **Run with:** `streamlit run app.py`
