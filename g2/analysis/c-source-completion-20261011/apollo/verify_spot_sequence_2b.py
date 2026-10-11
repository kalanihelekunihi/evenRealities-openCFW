#!/usr/bin/env python3
"""Stock/source bounded state comparison for spot transition children."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PRIMASK
ROOT=Path(__file__).resolve().parents[4]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/source_candidate_20261010/pcm22_timer_service.c'
LOCKED='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert hashlib.sha256(STOCK.read_bytes()).hexdigest()==LOCKED
with tempfile.TemporaryDirectory(prefix='boot-spot-2b-') as td:
 d=Path(td);obj=d/'spot.o';stubs=d/'stubs.o';elfpath=d/'spot.elf'
 cc=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections']
 subprocess.run(cc+['-c',str(SOURCE),'-o',str(obj)],check=True)
 (d/'stubs.S').write_text('.syntax unified\n.thumb\n.global opencfw_hal_delay_us\n.thumb_func\nopencfw_hal_delay_us:\nbx lr\n.global opencfw_hal_status_poll\n.thumb_func\nopencfw_hal_status_poll:\nbx lr\n.global opencfw_boot_control_critical_save\n.thumb_func\nopencfw_boot_control_critical_save:\nbx lr\n.global opencfw_pcm22_spot_timer_stop\n.thumb_func\nopencfw_pcm22_spot_timer_stop:\nbx lr\n.section .note.GNU-stack,"",%progbits\n')
 subprocess.run(cc+['-c',str(d/'stubs.S'),'-o',str(stubs)],check=True)
 subprocess.run(['arm-none-eabi-ld','--gc-sections','-u','opencfw_pcm22_sequence2b','-u','opencfw_pcm22_sequence7b','-u','opencfw_pcm22_timer_service','-Ttext=0x500000',str(obj),str(stubs),'-o',str(elfpath)],check=True)
 with elfpath.open('rb') as f:
  e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
  segments=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 cases=[]
 for label,seed,kind,mode in [('2b-zero',0,'2b',0),('2b-pattern',0xa5a55a5a,'2b',0),('2b-all-set',0xffffffff,'2b',0),('7b-idle',0x55aa55aa,'7b',0),('7b-switched',0xa5a55a5a,'7b',2),('finish-2b',0x13572468,'finish2',0),('finish-7b',0x24681357,'finish7',0),('finish-other',0x96969696,'finish0',0)]:
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x410000,0x40000);u.mem_write(0x410000,STOCK.read_bytes())
   u.mem_map(0x500000,0x10000)
   if not native:
    for a,b in segments:u.mem_write(a,b)
   u.mem_map(0x20000000,0x40000);u.mem_map(0x40020000,0x2000);u.mem_map(0x40004000,0x1000)
   initial={0x200270b0:seed&127,0x200270bc:seed&15,0x200270b8:seed&1023,0x200270b4:seed&127,
            0x40020044:seed^0x12345678,0x40020080:seed^0x88776655,0x4002037c:seed^0xffffffff,0x4002004c:seed^0x55aa55aa}
   for a,v in initial.items():u.mem_write(a,struct.pack('<I',v))
   u.mem_write(0x40021000,struct.pack('<I',mode|4))
   u.mem_write(0x40004044,struct.pack('<I',32))
   u.mem_write(0x40004030,struct.pack('<I',0))
   u.mem_write(0x2000055a,bytes([2 if kind=='finish2' else 7 if kind=='finish7' else 4 if kind=='finish0' else 0xff]))
   writes=[];delays=[];cuts=[]
   def on_write(uc,access,a,size,val,data):
    if a in (0x40020044,0x40020080,0x4002037c,0x4002004c,0x40021000,0x40004044,0x2000055a):writes.append([hex(a),size,val])
   def on_code(uc,a,size,data):
    if a in ((0x41b8ec,0x41ccd6) if native else (symbols['opencfw_boot_control_critical_save']&~1,symbols['opencfw_pcm22_spot_timer_stop']&~1)):
     cuts.append('critical' if a==(0x41b8ec if native else symbols['opencfw_boot_control_critical_save']&~1) else 'timer-stop')
     if cuts[-1]=='critical':uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PRIMASK,1)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif native and a==0x41d1c0:
     delays.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif not native and a==(symbols['opencfw_hal_delay_us']&~1):delays.append(uc.reg_read(UC_ARM_REG_R0))
   u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.hook_add(UC_HOOK_CODE,on_code)
   u.reg_write(UC_ARM_REG_SP,0x2002f000);u.reg_write(UC_ARM_REG_LR,0x50f001)
   entry=(0x428378 if kind=='2b' else 0x428a94 if kind=='7b' else 0x42a04a) if native else symbols['opencfw_pcm22_timer_service' if kind.startswith('finish') else 'opencfw_pcm22_sequence'+kind]&~1
   u.emu_start(entry|1,0x50f000,count=10000)
   state={hex(a):struct.unpack('<I',u.mem_read(a,4))[0] for a in list(initial)+[0x40021000,0x40004044,0x40004030] if a>=0x40000000}
   pair.append({'writes':writes,'delays':delays,'cuts':cuts,'state':state,'phase':u.mem_read(0x2000055a,1).hex(),'primask':u.reg_read(UC_ARM_REG_PRIMASK)})
  assert pair[0]==pair[1],(label,pair)
  cases.append({'case':label,'result':pair[0]})
 report={'status':'PASS_BOUNDED_SPOT_SEQUENCE_2B_7B_FINISH','cases':cases,'original_sha256':LOCKED,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'limits':['Synthetic MMIO, delay and caller critical/timer-stop cuts; no physical power transition or timing proof.','7b tested with already enabled 0x40004044 bit5 and ready 0x40021000 bit2; status-change wait and timeout branches remain unqualified.','Native caller ignores child R0, so comparison covers ordered writes, final state, cut order and PRIMASK.']}
 Path(__file__).with_name('spot-sequence-2b-oracle.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'cases':len(cases)}))
