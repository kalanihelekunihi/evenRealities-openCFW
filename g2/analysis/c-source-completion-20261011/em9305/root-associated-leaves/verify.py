#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[4]
T=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
n=(ROOT/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(n).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.text',str(P/'source.o'),str(P/'text.bin')],check=True);raw=(P/'text.bin').read_bytes();assert raw[:12]==n[0x31b7bc-0x302400:0x31b7c8-0x302400];assert raw[12:24]==n[0x3294fc-0x302400:0x329508-0x302400]
subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.text',str(P/'time-alias-review.elf'),str(P/'time-alias.bin')],check=True);assert (P/'time-alias.bin').read_bytes()==n[0x30fd34-0x302400:0x30fd38-0x302400]
r={'status':'PASS_THREE_COMPLETE_NATIVE_FUNCTION_BYTE_BINDINGS','functions':['31b7bc','3294fc','30fd34'],'native_bytes':[12,12,4],'source_sha256':hashlib.sha256((P/'source.c').read_bytes()).hexdigest(),'alias_source_sha256':hashlib.sha256((P/'time-alias.c').read_bytes()).hexdigest(),'selected':False,'limits':['Time alias uses an isolated review link with authenticated child address; this is not a production provider.','No physical hardware or full image proof.']}
(P/'combined-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
