#!/usr/bin/env python3
"""Fixed-image legacy entry branch frontier for every opcode and selected valid lengths."""
from pathlib import Path
import hashlib,json
from collections import Counter,defaultdict
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:]
covered=set(range(0xa0,0xb1))|{0xd0,0xd1,0xd2,0xd3,0xd4,0xdd,0xdf};prefix={0xee,0xff}
rows=[]
for opcode in range(256):
 for length in [0,1,2,4,8]:
  for flag in [0,1]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000)
   u.mem_write(0x20004000,bytes([opcode,0x55,0x66,0x77,0x88])+bytes(27));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087c,bytes(32));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
   stop=[]
   def code(uc,address,size,user):
    if not 0x08000928<=address<0x08000c68 and not 0x08009190<=address<0x080091aa:
     stop.append(address);uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,code)
   try:u.emu_start(0x08000929,0x20001000,count=10000);kind='lower' if stop else 'return';detail=hex(stop[0]) if stop else None
   except Exception as e:kind='error';detail=repr(e)
   rows.append(dict(opcode=opcode,length=length,flag=flag,kind=kind,detail=detail,return_value=u.reg_read(UC_ARM_REG_R0) if kind=='return' else None,known_dispatch=opcode in covered,prefix_only=opcode in prefix))
summary={}
for opcode in range(256):
 r=[x for x in rows if x['opcode']==opcode];summary[f'{opcode:02x}']=dict(kinds=dict(Counter(x['kind'] for x in r)),stops=sorted({x['detail'] for x in r if x['detail']}),known_dispatch=opcode in covered,prefix_only=opcode in prefix)
result=dict(status='BOUNDED_FIXED_IMAGE_BRANCH_FRONTIER',image_sha256=sha,logical_lengths=[0,1,2,4,8],log_flags=[0,1],cases=len(rows),counts=dict(Counter(x['kind'] for x in rows)),covered_opcodes=len(covered),prefix_opcodes=len(prefix),unsupported_opcodes=256-len(covered),per_opcode=summary,rows=rows,limits=['Length zero is reachable through decoded two-character de outer frame; test storage still allocates 32 bytes.','Stops before any code outside legacy entry/table helper; lower effects and nonreturn paths are not executed.','This is stock branch census, not source equivalence or public-handler completeness.'])
(D/'opcode-256-stock-frontier.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],result['cases'],result['counts'],'covered',len(covered),'prefix',len(prefix))
print('nontrivial unsupported',[(hex(i),summary[f'{i:02x}']['stops']) for i in range(256) if i not in covered and (summary[f'{i:02x}']['stops'] or summary[f'{i:02x}']['kinds'].get('error'))])
