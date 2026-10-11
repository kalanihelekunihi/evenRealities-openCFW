#!/usr/bin/env python3
"""Stock/source LittleFS block-device sync ABI."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_sync_candidate/bd_sync.c';O=D/'bd-sync-m4.o';E=D/'bd-sync-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
args=['--defsym=g2_lfs_cache_drop=0x101001','--defsym=g2_lfs_bd_flush=0x101011','--defsym=g2_file_close_error=0x101021']
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*args,'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4ca81a:'flush',0x4caafa:'prog',0x4d09b4:'error'};new={0x101000:'flush',0x101010:'prog',0x101020:'error'}
def run(stock,validate,prog,sync):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 u.mem_write(0x20010068,(0x20012000).to_bytes(4,'little'))
 u.mem_write(0x20012010,(0x101031).to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,0x20011000),(A.UC_ARM_REG_R2,0x20011100),(A.UC_ARM_REG_R3,validate),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if pc==0x101030:n='sync'
  if n:
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   events.append([n,r[:4 if n=='prog' else 3 if n=='error' else 2 if n=='flush' else 1]])
   cpu.reg_write(A.UC_ARM_REG_R0,prog if n=='prog' else sync if n=='sync' else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cabbc if stock else sy['g2_lfs_bd_sync'])|1,0,count=150)
 assert done[0]
 return {'result':u.reg_read(A.UC_ARM_REG_R0),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for v in (0,1,0x101):
 for p,s in ((0,0),(0xffffffff,0),(0,1),(0,0xffffffff)):
  a=run(True,v,p,s);b=run(False,v,p,s);assert a==b,(v,p,s,a,b);rows.append([v,p,s])
out={'status':'PASS_BD_SYNC_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Flush/prog/config-sync/semihost child effects cut; no actual flash writes.'}
(D/'bd-sync-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
