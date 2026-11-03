from compiler import parse_dfa_code
from semantic import analyze

H = "M = (Q, Σ, δ, q₀, F)\nQ = {%s}\nΣ = {a, b}\nδ = Q × Σ → Q\nq₀ = %s\nF = {%s}\n\nδ %s\n%s"
I = "M = ({%s}, {a,b}, δ, %s, {%s})\n%s"
cases = {
 "valid table": H % ("q1, q2, Trap","q1","q2","a b","q1 q2 Trap\nq2 q2 q1\nTrap Trap Trap"),
 "valid inline": I % ("q1,q2","q1","q2","δ(q1,a)=q2\nδ(q1,b)=q1\nδ(q2,a)=q2\nδ(q2,b)=q1"),
 "bad start+final": I % ("q1,q2","q9","q8","δ(q1,a)=q2\nδ(q1,b)=q1\nδ(q2,a)=q2\nδ(q2,b)=q1"),
 "undeclared use": I % ("q1,q2","q1","q2","δ(q1,a)=q9\nδ(q1,b)=q1\nδ(q2,a)=q2\nδ(q2,b)=q1\nδ(q7,a)=q1\nδ(q1,z)=q1"),
 "nondeterministic+dup": I % ("q1,q2","q1","q2","δ(q1,a)=q2\nδ(q1,a)=q1\nδ(q1,b)=q1\nδ(q1,b)=q1\nδ(q2,a)=q2\nδ(q2,b)=q1"),
 "missing transitions": I % ("q1,q2","q1","q2","δ(q1,a)=q2"),
 "dup decl + unreachable": I % ("q1,q2,q2,q3","q1","q2","δ(q1,a)=q2\nδ(q1,b)=q1\nδ(q2,a)=q2\nδ(q2,b)=q1\nδ(q3,a)=q3\nδ(q3,b)=q3"),
 "swapped header": H % ("q1, q2","q1","q2","b a","q1 q2 q1\nq2 q2 q1"),
 "short row": H % ("q1, q2","q1","q2","a b","q1 q2 q1\nq2 q2"),
}
for name, src in cases.items():
    issues, _ = analyze(parse_dfa_code(src))
    print(f"--- {name}: {sum(i.severity=='error' for i in issues)} error(s), {sum(i.severity=='warning' for i in issues)} warning(s)")
    for i in issues: print("   ", i)
