#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,re,hashlib,struct
P=Path(__file__).resolve().parent;R=P.parents[4];T=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin';B=R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin'
b=B.read_bytes();assert hashlib.sha256(b).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
ptr=struct.unpack('<10I',b[0x335300-0x302400:0x335328-0x302400]);o=P/'tables.o'
n=subprocess.check_output([str(T/'arc-elf32-nm'),'-S',str(o)],text=True);assert re.search(r'00000028 [RrD] opencfw_em9305_pcl_table_335300',n)
r=subprocess.check_output([str(T/'arc-elf32-objdump'),'-r','-j','.rodata.opencfw_pcl_table',str(o)],text=True)
actual={int(a,16):s for a,s in re.findall(r'([0-9a-f]{8}) R_ARC_32\s+(\w+)',r)};expected={i*4:f'opencfw_em9305_child_{v:x}' for i,v in enumerate(ptr) if v};assert actual==expected
subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.rodata.opencfw_pcl_table',str(o),str(P/'tables.bin')],check=True);assert (P/'tables.bin').read_bytes()==bytes(40)
z={'status':'PASS_NATIVE_TEN_SLOT_SOURCE_TABLE_RELOCATIONS','slots':10,'extent_bytes':40,'pointer_relocations':7,'zero_slots':[i for i,v in enumerate(ptr) if not v],'source_sha256':hashlib.sha256((P/'tables.c').read_bytes()).hexdigest(),'limits':['Native address named bodies independently crosswalked; SDK identity still provisional.','Dispatcher relocation, index proof, coherent link and final placement remain separate.']};(P/'tables-compile-receipt.json').write_text(json.dumps(z,indent=2)+'\n');print(z)
