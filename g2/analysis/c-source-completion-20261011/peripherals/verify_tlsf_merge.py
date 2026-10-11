#!/usr/bin/env python3
"""Stock/source TLSF coalescing outer ABI."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_pool_free_candidate/tlsf_merge.c';O=D/'tlsf-merge-m4.o';E=D/'tlsf-merge-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
names=['g2_tlsf_block_is_prev_free','g2_tlsf_block_prev','g2_tlsf_block_is_free','g2_tlsf_block_next','g2_tlsf_block_is_last','g2_tlsf_block_remove','g2_tlsf_block_absorb','g2_file_close_error'];addr={k:0x101000+16*i for i,k in enumerate(names)}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v+1:#x}' for k,v in addr.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cfddc:'prevfree',0x4cfe1e:'prev',0x4cfdb4:'isfree',0x4cfe44:'next',0x4cfda0:'islast',0x4d0178:'remove',0x4d0294:'absorb',0x4d09b4:'error'};new={addr[n]:s for n,s in zip(names,['prevfree','prev','isfree','next','islast','remove','absorb','error'])}
def run(stock,which,flag):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,0x20011000),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if n:
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   events.append([n,r[:3 if n=='error' else 2 if n in ('remove','absorb') else 1]])
   ret={'prevfree':flag,'prev':0x20012000,'isfree':flag if which=='next' else 1,'next':0x20013000,'islast':0,'remove':0,'absorb':0x20014000,'error':0}[n]
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(((0x4d02d6 if which=='prev' else 0x4d033a) if stock else sy['g2_tlsf_block_merge_'+which])|1,0,count=140)
 assert done[0]
 return {'result':u.reg_read(A.UC_ARM_REG_R0),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for w in ('prev','next'):
 for flag in (0,1):
  a=run(True,w,flag);b=run(False,w,flag);assert a==b,(w,flag,a,b);rows.append([w,flag])
out={'status':'PASS_TLSF_MERGE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Child block search/remove/absorb effects cut; valid nonnull physical blocks, no real coalescing.'}
(D/'tlsf-merge-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
