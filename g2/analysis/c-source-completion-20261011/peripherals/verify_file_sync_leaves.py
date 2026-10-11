#!/usr/bin/env python3
"""Stock/source LittleFS pair-null and target endian leaves."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_sync_candidate/file_sync_leaves.c';O=D/'file-sync-leaves-m4.o';E=D/'file-sync-leaves-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,which,a,b):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for x,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(x,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for x,d in seg:u.mem_write(x,d)
 u.mem_write(0x20010000,a.to_bytes(4,'little')+b.to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(((0x4cadd0 if which=='pair' else 0x4cb000) if stock else sy['g2_lfs_pair_isnull' if which=='pair' else 'g2_lfs_ctz_tole32'])|1,0,count=80)
 assert done[0]
 return {'value':u.reg_read(A.UC_ARM_REG_R0) if which=='pair' else None,'bytes':u.mem_read(0x20010000,8).hex()}
rows=[]
for a,b in ((0,0),(0xffffffff,0),(0,0xffffffff),(0xffffffff,0xffffffff),(0x12345678,0xabcdef01)):
 for w in ('pair','ctz'):
  x=run(True,w,a,b);y=run(False,w,a,b);assert x==y,(w,a,b,x,y);rows.append([w,a,b])
out={'status':'PASS_FILE_SYNC_LEAVES','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Synthetic pair/CTZ words; no directory commit or disk effects.'}
(D/'file-sync-leaves-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
