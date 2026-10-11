#!/usr/bin/env python3
"""Bounded stock/source mutex-owned file heap free outer ABI."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_heap_free_candidate/file_heap_free.c';O=D/'file-heap-free-m4.o';E=D/'file-heap-free-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
syms={'audio_file_mutex_acquire':0x101001,'audio_file_mutex_release':0x101011,'g2_file_pool_free':0x101021,'g2_file_heap_error_log':0x101031,'g2_file_close_error':0x101041}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in syms.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4497b6:'audio_file_mutex_acquire',0x44981c:'audio_file_mutex_release',0x4d0808:'g2_file_pool_free',0x4733ee:'g2_file_heap_error_log',0x4d09b4:'g2_file_close_error'}
new={v-1:k for k,v in syms.items()}
def run(stock,status,buffer):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 u.mem_write(0x200748f8,(0x20020000).to_bytes(4,'little'));u.mem_write(0x20074abc,(0x20030000).to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,buffer),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if name:
   regs=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   events.append([name,regs[:3 if name=='g2_file_close_error' else 2 if name in ('audio_file_mutex_acquire','g2_file_pool_free') else 1]])
   cpu.reg_write(A.UC_ARM_REG_R0,status if name=='audio_file_mutex_acquire' else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x474d16 if stock else sy['audio_file_heap_free'])|1,0,count=180)
 assert done[0]
 return {'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for status in (0,1,0xffffffff):
 for buffer in (0,0x20035000):
  a=run(True,status,buffer);b=run(False,status,buffer);assert a==b,(status,buffer,a,b);rows.append([status,hex(buffer)])
out={'status':'PASS_FILE_HEAP_FREE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Mutex, pool free, log, and semihost diagnostic children cut; success/failure outer ABI only.'}
(D/'file-heap-free-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
