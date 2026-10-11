#!/usr/bin/env python3
"""Stock/source TLSF block absorption with leaf cuts."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_pool_free_candidate/tlsf_absorb.c';O=D/'tlsf-absorb-m4.o';E=D/'tlsf-absorb-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
syms={'g2_tlsf_block_is_last':0x101001,'g2_tlsf_block_size':0x101011,'g2_tlsf_block_link_next':0x101021,'g2_file_close_error':0x101031}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in syms.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cfda0:'last',0x4cfd70:'size',0x4cfe88:'link',0x4d09b4:'error'};new={0x101000:'last',0x101010:'size',0x101020:'link',0x101030:'error'}
def run(stock,last,size,overhead):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 u.mem_write(0x78f4bc,overhead.to_bytes(4,'little'));u.mem_write(0x20010004,(0x100).to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,0x20011000),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if n:
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)];events.append([n,r[:3 if n=='error' else 1]])
   ret={'last':last,'size':size,'link':0x20012000,'error':0}[n];cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4d0294 if stock else sy['g2_tlsf_block_absorb'])|1,0,count=100)
 assert done[0]
 return {'ret':u.reg_read(A.UC_ARM_REG_R0),'sizeword':int.from_bytes(u.mem_read(0x20010004,4),'little'),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for last in (0,1):
 for size in (8,32):
  for over in (4,8):
   a=run(True,last,size,over);b=run(False,last,size,over);assert a==b,(last,size,over,a,b);rows.append([last,size,over])
out={'status':'PASS_TLSF_ABSORB_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Block-size/link-next and diagnostic children cut; no actual neighbor linkage.'}
(D/'tlsf-absorb-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
