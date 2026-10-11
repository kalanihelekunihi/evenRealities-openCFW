#!/usr/bin/env python3
"""Bounded stock/source littlefs membership execution."""
from pathlib import Path
import subprocess,hashlib,json
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_backend_close_candidate/mlist_isopen.c'
O=D/'mlist-isopen-m4.o';E=D/'mlist-isopen-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f); seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,head,needle):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 for a,n in ((0x20010000,0x20010010),(0x20010010,0x20010020),(0x20010020,0)):
  u.mem_write(a,n.to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,head),(A.UC_ARM_REG_R1,needle),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cb082 if stock else sy['g2_lfs_mlist_isopen'])|1,0,count=100)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),u.reg_read(A.UC_ARM_REG_SP)
rows=[]
for h in (0,0x20010000):
 for n in (0,0x20010000,0x20010010,0x20010020,0x20010030):
  a=run(True,h,n);b=run(False,h,n);assert a==b,(h,n,a,b);rows.append([hex(h),hex(n),a[0]])
receipt={'status':'PASS_MLIST_ISOPEN_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Three-node synthetic list and null head; memory corruption/cycles excluded.'}
(D/'mlist-isopen-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
