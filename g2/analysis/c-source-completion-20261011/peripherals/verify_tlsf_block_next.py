#!/usr/bin/env python3
"""Stock/source TLSF physical next-block calculation."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_pool_free_candidate/tlsf_block_next.c';O=D/'tlsf-block-next-m4.o';E=D/'tlsf-block-next-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_file_close_error=0x101001','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,size,ff,pf,offset,overhead):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 for a,v in ((0x78f4b4,ff),(0x78f4b8,pf),(0x78f4c0,offset),(0x78f4bc,overhead),(0x20010004,size|ff)):
  u.mem_write(a,v.to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  if pc==(0x4d09b4 if stock else 0x101000):
   events.append([cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]);cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cfe44 if stock else sy['g2_tlsf_block_next'])|1,0,count=100)
 assert done[0]
 return {'next':u.reg_read(A.UC_ARM_REG_R0),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for size in (0,8,32,256):
 for ff,pf,off,over in ((1,2,8,4),(2,1,12,8)):
  a=run(True,size,ff,pf,off,over);b=run(False,size,ff,pf,off,over);assert a==b,(size,ff,pf,off,over,a,b);rows.append([size,ff,pf,off,over])
out={'status':'PASS_TLSF_BLOCK_NEXT_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Controlled TLSF configuration words; last-block semihost diagnostic cut; no actual heap walk.'}
(D/'tlsf-block-next-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
