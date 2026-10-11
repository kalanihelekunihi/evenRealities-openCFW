#!/usr/bin/env python3
"""Bounded stock/source CMSIS osThreadNew outer ABI comparisons."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/audio/thread_new_source_candidate/thread_new.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'thread-new-m4.o';ELF=OUT/'thread-new-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
defs=['audio_irq_context=0x101001','audio_daemon_create_static=0x101011','g2_thread_create_dynamic=0x101021']
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={x}' for x in defs],'-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,kind,irq,status):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def r(a):return int.from_bytes(u.mem_read(a,4),'little')
 attrs=0x20010000
 data={'dynamic':(0x20011000,0,0,0,0,0,54),'static':(0x20011000,0,0x20012000,0x70,0x20013000,4096,54),'invalid_priority':(0,0,0,0,0,0,57),'invalid_partial':(0,0,0x20012000,0,0,0,30),'invalid_bits':(0,1,0,0,0,0,24)}
 if kind in data:
  name,bits,cb,cbsize,stack,stacksize,priority=data[kind]
  for i,v in enumerate((name,bits,cb,cbsize,stack,stacksize,priority,0,0)):w(attrs+4*i,v)
 argument=0x20015500
 for reg,val in ((A.UC_ARM_REG_R0,0 if kind=='null_entry' else 0x20014401),(A.UC_ARM_REG_R1,argument),(A.UC_ARM_REG_R2,0 if kind in ('null_attrs','null_entry') else attrs),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 calls=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  old={0x44900e:'irq',0x454820:'static',0x4548ba:'dynamic'}
  new={0x101000:'irq',0x101010:'static',0x101020:'dynamic'}
  name=(old if stock else new).get(pc)
  if name:
   args=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if name!='irq':
    sp=cpu.reg_read(A.UC_ARM_REG_SP);extra=[r(sp+4*i) for i in range(3 if name=='static' else 2)];args+=extra
    if name=='dynamic' and status==1:w(extra[1],0x20016600)
   calls.append([name,args if name!='irq' else []]);cpu.reg_write(A.UC_ARM_REG_R0,irq if name=='irq' else 0x20017700 if name=='static' else status)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4490e2 if stock else SY['osThreadNew'])|1,0,count=2000)
 assert done[0],(stock,kind,irq,status)
 return {'r0':u.reg_read(A.UC_ARM_REG_R0),'calls':calls,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for kind,irq,status in [(k,i,s) for k in ('null_attrs','dynamic','static','invalid_priority','invalid_partial','invalid_bits','null_entry') for i,s in ((0,1),(0,0),(1,1))]:
 a=run(True,kind,irq,status);b=run(False,kind,irq,status)
 if a!=b:
  (OUT/'thread-new-failure.json').write_text(json.dumps({'kind':kind,'irq':irq,'status':status,'stock':a,'source':b},indent=2)+'\n');raise AssertionError((kind,irq,status))
 rows.append({'kind':kind,'irq':irq,'status':status,'result':a})
result={'status':'PASS_THREAD_NEW_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'IRQ context and static/dynamic FreeRTOS task constructors cut; compares outer ABI, not allocation, scheduler, product attributes or live thread.'}
(OUT/'thread-new-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows))
