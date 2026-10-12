#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4];T=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
o=P/'tables.o';dump=subprocess.check_output([str(T/'arc-elf32-objdump'),'-t','-r',str(o)],text=True)
subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.rodata',str(o),str(P/'tables.rodata.bin')],check=True)
b=(P/'tables.rodata.bin').read_bytes();binding=json.loads((P/'sdk-action-slot-binding.json').read_text())
def extent(name):
 m=re.search(r'^([0-9a-f]+)\s+g\s+O\s+\.rodata\s+([0-9a-f]+) '+name+'$',dump,re.M);assert m,name
 return int(m[1],16),int(m[2],16)
sw,sz=extent('opencfw_em9305_enc_switch_3344b7');assert sz==9;assert b[sw:sw+sz]==(P/'slave-switch-table.bin').read_bytes();a,n=extent('opencfw_em9305_enc_actions_335564');t,z=extent('opencfw_em9305_enc_transitions_335628');assert (n,z)==(196,49)
actual={int(x,16):y for x,y in re.findall(r'^([0-9a-f]+)\s+R_ARC_32\s+(\w+)$',dump,re.M)}
expected={a+s['offset']:('opencfw_em9305_child_' if s['native_target']=='31b714' else 'opencfw_em9305_enc_action_')+s['native_target'] for s in binding['slots'] if s['native_target']}
assert actual==expected;assert b[a:a+n]==bytes(n);assert b[t:t+z]==(P/'slave-NextStateTbl.bin').read_bytes()
native=(R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(native).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03';assert b[t:t+z]==native[0x335628-0x302400:0x335628-0x302400+49]
r={'status':'PASS_ALL_TABLE_EXTENTS_RELOCATIONS_AND_TRANSITION_BYTES','slots':49,'callback_relocations':len(actual),'zero_slots':17,'transition_bytes':49,'switch_bytes':9,'source_sha256':hashlib.sha256((P/'tables.c').read_bytes()).hexdigest(),'limits':['Final placement and runtime state/event bounds remain open.']};(P/'tables-compile-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
