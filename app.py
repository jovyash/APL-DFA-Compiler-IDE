# Author: Joievelle Leslie and Kadiedra Salmon
# Id#: 2001095 , 2105254
# Interactive DFA Compiler & Visualization 

import streamlit as st
import graphviz
from syntax_parser import parse_dfa_code
from semantic import analyze
import streamlit as st

# 1. GLOBAL THEME INJECTION (Handles overall theme vars)
st.html("""
    <style>
        /* Base Global Overrides for Accents and Focus borders */
        :root {
            --primary-color: #ff2a74 !important;
        }
        
        /* Textarea input border color adjustments on focus */
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #ff2a74 !important;
            box-shadow: 0 0 5px rgba(255, 42, 116, 0.5) !important;
        }

        /* FIX: Target using Streamlit's official native key class wrapper */
        div.st-key-compile_btn button {
            transition: all 0.3s ease-in-out !important;
            position: relative !important;
            border: 1px solid rgba(255, 42, 116, 0.4) !important;
        }
        
        /* Neon hover state targeting the inner button element */
        div.st-key-compile_btn button:hover {
            color: #ffffff !important;
            border-color: #ff2a74 !important;
            background-color: rgba(255, 42, 116, 0.15) !important;
            box-shadow: 0 0 10px #ff2a74, 0 0 20px #ff2a74, 0 0 30px rgba(255, 42, 116, 0.6) !important;
            transform: translateY(-1px) !important;
        }

        /* ALERTS & NOTIFICATIONS (Hints of Pink) */
        div[data-testid="stNotificationV2"]:has(div[aria-label="Success"]), 
        div[data-testid="stNotification"]:has(div[aria-label="Success"]) {
            background-color: rgba(255, 42, 116, 0.1) !important;
            border-left: 5px solid #ff2a74 !important;
        }
        div[data-testid="stNotificationV2"]:has(div[aria-label="Success"]) p,
        div[data-testid="stNotification"]:has(div[aria-label="Success"]) p {
            color: #ff80ab !important;
        }

        div[data-testid="stNotificationV2"]:has(div[aria-label="Info"]),
        div[data-testid="stNotification"]:has(div[aria-label="Info"]) {
            background-color: rgba(244, 143, 177, 0.08) !important;
            border-left: 5px solid #f48fb1 !important;
        }
        div[data-testid="stNotificationV2"]:has(div[aria-label="Info"]) p,
        div[data-testid="stNotification"]:has(div[aria-label="Info"]) p {
            color: #f48fb1 !important;
        }
        
        h2, h3 {
            color: #f48fb1 !important;
        }
    </style>
""")

# Page styling configurations
st.set_page_config(page_title="DFA Compiler & Visualization Suite", layout="wide", initial_sidebar_state="expanded")

st.title(" DFA Formal Description Compiler IDE")
st.caption("Joievelle Leslie, Kadiedra Salmon and Michael Wright | University of Technology, Jamaica | APL Project|Dr.David White ")

# Sidebar - Compiler Status Logs & Documentation ShortcuTS 
# this section is for displaying compiler status logs, reference syntax, and other relevant information 
with st.sidebar:
    st.header(" System Configuration & Logs")
    st.info("Grammar Standard: CFG (BNF Loaded)")
    
    st.markdown("---")
    st.subheader(" Reference Test Syntaxes")
    st.code("""# Format 2 (Inline Style)
M = ({q1,q2}, {a,b}, δ, q1, {q2})
δ(q1,a)=q2
δ(q1,b)=q1
δ(q2,a)=q2
δ(q2,b)=q1""", language="text")

# Code Input Split Panes
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("Source Code Editor")
    input_code = st.text_area(
        "Enter DFA Formal Description Language Source Code Here:",
        value="""M = (Q, Σ, δ, q₀, F)\nQ = {q1, q2, Trap}\nΣ = {a, b}\nδ = Q × Σ → Q\nq₀ = q1\nF = {q2}\n\nδ a b\nq1 q2 Trap\nq2 q2 q1\nTrap Trap Trap""",
        height=320
    )
    
    #compile_btn = st.button(" Compile & Render Engine", use_container_width=True) 
    compile_btn = st.button(" Compile & Render Engine", use_container_width=True, key="compile_btn") 


with col2:
    st.subheader("Live Canvas State Diagram")
    
    if compile_btn:
        try:
            # Execute Pipeline
            parsed_ast = parse_dfa_code(input_code)
            
            # --- SEMANTIC ANALYSIS STAGE (semantic.py) ---
            issues, symbol_table = analyze(parsed_ast)
            errors = [i for i in issues if i.severity == "error"]
            warnings = [i for i in issues if i.severity == "warning"]

            if errors:
                st.error(f"❌{len(errors)} semantic error(s) found - diagram not rendered.")
                for err in errors:
                    st.error(str(err))
                for w in warnings:
                    st.warning(str(w))
                with st.expander("Symbol table"):
                    st.table(symbol_table)
            else:
                st.success(f" Compilation Successful! Instantiated Automaton Object: '{parsed_ast['name']}'")
                
                for w in warnings:
                    st.warning(str(w))
                with st.expander("Symbol table (bindings)"):
                    st.table(symbol_table)

                # --- VISUALIZATION RENDERING ENGINE ---
                dot = graphviz.Digraph(comment=parsed_ast["name"])
                dot.attr(rankdir='LR', size='8,5', bgcolor='transparent')
                dot.attr('node', fontname='Helvetica', fontsize='12', labelfontcolor='white')
                
                # Invisible starting anchor node
                dot.node('start_anchor', shape='point', width='0', fillcolor='white', style='invis')
                
                # Render States Loop
                for state in parsed_ast["Q"]:
                    if state in parsed_ast["F"]:
                        dot.node(state, shape='doublecircle', style='filled', fillcolor='#2e7d32', color='#a1ffaf', fontcolor='white', penwidth='2')
                    elif state == parsed_ast["q0"]:
                        dot.node(state, shape='circle', style='filled', fillcolor='#1565c0', color='#90caf9', fontcolor='white', penwidth='2')
                    else:
                        dot.node(state, shape='circle', style='filled', fillcolor="#704764", color='#cfd8dc', fontcolor='white')
                
                # Initial Arrow Pointer. // this shows the starting state of the DFA with a directed edge from an invisible anchor node to the initial state.
                dot.edge('start_anchor', parsed_ast["q0"], label='', color='#eceff1', fontcolor='#ffb300')
                
                # Group shared direction edges cleanly to avoid visual mess
                edge_groups = {}
                for src, sym, dest in parsed_ast["transitions"]:
                    key = (src, dest)
                    edge_groups[key] = edge_groups.get(key, []) + [sym]
                
                for (src, dest), symbols in edge_groups.items():
                    label_str = ", ".join(symbols)
                    dot.edge(src, dest, label=f" {label_str} ", color='#eceff1', fontcolor='#ffb300')
                
                # Output Diagram directly into the UI Frame
                st.graphviz_chart(dot, use_container_width=True)
                
        except Exception as e:
            st.error(f" Structural Failure During Pass: {str(e)}")
    else:
        st.info("Awaiting input data stream. Click 'Compile & Render Engine' above to trigger pipeline.")

if __name__ == '__main__':
    if not st.runtime.exists():
        import sys
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())

