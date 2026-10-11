#!/usr/bin/env python3
"""Stock/source bounded FreeRTOS task scheduling and ready insertion."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
S=ROOT/'g2/components/audio/thread_new_source_candidate/schedule_tcb.c';L=ROOT/'g2/components/foundation/freertos_ready/list_subset.c'
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
objs=[]
for src in (S,L):
 obj=OUT/(src.stem+'-schedule-m4.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(src),'-o',str(obj)],check=True);objs.append(obj)
ELF=OUT/'thread-schedule-m4.elf'
defs=['stock_enter_critical=0x101001','stock_exit_critical=0x101011','audio_yield=0x101021','g2_thread_initialize_lists=0x101031']
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={x}' for x in defs],'-o',str(ELF),*[str(o) for o in objs]],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,prior_current,priority,running):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def r(a):return int.from_bytes(u.mem_read(a,4),'little')
 tcb=0x20012000;cur=0x20013000;lst=0x2006a49c+20*priority;end=lst+8
 w(tcb+44,priority);w(cur+44,prior_current or 0);w(0x20074a20,cur if prior_current is not None else 0)
 w(0x20074a30,0 if prior_current is None else 1);w(0x20074a4c,7);w(0x20074a38,prior_current or 0);w(0x20074a3c,running)
 w(lst,0);w(lst+4,end);w(end,0xffffffff);w(end+4,end);w(end+8,end)
 for reg,val in ((A.UC_ARM_REG_R0,tcb),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 done=[False];events=[]
 old={0x4420d0:'enter',0x4420e8:'exit',0x4420bc:'yield',0x45568c:'init'}
 new={0x101000:'enter',0x101010:'exit',0x101020:'yield',0x101030:'init'}
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if name:events.append(name);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4549fc if stock else SY['g2_thread_schedule_tcb'])|1,0,count=1200)
 assert done[0]
 addresses=[0x20074a20,0x20074a30,0x20074a4c,0x20074a38,0x20074a3c,tcb+8,tcb+12,tcb+20,tcb+88,lst,lst+4,end+4,end+8]
 return {'events':events,'values':{hex(a):r(a) for a in addresses},'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for cur,p,running in ((None,1,0),(1,2,0),(2,1,0),(1,2,1),(2,1,1)):
 a=run(True,cur,p,running);b=run(False,cur,p,running)
 if a!=b:
  f={'current_priority':cur,'new_priority':p,'running':running};(OUT/'thread-schedule-failure.json').write_text(json.dumps({'fixture':f,'stock':a,'source':b},indent=2)+'\n');raise AssertionError(f)
 rows.append({'current_priority':cur,'new_priority':p,'running':running})
result={'status':'PASS_THREAD_SCHEDULE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'Critical/yield/list-init children cut, ready-list insert selected source executes; no preemption/hardware task switch proof.'}
(OUT/'thread-schedule-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows))
