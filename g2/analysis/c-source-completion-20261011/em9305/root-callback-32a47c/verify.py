#!/usr/bin/env python3
from pathlib import Path
import subprocess,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[4]
T=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
B=ROOT/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin';n=B.read_bytes()
assert hashlib.sha256(n).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.text',str(P/'source.o'),str(P/'text.bin')],check=True)
a=(P/'text.bin').read_bytes();expected=n[0x32a47c-0x302400:0x32a4be-0x302400];assert a[:66]==expected
r={'status':'PASS_COMPLETE_NATIVE_FUNCTION_BYTE_BINDING','native_function_bytes':66,'target_function_bytes':66,'trailing_alignment_bytes':len(a)-66,'source_sha256':hashlib.sha256((P/'source.c').read_bytes()).hexdigest(),'selected':False,'imports':0,'limits':['No hardware execution or final image proof.']}
(P/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
