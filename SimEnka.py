"""
Endpoint for checking epsilon NFA output.
"""
import form.preformat as pf
import form.readers as rs
import form.compositors as cs

TEXT = rs.Reader.read_input()
E_NFA = pf.get_e_nfa(TEXT)
# cs.StandardCompositor(e_nfa).composite_output()
print(cs.StandardCompositor(E_NFA).composite_output())
