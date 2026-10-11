#!/usr/bin/env python3
"""Bounded stock/source selector4 state and call-order comparison."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[4]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/pcm22_remaining.c'
DATA=ROOT/'g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/initialized_data.c'
LOCKED='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert hashlib.sha256(STOCK.read_bytes()).hexdigest()==LOCKED
with tempfile.TemporaryDirectory(prefix='boot-selector4-') as td:
 d=Path(td);obj=d/'selector.o';stubs=d/'stubs.o';elfpath=d/'selector.elf'
 cc=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections']
 subprocess.run(cc+['-c',str(SOURCE),'-o',str(obj)],check=True)
 names=['opencfw_hal_delay_us','opencfw_pcm22_timer_service','event_a_power_ton_adjust']
 (d/'stubs.S').write_text('.syntax unified\n.thumb\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\nbx lr\n' for n in names)+'.section .note.GNU-stack,"",%progbits\n')
 subprocess.run(cc+['-c',str(d/'stubs.S'),'-o',str(stubs)],check=True)
 subprocess.run(['arm-none-eabi-ld','--gc-sections','-u','opencfw_spot_pcm22_transition4','-Ttext=0x500000',str(obj),str(stubs),'-o',str(elfpath)],check=True)
 with elfpath.open('rb') as f:
  e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
  segments=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 cases=[]
 for label,active,ready,word in [('inactive-zero',0,0,0),('inactive-fields',0,1,0x0d9f5ca5),('active-ready',1,1,0x0a8e1234),('active-timeout',1,0,0x0f6a55ab)]:
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x410000,0x40000);u.mem_write(0x410000,STOCK.read_bytes())
   u.mem_map(0x500000,0x10000)
   if not native:
    for a,b in segments:u.mem_write(a,b)
   u.mem_map(0x20000000,0x40000);u.mem_map(0x40008000,0x1000);u.mem_map(0x40020000,0x2000)
   profile=0x20026ba0;target=3;current=1;ton=9;old_ton=6
   u.mem_write(profile+0x64,struct.pack('<I',0x12345678))
   u.mem_write(profile+4+current*4,struct.pack('<I',0x0456789a))
   u.mem_write(profile+4+target*4,struct.pack('<I',word))
   u.mem_write(0x400083e0,struct.pack('<I',active))
   u.mem_write(0x40008064,struct.pack('<I',0x40000000 if ready else 0))
   for a,v in ((0x40020080,0xa5a55a5a),(0x40020044,0x5a5aa5a5),(0x4002004c,0xf0f0f0f0),(0x4002037c,0xffffffff)):u.mem_write(a,struct.pack('<I',v))
   calls=[];writes=[]
   targets={0x41d1c0:'delay',0x42a04a:'timer',0x42a1bc:'adjust'} if native else {symbols['opencfw_hal_delay_us']&~1:'delay',symbols['opencfw_pcm22_timer_service']&~1:'timer',symbols['event_a_power_ton_adjust']&~1:'adjust'}
   def on_code(uc,a,size,data):
    if a in targets:
     kind=targets[a]
     calls.append([kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)] if kind=='adjust' else [kind,uc.reg_read(UC_ARM_REG_R0)] if kind=='delay' else [kind])
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def on_write(uc,access,a,size,value,data):
    if a in (0x200270c0,0x200270c4,0x200270b8,0x200270bc,0x200270b0,0x200270b4,0x40020080,0x40020044,0x4002004c,0x4002037c):writes.append([hex(a),size,value])
   u.hook_add(UC_HOOK_CODE,on_code);u.hook_add(UC_HOOK_MEM_WRITE,on_write)
   for reg,val in ((UC_ARM_REG_R0,target),(UC_ARM_REG_R1,current),(UC_ARM_REG_R2,ton),(UC_ARM_REG_R3,old_ton),(UC_ARM_REG_SP,0x2002f000),(UC_ARM_REG_LR,0x50f001)):u.reg_write(reg,val)
   entry=0x428506 if native else symbols['opencfw_spot_pcm22_transition4']&~1
   u.emu_start(entry|1,0x50f000,count=50000)
   pair.append({'return':u.reg_read(UC_ARM_REG_R0),'calls':calls,'writes':writes,'registers':{hex(a):struct.unpack('<I',u.mem_read(a,4))[0] for a in (0x40020080,0x40020044,0x4002004c,0x4002037c)}})
  assert pair[0]==pair[1],(label,pair)
  cases.append({'case':label,'result':pair[0]})
 report={'status':'PASS_BOUNDED_SPOT_SELECTOR4','cases':cases,'original_sha256':LOCKED,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'data_source_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),'limits':['Synthetic MMIO; timer service, delay and TON adjust are explicit matched call cuts.','Ready and 60-delay exhaustion paths tested. No physical power timing or full callback graph proof.']}
 Path(__file__).with_name('spot-selector4-oracle.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'cases':len(cases)}))
