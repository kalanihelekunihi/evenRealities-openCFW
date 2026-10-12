"""Verify observed compiled setter does not clobber native caller R8 status."""
from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4]
T=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
O=R/'g2/build/c-firmware/20261012/em-root-dispatch-round47/ble_em9305/candidate.o'
S=R/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
symbol='opencfw_em9305_associated_set_3338f4'
nm=subprocess.check_output([str(T/'arc-elf32-nm'),'-S',str(O)],text=True)
match=re.search(r'^([0-9a-f]+) ([0-9a-f]+) T '+symbol+r'$',nm,re.M);assert match
start,size=map(lambda x:int(x,16),match.groups())
dis=subprocess.check_output([str(T/'arc-elf32-objdump'),'-d','-Mcpu=em,dsp','--disassemble='+symbol,str(O)],text=True)
(P/'associated-set-compiled.txt').write_text(dis)
rows=[]
for line in dis.splitlines():
 v=line.split('\t')
 if len(v)>=3 and re.fullmatch(r'\s*[0-9a-f]+:',v[0]):
  address=int(v[0].strip()[:-1],16);assert start<=address<start+size
  m=v[2].strip();operand=v[3].strip() if len(v)>3 else '';rows.append((address,m,operand))
assert rows and rows[0][0]==start and rows[-1][0]==start+size-2
assert not any(re.search(r'(?<![\w])r8(?![\w])',o) for a,m,o in rows)
assert not any(m.startswith('bl') or m.startswith('jl') for a,m,o in rows)
assert all('[blink]' in o for a,m,o in rows if m.startswith('j'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'PASS_COMPILED_SETTER_PRESERVES_R8_WITH_NO_NESTED_CALLS','caller':'3136fc','status_capture':'313724','setter_call':'313738','status_return':'313740','compiled_setter':symbol,'compiled_setter_bytes':size,'compiled_instructions':len(rows),'candidate_sha256':sha(O),'controller_source_sha256':sha(S),'caller_source_sha256':sha(P/'source.c'),'limits':['Proof is specific to the Round47 compiled setter and current source snapshot. Recheck after compiler/provider changes.','Does not establish ISR preservation, state bounds, runtime operation or full image equivalence.']}
(P/'r8-preservation-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
