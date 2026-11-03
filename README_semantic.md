# Semantic Analysis Stage: `semantic.py`

**Author:** Michael Wright (2005335) | Member 3 | APL Project, DFA Formal Description Compiler

This document covers the semantic analysis stage and the changes made to `app.py` to integrate it.

---

## 1. Where it fits in the pipeline

```
Source text → Lexer → Parser → [ Semantic analysis ] → Diagram rendering
              (PLY)    (PLY)      semantic.py             app.py / Graphviz
```

The lexer and parser check that the input is *well-formed*. They do not check that it *makes sense*. For example, `δ(q1,a)=q9` is grammatically valid even if `q9` was never declared. `semantic.py` takes the dictionary produced by `parse_dfa_code()` and checks it for meaning.

**Input:** the parser's output dictionary:

| Key | Content |
|---|---|
| `name` | automaton name (e.g. `M`) |
| `Q` | list of declared states |
| `Sigma` | list of declared alphabet symbols |
| `q0` | start state |
| `F` | list of final states |
| `transitions` | list of `(source, symbol, target)` tuples |
| `table_header`, `table_leftover` | *(optional, see section 6)* |

**Output:** a tuple `(issues, symbol_table)`:
- `issues`: a list of `Issue` objects, each with a `severity` (`"error"` or `"warning"`), a `code` (e.g. `E08`), and a `message`.
- `symbol_table`: a list of dictionaries describing every binding in the program.

---

## 2. Scope, binding and identifiers

- **Scope:** the language has a single global scope, because a DFA description is one flat program. Every declared name lives in that scope.
- **Binding:** names are bound by declarations, never by use.

| Construct | Effect |
|---|---|
| `M = ...` | binds `M` as the automaton name |
| `Q = {...}` | binds each identifier as a **state** |
| `Σ = {...}` | binds each identifier as an **alphabet symbol** |
| `q₀ = x` | *uses* `x`, which must resolve to a state in Q |
| `F = {...}` | *uses* each name, each of which must resolve to a state in Q |
| `δ(s,a)=t` / table rows | *uses* `s` and `t` as states and `a` as a symbol |

An identifier is valid only where its category matches the binding it resolves to. Any use that fails to resolve is a semantic error.

---

## 3. Checks performed

### Errors (the diagram is **not** rendered)

| Code | Meaning |
|---|---|
| E01 | State declared more than once in Q |
| E02 | Symbol declared more than once in Σ |
| E03 | Start state not declared in Q |
| E04 | Final state not declared in Q |
| E05 | Transition source state not declared in Q |
| E06 | Transition symbol not in Σ |
| E07 | Transition target state not declared in Q |
| E08 | Nondeterminism: same (state, symbol) maps to two different targets |
| E09 | Missing transition: δ must be total (Q × Σ → Q) |
| E10 | Table header columns do not match Σ (order matters) *(needs the compiler patch)* |
| E11 | Incomplete table row *(needs the compiler patch)* |
| E12 | Alphabet Σ is empty |

### Warnings (the diagram **is** still rendered)

| Code | Meaning |
|---|---|
| W01 | Same name declared as both a state and a symbol |
| W02 | Automaton name is also declared as a state or symbol |
| W03 | Final state listed more than once in F |
| W04 | F is empty (the automaton accepts nothing) |
| W05 | Duplicate transition (same state, symbol and target repeated) |
| W06 | State unreachable from the start state |

### How errors are detected and reported

1. The stage only runs after parsing succeeds, so it can assume the structure is valid.
2. It makes one pass for each category of check (declarations, start/final states, table layout, transitions, totality, reachability).
3. **All** problems are collected instead of stopping at the first one, so the user sees everything at once.
4. Identical messages are reported only once.
5. Each message has a stable code and plain-language text, for example:
   `Semantic Error [E08]: Nondeterminism: δ(q1,a) is defined as both 'q2' and 'q1'. A DFA allows exactly one.`

---

## 4. Public API

```python
from semantic import analyze

issues, symbol_table = analyze(parsed_ast)

errors   = [i for i in issues if i.severity == "error"]
warnings = [i for i in issues if i.severity == "warning"]
```

- `analyze(dfa)` returns `(issues, symbol_table)`.
- `str(issue)` gives the formatted message, e.g. `Semantic Error [E03]: ...` or `Warning [W06]: ...`.
- `build_symbol_table(dfa)` is called by `analyze()`. Each row has `Identifier`, `Category` (automaton, state, or alphabet symbol), `Declared in`, and `Role` (start and/or final).

---

## 5. Changes to `app.py`

Three edits. Nothing else in the file was changed.

**1. New import**

```python
from compiler import parse_dfa_code
from semantic import analyze          # added
```

**2. The inline semantic block is replaced by a call to `analyze()`**

*Before:* the app only checked that `q0` and every state in `F` were in `Q`.

*After:*

```python
issues, symbol_table = analyze(parsed_ast)
errors   = [i for i in issues if i.severity == "error"]
warnings = [i for i in issues if i.severity == "warning"]
```

**3. Reporting to the user**

- **If there are errors:** a summary banner (`N semantic error(s) found - diagram not rendered`), each error in red, each warning in yellow, and a collapsible **Symbol table** panel. No diagram is drawn.
- **If there are no errors:** the success message, any warnings in yellow, a collapsible **Symbol table (bindings)** panel, and then the diagram as before.

The visualization code is unchanged.

---

## 6. Optional change to `compiler.py`

Without this change, `semantic.py` still works, but checks **E10** and **E11** are skipped. `p_table_def` throws away the table header and any leftover row tokens, so there is nothing for those checks to look at. The code reads these fields with `.get()`, so it won't crash without them.

The patch is additive and changes no existing behavior:

1. Both copies of the `dfa_data` initialization gain two keys:
   ```python
   "table_header": None, "table_leftover": []
   ```
2. `p_table_def` records them after computing `matrix` and `row_len`:
   ```python
   dfa_data["table_header"] = all_ids[:num_sigma]
   dfa_data["table_leftover"] = matrix[len(matrix) - (len(matrix) % row_len):] if len(matrix) % row_len else []
   ```

`compiler.py` belongs to the lexer and parser members, so tell them before this goes in.

---

## 7. Testing

`test_semantic.py` runs `analyze()` on 9 inputs, covering valid programs in both formats plus invalid start/final states, undeclared names, nondeterminism and duplicates, missing transitions, duplicate declarations with unreachable states, a swapped header, and a short table row.

```
python test_semantic.py
```

**Requirements:** `ply`, `streamlit`, `graphviz` (Python packages), and the Graphviz system binary (`dot`) for diagram rendering.
Run the app with `streamlit run app.py`.

---

## 8. Known limitations

- Messages have no line or column numbers, because the lexer does not track positions.
- Lexer limitations occur before this stage and cannot be fixed here: states named with a leading `Q` or `F` (e.g. `Q1`) are rejected, and digit symbols such as `{0,1}` are not accepted.
- The parser stores results in a module-level global (`dfa_data`), so compilation is not thread-safe.
