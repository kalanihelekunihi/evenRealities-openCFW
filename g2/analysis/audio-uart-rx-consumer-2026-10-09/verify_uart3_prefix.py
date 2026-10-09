import verify as v
from unicorn import *
from unicorn.arm_const import *
import struct,json
rows=[]
for mode,n in [('initializer',0),('receive',0),('receive',15),('receive',205)]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x100001);stop=[]
 def hook(uc,pc,size,user):
  if pc==0x55e5bc:stop.append('before-UART3-wake');uc.emu_stop();return
  if pc==0x100000:stop.append('return');uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 if mode=='initializer':u.reg_write(UC_ARM_REG_PC,0x58fb53)
 else:
  u.mem_write(0x20073ed4,struct.pack('<4I',0x200731b0,63,0,0));u.mem_write(0x20042000,bytes((i*13+5)&255 for i in range(n)));u.reg_write(UC_ARM_REG_R0,0x20042000);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_PC,0x58fb1d)
 for _ in range(20000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop
 ring=list(struct.unpack('<4I',u.mem_read(0x20073ed4,16)));storage=bytes(u.mem_read(0x200731b0,64));kept=bytes(storage[(ring[2]+i)&ring[1]] for i in range((ring[3]-ring[2])&ring[1]))
 if mode=='initializer':assert ring==[0x200731b0,63,0,0] and int.from_bytes(u.mem_read(0x20000d94,4),'little')==0x58fb1d and u.reg_read(UC_ARM_REG_R0)==3
 else:assert kept==bytes((i*13+5)&255 for i in range(n))[-63:] if n else kept==b''
 rows.append({'mode':mode,'bytes':n,'stop':stop,'ring_words':list(map(hex,ring)),'retained_bytes':kept.hex(),'capacity':63})
(v.D/'uart3-prefix-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'rows':rows,'limits':'Unchanged UART3 init/callback/ring instructions; synthetic initial SRAM and input bytes. Stops before channel wake; no actual IRQ/arrival rate or hardware loss.'},indent=2)+'\n');print('UART3 PREFIX PASS',len(rows))
