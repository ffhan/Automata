import format.preformat as pf
import format.readers as rs
import format.parsers as ps
import format.compositors as cs

from automata.dfa import DFA

text = rs.Reader.read_input()
dfa = pf.get_pda(text)
print(cs.StandardPushDownCompositor(dfa).composite_output())