# Author: Michael Wright (semantic stage - Member 3)
# Semantic analysis for the DFA description language.
#
# Input : the dictionary produced by the syntax stage (compiler.parse_dfa_code)
# Output: (issues, symbol_table)
#
# SCOPE   : the language has ONE global scope. A DFA description is a single
#           flat program, so every declared name lives in that scope.
# BINDING : names are bound by declarations, never by use:
#             Q  = {...}   binds identifiers as STATES
#             Σ  = {...}   binds identifiers as ALPHABET SYMBOLS
#             q₀ = x       USES a state (must resolve to a state in Q)
#             F  = {...}   USES states  (must resolve to states in Q)
#             δ(s,a)=t     USES s,t as states and a as a symbol
#           The leading identifier (M = ...) binds the automaton's name.
# An identifier is only valid where its category matches the binding it
# resolves to. Anything that fails to resolve is a semantic error.

from dataclasses import dataclass


@dataclass
class Issue:
    severity: str   # "error" blocks rendering, "warning" does not
    code: str
    message: str

    def __str__(self):
        label = "Semantic Error" if self.severity == "error" else "Warning"
        return f"{label} [{self.code}]: {self.message}"


def build_symbol_table(dfa):
    """Every binding the program introduces, with its category and role."""
    rows = []
    if dfa.get("name"):
        rows.append({"Identifier": dfa["name"], "Category": "automaton",
                     "Declared in": "program header", "Role": "-"})
    for s in dict.fromkeys(dfa["Q"]):
        roles = []
        if s == dfa["q0"]:
            roles.append("start")
        if s in dfa["F"]:
            roles.append("final")
        rows.append({"Identifier": s, "Category": "state", "Declared in": "Q",
                     "Role": ", ".join(roles) or "-"})
    for a in dict.fromkeys(dfa["Sigma"]):
        rows.append({"Identifier": a, "Category": "alphabet symbol",
                     "Declared in": "Σ", "Role": "-"})
    return rows


def analyze(dfa):
    issues = []
    seen_msgs = set()

    def add(sev, code, msg):
        if (code, msg) not in seen_msgs:      # report each distinct problem once
            seen_msgs.add((code, msg))
            issues.append(Issue(sev, code, msg))

    err = lambda c, m: add("error", c, m)
    warn = lambda c, m: add("warning", c, m)

    Q, S, q0, F, T = dfa["Q"], dfa["Sigma"], dfa["q0"], dfa["F"], dfa["transitions"]
    states, symbols = set(Q), set(S)

    # --- 1. Declaration checks (binding) --------------------------------
    seen = set()
    for s in Q:
        if s in seen:
            err("E01", f"State '{s}' is declared more than once in Q.")
        seen.add(s)
    seen = set()
    for a in S:
        if a in seen:
            err("E02", f"Symbol '{a}' is declared more than once in Σ.")
        seen.add(a)
    for n in sorted(states & symbols):
        warn("W01", f"'{n}' is declared as both a state and an alphabet symbol; "
                    f"its meaning depends on where it is used.")
    if dfa.get("name") in states | symbols:
        warn("W02", f"The automaton name '{dfa['name']}' is also declared as a state or symbol.")
    if not S:
        err("E12", "The alphabet Σ is empty.")

    # --- 2. Start / final state resolution ------------------------------
    if q0 not in states:
        err("E03", f"Start state '{q0}' is not declared in Q.")
    seen = set()
    for f in F:
        if f not in states:
            err("E04", f"Final state '{f}' is not declared in Q.")
        if f in seen:
            warn("W03", f"Final state '{f}' is listed more than once in F.")
        seen.add(f)
    if not F:
        warn("W04", "F is empty: the automaton accepts no strings.")

    # --- 3. Table layout checks (Format 1 only) -------------------------
    header = dfa.get("table_header")
    if header is not None and header != S:
        err("E10", f"Table header columns {header} do not match Σ {S} "
                   f"(order matters: each column is read as the symbol at that position of Σ).")
    if dfa.get("table_leftover"):
        err("E11", f"Incomplete table row near {dfa['table_leftover']}: "
                   f"each row needs a state followed by {len(S)} target(s).")

    # --- 4. Transition resolution + determinism -------------------------
    delta = {}
    for src, sym, dst in T:
        if src not in states:
            err("E05", f"Transition source '{src}' is not declared in Q.")
        if sym not in symbols:
            err("E06", f"Transition symbol '{sym}' is not in Σ.")
        if dst not in states:
            err("E07", f"Transition target '{dst}' is not declared in Q.")
        key = (src, sym)
        if key in delta:
            if delta[key] == dst:
                warn("W05", f"Duplicate transition δ({src},{sym}) = {dst}.")
            else:
                err("E08", f"Nondeterminism: δ({src},{sym}) is defined as both "
                           f"'{delta[key]}' and '{dst}'. A DFA allows exactly one.")
        else:
            delta[key] = dst

    # --- 5. Totality of δ : Q × Σ → Q -----------------------------------
    for s in dict.fromkeys(Q):
        for a in dict.fromkeys(S):
            if (s, a) not in delta:
                err("E09", f"Missing transition: δ({s},{a}) is not defined (δ must be total).")

    # --- 6. Reachability (warning) --------------------------------------
    if q0 in states:
        reach, stack = {q0}, [q0]
        while stack:
            cur = stack.pop()
            for (s, a), t in delta.items():
                if s == cur and t in states and t not in reach:
                    reach.add(t)
                    stack.append(t)
        for s in dict.fromkeys(Q):
            if s not in reach:
                warn("W06", f"State '{s}' is unreachable from the start state '{q0}'.")

    return issues, build_symbol_table(dfa)
