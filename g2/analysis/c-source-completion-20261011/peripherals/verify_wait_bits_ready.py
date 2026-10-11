#!/usr/bin/env python3
"""Stock/source event wait ready and zero-timeout states; deeper children cut."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/event_wait_source_candidate/wait_bits.c';O=D/'wait-bits-m4.o';E=D/'wait-bits-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
names=['audio_scheduler_state','audio_suspend','stock_scheduler_resume','audio_yield','stock_enter_critical','stock_exit_critical','g2_event_place_unordered','g2_event_reset_item_value','g2_event_wait_assert']
addr={k:0x101000+16*i for i,k in enumerate(names)}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v+1:#x}' for k,v in addr.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4558a4:'audio_scheduler_state',0x454d7c:'audio_suspend',0x454dcc:'stock_scheduler_resume',0x47ee30:'condition'}
new={v:k for k,v in addr.items()}
def run(stock,bits,request,clear,all,timeout):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 u.mem_write(0x20010000,bits.to_bytes(4,'little'));u.mem_write(0x2007f000,timeout.to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,request),(A.UC_ARM_REG_R2,clear),(A.UC_ARM_REG_R3,all),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if name:
   if name=='condition':
    a,b,c=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
    ret=int((a&b)==b if c else (a&b)!=0)
   else:
    events.append(name);ret=1 if name=='audio_scheduler_state' else 0
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x47ebf8 if stock else sy['g2_event_wait_bits'])|1,0,count=300)
 assert done[0]
 return {'result':u.reg_read(A.UC_ARM_REG_R0),'bits':int.from_bytes(u.mem_read(0x20010000,4),'little'),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for bits,request in ((0,1),(1,1),(2,1),(3,1),(3,3)):
 for clear in (0,1):
  for all in (0,1):
   a=run(True,bits,request,clear,all,0);b=run(False,bits,request,clear,all,0)
   assert a==b,(bits,request,clear,all,a,b)
   rows.append([bits,request,clear,all,a['result']])
out={'status':'PASS_EVENT_WAIT_READY_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Immediate and zero-timeout paths only; blocked waiter placement and resumed task path remain unvalidated.'}
(D/'wait-bits-ready-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
