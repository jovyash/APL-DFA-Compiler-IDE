Author: Kadiedra Salmon
ID: 2105254
Responsibility: Syntax analysis and syntax-error reporting

ACKNOWLEDGEMENT
This parser builds on Joievelle Leslie's initial parser prototype.
It uses the token definitions and lexer in her compiler.py file.

MY FILE
syntax_parser.py

FUNCTIONALITY
- Parses the multiline/table and inline DFA formats.
- Returns the DFA information in a dictionary.
- Reports unexpected tokens with a line, column, source line and pointer.
- Reports unexpected end of input.
- Checks table header counts and individual row lengths.
- Maps transitions using the table's actual header order.
- Clears previous DFA data before each new parse.


TEST 1: PYTHON SYNTAX CHECK
.\.venv_windows\Scripts\python.exe -m py_compile syntax_parser.py

Expected: returns to the terminal prompt without an error.
No output is expected on success.
This checks Python syntax, not the parser's behaviour.

TEST 2: VALID INLINE DFA
.\.venv_windows\Scripts\python.exe -c "from syntax_parser import parse_dfa_code; print(parse_dfa_code('M = ({Ready}, {a}, delta, Ready, {Ready}) delta(Ready,a)=Ready'))"

Expected:
{'name': 'M', 'Q': ['Ready'], 'Sigma': ['a'], 'q0': 'Ready', 'F': ['Ready'], 'transitions': [('Ready', 'a', 'Ready')]}

TEST 3: VALID TABLE WITH REVERSED HEADERS
.\.venv_windows\Scripts\python.exe -c "from syntax_parser import parse_dfa_code; print(parse_dfa_code('M = (Q, sigma, delta, q0, F)\nQ = {Ready,Busy}\nsigma = {a,b}\ndelta = Q * sigma -> Q\nq0 = Ready\nF = {Busy}\ndelta b a\nReady Busy Ready\nBusy Ready Busy'))"

Expected transitions:
[('Ready', 'b', 'Busy'), ('Ready', 'a', 'Ready'), ('Busy', 'b', 'Ready'), ('Busy', 'a', 'Busy')]

This tests the parser directly. It verifies that destinations are
paired with the actual table headings, even when their order
differs from the alphabet declaration.

TEST 4: MISSING EQUALS SIGN
.\.venv_windows\Scripts\python.exe -c "from syntax_parser import parse_dfa_code; parse_dfa_code('M = ({Ready}, {a}, delta, Ready, {Ready})\ndelta(Ready,a)Ready')"

Expected:
Syntax error at line 2, column 15: unexpected token 'Ready'.
The source line and a caret pointer are included.

The error is deliberate. A traceback is expected in the terminal.
This confirms that invalid syntax is rejected.

TEST 5: INCOMPLETE INPUT
.\.venv_windows\Scripts\python.exe -c "from syntax_parser import parse_dfa_code; parse_dfa_code('M = ({Ready}, {a}, delta, Ready, {Ready}) delta(Ready,a)=')"

Expected:
Syntax error: unexpected end of input.
The description may be incomplete.

The error is deliberate. A traceback is expected.

TEST 6: INCORRECT TABLE ROW
.\.venv_windows\Scripts\python.exe -c "from syntax_parser import parse_dfa_code; parse_dfa_code('M = (Q, sigma, delta, q0, F)\nQ = {Ready,Busy}\nsigma = {a,b}\ndelta = Q * sigma -> Q\nq0 = Ready\nF = {Busy}\ndelta a b\nReady Busy\nBusy Ready Busy Ready')"

Expected:
Table structure error at line 8: expected one source state
and 2 destination state(s), but found 2 value(s).

The error is deliberate. A ValueError traceback is expected.
The parser stops at the first incorrect row.

TEST 7: CONNECTION TO SEMANTIC ANALYSIS
Requires semantic.py in the same project folder.

.\.venv_windows\Scripts\python.exe -c "from syntax_parser import parse_dfa_code; from semantic import analyze; d = parse_dfa_code('M = ({Ready}, {a}, delta, Ready, {Ready}) delta(Ready,a)=Ready'); issues, table = analyze(d); print(d); print([str(i) for i in issues])"

Expected:
The parsed dictionary, followed by:
[]

The empty list means no semantic issues were found for this example.

RUN THE INTEGRATED GUI
app.py must import the parser using:
from syntax_parser import parse_dfa_code

Launch:
.\.venv_windows\Scripts\python.exe -m streamlit run app.py

Open the Local URL printed in the terminal.
It is usually http://localhost:8501, but use the actual URL shown.

Enter a DFA description and click Compile & Render Engine.
Keep the terminal running while using the webpage.
Press Ctrl+C in that terminal to stop the application.

COMMON ERRORS
- ".venv\Scripts\python.exe is not recognized":
  This README uses .venv_windows, not .venv.

- ".venv_windows\Scripts\python.exe is not recognized":
  Check that the terminal is in the correct project folder and
  that the environment exists there.

- "No module named ply":
  Install PLY using the same environment's Python:
  .\.venv_windows\Scripts\python.exe -m pip install ply

- Incorrect syntax-error line numbers:
  The lexer must count newlines, and parse_dfa_code must reset
  lexer.lineno to 1 before parsing.

INTEGRATION NOTES
The parser checks structure and collects DFA information.
Semantic analysis checks declared names and DFA constraints.

The current parser does not provide the optional table_header
and table_leftover fields used by Member 3's E10/E11 checks.
It checks row lengths itself, but header membership and duplicate
header validation remain items for group review.

Member 3's test_semantic.py currently imports the original parser
from compiler.py. It does not test syntax_parser.py.

The imported lexer has known limitations, including numeric
alphabet symbols and some identifiers beginning with Q or F.
These are lexical-stage limitations.

AUTHORSHIP AND INTEGRATION CHANGES
The parser is based on Member 1's original prototype.
Member 2's work includes detailed syntax-error reporting,
individual table-row checks, source-position handling,
and mapping transitions using actual table headings.

During integration, app.py was connected to syntax_parser.py,
and newline counting was added to the shared lexer.