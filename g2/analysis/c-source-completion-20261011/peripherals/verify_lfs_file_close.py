#!/usr/bin/env python3
"""Bounded stock/source LittleFS close worker with typed child cuts."""
from pathlib import Path
import subprocess,hashlib,json
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_backend_close_candidate/file_close.c';O=D/'lfs-file-close-m4.o';E=D/'lfs-file-close-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
syms={'g2_lfs_file_sync':0x101001,'g2_lfs_mlist_remove':0x101011,'g2_lfs_free':0x101021}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in syms.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];named={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,has_buffer,child_result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 u.mem_write(0x20012050,(0x20013000).to_bytes(4,'little'))
 u.mem_write(0x2001204c,(0x20014000).to_bytes(4,'little'))
 u.mem_write(0x20013000,(0x20015000 if has_buffer else 0).to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20011000),(A.UC_ARM_REG_R1,0x20012000),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 event=[];done=[False];old={0x4cdf74:'sync',0x4cb0a0:'remove',0x4ca812:'free'};new={0x101000:'sync',0x101010:'remove',0x101020:'free'}
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if n:
   event.append([n,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1) if n!='free' else None]);cpu.reg_write(A.UC_ARM_REG_R0,child_result if n=='sync' else 0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cdce4 if stock else named['g2_lfs_file_close'])|1,0,count=100)
 assert done[0]
 return {'result':u.reg_read(A.UC_ARM_REG_R0),'events':event,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for h in (0,1):
 for x in (0,0xffffffff):
  a=run(True,h,x);b=run(False,h,x);assert a==b,(h,x,a,b);rows.append({'has_buffer':h,'child_result':x})
out={'status':'PASS_LFS_FILE_CLOSE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Pinned sync/list-remove/free child calls cut; no storage writes or real heap lifecycle.'}
(D/'lfs-file-close-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
