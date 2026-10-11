#!/usr/bin/env python3
"""Stock/source TLSF list-wrapper size-class and child ABI."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_pool_free_candidate/tlsf_lists.c';O=D/'tlsf-lists-m4.o';E=D/'tlsf-lists-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
syms={'g2_tlsf_block_size':0x101001,'g2_tlsf_mapping_insert':0x101011,'g2_tlsf_remove_free_block':0x101021,'g2_tlsf_insert_free_block':0x101031}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in syms.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cfd70:'size',0x4cff6c:'mapping',0x4d003a:'remove',0x4d00d0:'insert'};new={0x101000:'size',0x101010:'mapping',0x101020:'remove',0x101030:'insert'}
def run(stock,which,size):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,0x20011000),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if n:
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if n=='mapping':
    events.append([n,r[0]]);cpu.mem_write(r[1],(3).to_bytes(4,'little'));cpu.mem_write(r[2],(7).to_bytes(4,'little'))
   elif n in ('remove','insert'):events.append([n,r])
   else:events.append([n,r[0]])
   cpu.reg_write(A.UC_ARM_REG_R0,size if n=='size' else 0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(((0x4d0178 if which=='remove' else 0x4d019a) if stock else sy['g2_tlsf_block_'+which])|1,0,count=100)
 assert done[0]
 return events
rows=[]
for w in ('remove','insert'):
 for size in (4,32,4096):
  a=run(True,w,size);b=run(False,w,size);assert a==b,(w,size,a,b);rows.append([w,size])
out={'status':'PASS_TLSF_LIST_WRAPPERS','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Mapping and free-list mutation children cut; exact class values injected for ABI check.'}
(D/'tlsf-lists-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
