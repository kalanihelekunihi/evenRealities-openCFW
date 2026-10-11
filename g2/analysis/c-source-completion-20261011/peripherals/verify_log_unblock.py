#!/usr/bin/env python3
"""Bounded stock/source unordered event waiter removal, initialized lists."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
S=ROOT/'g2/components/main/extended_log_runtime_candidate/event_unblock.c'
L=ROOT/'g2/components/foundation/freertos_ready/list_subset.c'
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
objs=[]
for f in (S,L):
 o=OUT/(f.stem+'-m4.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(f),'-o',str(o)],check=True);objs.append(o)
elf=OUT/'log-unblock-m4.elf'
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_resume_next_unblock=0x101001','--defsym=opencfw_event_group_assert_failure=0x101011','-o',str(elf),*[str(x) for x in objs]],check=True)
with elf.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,priority,current_priority,wait_value):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def r(a):return int.from_bytes(u.mem_read(a,4),'little')
 event=0x20012000; delayed=0x20012100; tcb=0x20013000; cur=0x20014000
 item=tcb+24;state=tcb+4;elist_end=event+8;dlist_end=delayed+8
 ready=0x2006a49c+20*priority;ready_end=ready+8
 for lst,end,entry in ((event,elist_end,item),(delayed,dlist_end,state)):
  w(lst,1);w(lst+4,entry);w(end,0xffffffff);w(end+4,entry);w(end+8,entry)
  w(entry,0);w(entry+4,end);w(entry+8,end);w(entry+12,tcb);w(entry+16,lst)
 w(ready,0);w(ready+4,ready_end);w(ready_end,0xffffffff);w(ready_end+4,ready_end);w(ready_end+8,ready_end)
 w(tcb+44,priority);w(cur+44,current_priority);w(0x20074a20,cur);w(0x20074a58,1);w(0x20074a38,0);w(0x20074a44,0);w(0x20074a24,delayed);w(0x20074a50,1234)
 for reg,val in ((A.UC_ARM_REG_R0,item),(A.UC_ARM_REG_R1,wait_value),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  if pc==(0x455876 if stock else 0x101000):
   events.append('next_unblock');cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
  if pc==0x101010:raise AssertionError('unexpected assertion')
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x45547c if stock else SY['vTaskRemoveFromUnorderedEventList'])|1,0,count=3000)
 assert done[0],(stock,priority,current_priority)
 fields=[item,item+4,item+8,item+16,state+4,state+8,state+16,event,event+4,elist_end+4,elist_end+8,delayed,delayed+4,dlist_end+4,dlist_end+8,ready,ready+4,ready_end+4,ready_end+8,0x20074a38,0x20074a44,0x20074a50]
 return {'events':events,'values':{hex(a):r(a) for a in fields}}
rows=[]
for p,c,v in ((1,0,0),(1,1,0x35),(0,1,0xffffff),(3,1,0xffffffff)):
 a=run(True,p,c,v);b=run(False,p,c,v)
 if a!=b:
  (OUT/'log-unblock-failure.json').write_text(json.dumps({'p':p,'c':c,'v':v,'stock':a,'source':b},indent=2)+'\n');raise AssertionError((p,c,v))
 rows.append({'priority':p,'current_priority':c,'value':v,'result':a})
receipt={'status':'PASS_LOG_UNBLOCK_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'One initialized waiter/delayed item; next-unblock selected child cut; assertions and multiwaiter scheduler effects untested.'}
(OUT/'log-unblock-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
