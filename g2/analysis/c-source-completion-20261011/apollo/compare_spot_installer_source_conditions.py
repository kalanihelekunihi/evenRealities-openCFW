#!/usr/bin/env python3
"""Compare selected source branch/slot shape with bounded native installer output."""
from pathlib import Path
import json, hashlib
here=Path(__file__).resolve().parent
source=here.parents[2]/'components/bootloader/initializer_callbacks/startup_runtime.c'
text=source.read_text()
for marker in ('if(B(0x200271ad))','else if(B(0x200271a9))','else if(REV==33&&VAR==1)','slot(0x20,','slot(0x24,'):
 assert marker in text,marker
stock=json.loads((here/'boot-spot-installer-stock-matrix.json').read_text())
compared=[]
for case in stock['results']:
 rev,var=case['rev'],case['var']
 ad=int((rev==35 and var>=2) or rev>=36)
 a9=int((rev==34 and var==2) or (rev==35 and var==1))
 aa=int((rev==33 and var in (2,3)) or (rev==34 and var==0))
 ab=int(rev==33 and var>=3)
 ac=int((rev==34 and var==1) or (rev==35 and var==0))
 ae=int(((rev==34 and var==2) or (rev==35 and var==1)) and 1)
 flags=bytes((a9,aa,ab,ac,ad,ae)).hex()
 if ad:offsets={0,4,8,0x1c,0x28,0x2c}
 elif a9:offsets={0,4,8,0x14,0x18,0x1c,0x2c}
 elif (rev==33 and var>=2) or (rev==34 and var<2) or (rev==35 and var==0):offsets={0,4,8,0xc,0x10,0x18,0x1c,0x30,0x34,0x38}
 elif rev==33 and var==1:offsets={0,4,0x18,0x1c}
 else:offsets=set()
 if rev==33 and var<2:offsets|={0x20,0x24}
 actual=case['stock']
 assert actual['offsets']==sorted(offsets) and actual['flags']==flags,(rev,var,actual,sorted(offsets),flags)
 compared.append({'rev':rev,'var':var,'slot_offsets':sorted(offsets),'flags':flags})
out=here/'boot-spot-installer-condition-crosscheck.json'
r={'status':'PASS_STATIC_SOURCE_CONDITION_VS_NATIVE_STATE','cases':len(compared),'stock_receipt':'boot-spot-installer-stock-matrix.json','selected_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'comparisons':compared,'limits':['Selected side is condition-and-slot source model checked against selected C text markers; no selected M55 runtime execution.','Slot target identity and pointer relocation, MMIO read/write ordering, callback execution and external roots remain unqualified.']}
out.write_text(json.dumps(r,indent=2)+'\n')
print(r['status'],r['cases'])
