# Author: Kadiedra Salmon
# ID: 2105254
# Member 2: Syntax analysis and syntax-error reporting
# Based on the initial parser prototype by Joievelle Leslie.

import ply.yacc as yacc
from compiler import tokens, lexer

# --- PARSER CONFIGURATION ---
dfa_data = {"name": "", "Q": [], "Sigma": [], "q0": "", "F": [], "transitions": []}

# Rule 1: Root program rule must be defined first
def p_program(p):
    'program : IDENTIFIER EQUALS dfa_body'
    dfa_data["name"] = p[1]

def p_any_id(p):
    '''any_id : IDENTIFIER
              | Q0_SYM'''
    p[0] = p[1]

def p_dfa_body(p):
    '''dfa_body : format1_multiline
                | format2_inline'''
    pass

# --- Format 1 (Multiline + Table Layout) ---
def p_format1_multiline(p):
    'format1_multiline : tuple_def q_def sigma_def delta_def q0_def f_def table_def'
    pass

def p_tuple_def(p):
    'tuple_def : LPAREN Q_SYM COMMA SIGMA_SYM COMMA DELTA_SYM COMMA Q0_SYM COMMA F_SYM RPAREN'
    pass

def p_q_def(p):
    'q_def : Q_SYM EQUALS LBRACE state_list RBRACE'
    dfa_data["Q"] = p[4]

def p_sigma_def(p):
    'sigma_def : SIGMA_SYM EQUALS LBRACE alphabet_list RBRACE'
    dfa_data["Sigma"] = p[4]

def p_delta_def(p):
    'delta_def : DELTA_SYM EQUALS Q_SYM CROSS SIGMA_SYM ARROW Q_SYM'
    pass

def p_q0_def(p):
    'q0_def : Q0_SYM EQUALS any_id'
    dfa_data["q0"] = p[3]

def p_f_def(p):
    'f_def : F_SYM EQUALS LBRACE state_list RBRACE'
    dfa_data["F"] = p[4]

def p_table_def(p):
    'table_def : DELTA_SYM id_list'

    source = p.lexer.lexdata
    header_line = source.count('\n', 0, p.lexpos(1)) + 1
    num_sigma = len(dfa_data["Sigma"])

    # Group table values by their actual source line.
    lines = {}
    for value, position in p[2]:
        line_number = source.count('\n', 0, position) + 1
        lines.setdefault(line_number, []).append(value)

    headers = lines.pop(header_line, [])

    if len(headers) != num_sigma:
        raise ValueError(
            f"Table structure error at line {header_line}: "
            f"expected {num_sigma} column header(s), "
            f"but found {len(headers)}."
        )

    if not lines:
        raise ValueError(
            "Table structure error: no transition rows were provided."
        )

    for line_number, row in lines.items():
        expected = 1 + len(headers)

        if len(row) != expected:
            raise ValueError(
                f"Table structure error at line {line_number}: "
                f"expected one source state and {len(headers)} "
                f"destination state(s), but found {len(row)} value(s)."
            )

        from_state = row[0]
        targets = row[1:]

        for symbol, target in zip(headers, targets):
            dfa_data["transitions"].append(
                (from_state, symbol, target)
            )


def p_table_cell(p):
    '''table_cell : IDENTIFIER
                  | Q0_SYM'''
    p[0] = (p[1], p.lexpos(1))


def p_id_list(p):
    '''id_list : table_cell
               | table_cell id_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

# --- Format 2 (Inline Layout) ---
def p_format2_inline(p):
    'format2_inline : LPAREN LBRACE state_list RBRACE COMMA LBRACE alphabet_list RBRACE COMMA DELTA_SYM COMMA any_id COMMA LBRACE state_list RBRACE RPAREN inline_transitions'
    dfa_data["Q"] = p[3]
    dfa_data["Sigma"] = p[7]
    dfa_data["q0"] = p[12]
    dfa_data["F"] = p[15]

def p_inline_transitions(p):
    '''inline_transitions : inline_transition
                          | inline_transition inline_transitions'''
    pass

def p_inline_transition(p):
    'inline_transition : DELTA_SYM LPAREN any_id COMMA any_id RPAREN EQUALS any_id'
    dfa_data["transitions"].append((p[3], p[5], p[8]))

# --- Shared Base Lists ---
def p_state_list(p):
    '''state_list : any_id
                  | any_id COMMA state_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_alphabet_list(p):
    '''alphabet_list : any_id
                     | any_id COMMA alphabet_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_error(p):
    if p:
        source = p.lexer.lexdata
        last_newline = source.rfind('\n', 0, p.lexpos)
        column = p.lexpos - last_newline

        line_start = last_newline + 1
        line_end = source.find('\n', p.lexpos)
        if line_end == -1:
            line_end = len(source)

        source_line = source[line_start:line_end]
        pointer = " " * (column - 1) + "^"

        raise SyntaxError(
            f"Syntax error at line {p.lineno}, column {column}: "
            f"unexpected token '{p.value}'\n"
            f"{source_line}\n"
            f"{pointer}"
        )
    else:
        raise SyntaxError(
            "Syntax error: unexpected end of input. "
            "The description may be incomplete."
        )
    
parser = yacc.yacc(
    start="program",
    debug=False,
    write_tables=False,
    tabmodule="member2_parsetab"
)

def parse_dfa_code(code_text):
    global dfa_data
    dfa_data = {
        "name": "",
        "Q": [],
        "Sigma": [],
        "q0": "",
        "F": [],
        "transitions": []
    }
    lexer.lineno = 1
    parser.parse(code_text, lexer=lexer)
    return dfa_data