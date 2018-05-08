import format.preformat as pf
import format.readers as rs
import format.compositors as cs
text = rs.Reader.read_input()
e_nfa = pf.get_e_nfa(text)
# cs.StandardCompositor(e_nfa).composite_output()
print(cs.StandardCompositor(e_nfa).composite_output())