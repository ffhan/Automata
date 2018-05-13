"""
Endpoint for checking Deterministic PDA output.
"""
import form.preformat as pf
import form.readers as rs
import form.compositors as cs

TEXT = rs.Reader.read_input()
DFA = pf.get_dpda(TEXT)
print(cs.StandardPushDownCompositor(DFA).composite_output())
