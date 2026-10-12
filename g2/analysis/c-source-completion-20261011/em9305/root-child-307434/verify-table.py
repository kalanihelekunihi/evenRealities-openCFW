#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4];T=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
s=subprocess.check_output([str(T/'arc-elf32-objdump'),'-t','-r',str(P/'table.o')],text=True)
m=re.search(r'^([0-9a-f]+)\s+g\s+O\s+\.rodata\s+([0-9a-f]+) opencfw_em9305_proc_pending_334479$',s,re.M);assert m;off,size=int(m[1],16),int(m[2],16);assert size==15 and 'R_ARC_' not in s
subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.rodata',str(P/'table.o'),str(P/'table.rodata.bin')],check=True);b=(P/'table.rodata.bin').read_bytes();assert b[off:off+size]==(P/'sdk-switch.bin').read_bytes();assert b[off+size:]==bytes(len(b)-off-size)
r={'status':'PASS_COMPILED_TABLE_EXTENT_AND_ALL_FIFTEEN_BYTES','object_bytes':size,'section_bytes':len(b),'trailing_alignment_bytes':len(b)-off-size,'relocations':0,'source_sha256':hashlib.sha256((P/'table.c').read_bytes()).hexdigest(),'limits':['Final placement remains open.']};(P/'table-compile-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
