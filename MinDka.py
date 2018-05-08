import format.preformat as pf
import format.readers as rs

text = rs.Reader.read_input()
pf.print_encoding(pf.parse_dfa(text))