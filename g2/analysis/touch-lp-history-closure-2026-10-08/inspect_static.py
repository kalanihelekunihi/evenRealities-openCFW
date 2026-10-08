"""Narrow offline instruction/data evidence; candidate scan is not CFG proof."""
from pathlib import Path
import json,struct,hashlib
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
D=Path(__file__).resolve().parent;root=D.parents[2];fw=root/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';raw=fw.read_bytes()[32:];base=0x3300;cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN)
ranges=[(0x7e04,0x7e14),(0x6530,0x664c),(0x6780,0x6868),(0x4e6c,0x4e86),(0x5c02,0x5c18)]
lines=[]
for a,b in ranges:
 lines.append('\n# %x..%x (bounded excerpt)'%(a,b))
 lines.extend('%08x  %-10s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str) for i in cs.disasm(raw[a-base:b-base],a))
(D/'original-disassembly.txt').write_text('\n'.join(lines)+'\n')
# Aligned literal references are raw data facts, not all indirect uses.
refs={hex(v):[hex(base+i) for i in range(0,len(raw)-3,4) if struct.unpack_from('<I',raw,i)[0]==v] for v in [0x2000065e,0x20000808,0x20000656,0x2000064c]}
# Scan each halfword: may include data/alternate decode; classify before use.
candidates=[]
for i in range(0,len(raw)-1,2):
 ins=next(cs.disasm(raw[i:i+4],base+i,count=1),None)
 if ins and ((ins.mnemonic=='ldr' and '#0x38]' in ins.op_str and 'pc,' not in ins.op_str) or (ins.mnemonic=='strh' and '#0x16]' in ins.op_str)):
  candidates.append({'address':hex(ins.address),'instruction':ins.mnemonic+' '+ins.op_str})
(D/'static-evidence.json').write_text(json.dumps({'firmware_sha256':hashlib.sha256(fw.read_bytes()).hexdigest(),'aligned_literal_references':refs,'candidate_halfword_scan':candidates,'limits':['Not control-flow reconstruction or exhaustive alias analysis. Candidate instructions can occur in data.','Absence of direct literal/access does not exclude generic transport, indirect alias, external callbacks or hardware processing.']},indent=2)+'\n')
