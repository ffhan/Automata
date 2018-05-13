"""
Endpoint for checking minimized DFA representation.
"""
import form.preformat as pf
import form.readers as rs
import form.compositors as cs

TEXT = rs.Reader.read_input()
DFA = pf.get_dfa_min(TEXT)
print(cs.StandardCompositor(DFA).composite_automaton())
