#!/usr/bin/env python3
"""CASE 0x1574 bounded native/source outer OTA file state machine at child cuts."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_box_file_open_candidate.c';obj=H/'box_open.oracle.o';stub=H/'box_open.oracle_stub.c';stubobj=H/'box_open.oracle_stub.o';elf=H/'box_open.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
names={'wait':'case_policy_wait','log':'case_policy_log','crc':'case_policy_ota_checksum','send':'case_policy_ota_transmit','parse':'case_policy_parse_probe','bank':'case_policy_box_running_bank','erase':'case_policy_box_erase_bank','copy':'case_policy_box_copy_sn','apply':'case_policy_box_apply_file','chunk':'case_policy_box_write_chunk'}
ret={'wait':'void','log':'uint32_t','crc':'void','send':'uint32_t','parse':'uint32_t','bank':'uint32_t','erase':'uint32_t','copy':'uint32_t','apply':'uint32_t','chunk':'uint32_t'}
proto={'wait':'uint32_t a','log':'uint32_t a','crc':'uint8_t *a,uint32_t b','send':'uint32_t a,const uint8_t *b,uint32_t c,uint32_t d','parse':'uint32_t a','bank':'void','erase':'void','copy':'void','apply':'void','chunk':'uint32_t a'}
stub.write_text('#include <stdint.h>\n'+''.join(f'{ret[k]} {v}({proto[k]})'+'{'+('return 0;' if ret[k]!='void' else '')+'}\n' for k,v in names.items()))
subprocess.run([x for x in flags if x not in ('-Wall','-Wextra','-Werror')]+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
original={0x0800a7b0:'wait',0x08009170:'log',0x08009b70:'crc',0x08002744:'send',0x08001e94:'parse',0x08002f46:'bank',0x08002d48:'erase',0x08002b4c:'copy',0x08002cc0:'apply',0x08002e04:'chunk'}
rng=random.Random(0x1574)
for i in range(160):
 stage=i%6;quiet=i%2;size=20 if stage==5 else 0;bank=(i%4)+1
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000bf,bytes([quiet]));u.mem_write(0x2000089c,struct.pack('<I',size))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=original if native else {sym[v]&~1:k for k,v in names.items()};calls=[];parse_count=[0]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind=='log':calls.append((kind,bytes(uc.mem_read(x,90)).split(b'\0')[0]))
   elif kind=='crc':calls.append((kind,y,bytes(uc.mem_read(x,y))))
   elif kind=='send':calls.append((kind,x,z,w,bytes(uc.mem_read(y,z))))
   elif kind=='chunk':calls.append((kind,x,y,z))
   else:calls.append((kind,x if kind in ('wait','parse') else None))
   result=0
   if kind=='parse':result=0x59 if stage!=0 or parse_count[0]>0 else 0;parse_count[0]+=1
   elif kind=='bank':result=bank if stage!=1 else 0
   elif kind=='erase':result=0 if stage==2 else 1
   elif kind=='copy':result=0 if stage==3 else 1
   elif kind=='apply':result=0x98765432
   elif kind=='chunk':result=1;uc.mem_write(0x200008a8,bytes([20]))
   elif kind=='wait' and uc.mem_read(0x200000bc,1)[0]!=0 and len(calls)<2:uc.mem_write(0x200000bc,b'\0')
   if kind=='parse' and parse_count[0]>1:uc.mem_write(0x200008a4,struct.pack('<I',0x20004000));uc.mem_write(0x200008a8,b'\x14')
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08001574 if native else sym['case_policy_box_file_open'])|1,0x20008000,count=10000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200000bc,4)),bytes(u.mem_read(0x2000087c,64))))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOX_FILE_OPEN',160)
