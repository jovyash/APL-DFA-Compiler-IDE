# Author: Joievelle Leslie 
# Id#: 2001095
# Python(PLY) lex & yacc based DFA Compiler 
import ply.lex as lex
import ply.yacc as yacc

# --- LEXER CONFIGURATION ---
tokens = (
    'IDENTIFIER', 'EQUALS', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA',
    'Q_SYM', 'SIGMA_SYM', 'DELTA_SYM', 'Q0_SYM', 'F_SYM', 'CROSS', 'ARROW'
)

def t_EQUALS(t): r'='; return t
def t_LPAREN(t): r'\('; return t
def t_RPAREN(t): r'\)'; return t
def t_LBRACE(t): r'\{'; return t
def t_RBRACE(t): r'\}'; return t
def t_COMMA(t):  r','; return t

def t_Q_SYM(t):     r'Q'; return t
def t_SIGMA_SYM(t): r'Σ|\bsigma\b'; return t
def t_DELTA_SYM(t): r'δ|\bdelta\b'; return t
def t_Q0_SYM(t):    r'q₀|q0'; return t
def t_F_SYM(t):     r'F'; return t
def t_CROSS(t):     r'×|\*'; return t
def t_ARROW(t):     r'→|->'; return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value == 'Q': t.type = 'Q_SYM'
    elif t.value in ['sigma', 'Σ']: t.type = 'SIGMA_SYM'
    elif t.value in ['delta', 'δ']: t.type = 'DELTA_SYM'
    elif t.value in ['q0', 'q₀']: t.type = 'Q0_SYM'
    elif t.value == 'F': t.type = 'F_SYM'
    return t

t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    
def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

# --- PARSER CONFIGURATION ---
dfa_data = {"name": "", "Q": [], "Sigma": [], "q0": "", "F": [], "transitions": [], "table_header": None, "table_leftover": []}

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
    all_ids = p[2]
    num_sigma = len(dfa_data["Sigma"])
    
    # Skip the headers, extract the matrix values
    matrix = all_ids[num_sigma:]
    row_len = 1 + num_sigma

    # Recorded for the semantic stage (header/Sigma check, incomplete rows)
    dfa_data["table_header"] = all_ids[:num_sigma]
    dfa_data["table_leftover"] = matrix[len(matrix) - (len(matrix) % row_len):] if len(matrix) % row_len else []
    
    for i in range(0, len(matrix), row_len):
        row = matrix[i:i+row_len]
        if len(row) == row_len:
            from_state = row[0]
            targets = row[1:]
            for idx, target in enumerate(targets):
                if idx < len(dfa_data["Sigma"]):
                    symbol = dfa_data["Sigma"][idx]
                    dfa_data["transitions"].append((from_state, symbol, target))

def p_id_list(p):
    '''id_list : any_id
               | any_id id_list'''
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
        raise SyntaxError(f"Syntax error at token '{p.value}'")
    else:
        raise SyntaxError("Syntax error: Unexpected end of input configuration.")

parser = yacc.yacc()

def parse_dfa_code(code_text):
    global dfa_data
    dfa_data = {"name": "", "Q": [], "Sigma": [], "q0": "", "F": [], "transitions": [], "table_header": None, "table_leftover": []}
    parser.parse(code_text)
    return dfa_data
