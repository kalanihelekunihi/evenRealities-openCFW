#!/usr/bin/env python3
"""Stock/source TLSF pool free outer call graph and ABI."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_pool_free_candidate/pool_free.c';O=D/'pool-free-m4.o';E=D/'pool-free-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
names=['g2_tlsf_block_from_ptr','g2_tlsf_block_is_free','g2_tlsf_block_mark_free','g2_tlsf_block_merge_prev','g2_tlsf_block_merge_next','g2_tlsf_block_insert','g2_file_close_error'];addr={k:0x101000+16*i for i,k in enumerate(names)}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v+1:#x}' for k,v in addr.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cfe04:'from',0x4cfdb4:'isfree',0x4cfe96:'mark',0x4d02d6:'prev',0x4d033a:'next',0x4d019a:'insert',0x4d09b4:'error'};new={addr[n]:s for n,s in zip(names,['from','isfree','mark','prev','next','insert','error'])}
def run(stock,pointer,isfree):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,pointer),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if n:
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)];events.append([n,r[:3 if n=='error' else 2 if n in ('prev','next','insert') else 1]])
   ret={'from':0x20021000,'isfree':isfree,'mark':0,'prev':0x20022000,'next':0x20023000,'insert':0,'error':0}[n]
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4d0808 if stock else sy['g2_file_pool_free'])|1,0,count=120)
 assert done[0]
 return {'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for pointer in (0,0x20030000):
 for isfree in (0,1):
  a=run(True,pointer,isfree);b=run(False,pointer,isfree);assert a==b,(pointer,isfree,a,b);rows.append([hex(pointer),isfree])
out={'status':'PASS_POOL_FREE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'TLSF helper and semihost diagnostic effects cut; no actual block coalescing/free-list mutation.'}
(D/'pool-free-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
