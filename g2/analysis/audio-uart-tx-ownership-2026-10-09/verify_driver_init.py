import verify as v
import verify_initializer as init
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib
rows=[]
for native in [False,True]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x100000,0x10000)
 for a,b in v.sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(0x20000000,bytes(init.out));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);calls=[];done=[]
 def hook(uc,pc,size,user):
  if pc in (0x58dae4,0x58ddd6):
   args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if pc==0x58ddd6:args.append(int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little'))
   calls.append({'provider':hex(pc),'args':args[:2] if pc==0x58dae4 else args})
   if native:uc.reg_write(UC_ARM_REG_PC,v.syms['am_hal_uart_initialize' if pc==0x58dae4 else 'am_hal_uart_buffer_configure']|1);return
  if pc in (0x58dbb8,0x58e09e,0x480f0c,0x55e288,0x55e2a6,0x55e244,0x58e782):
   obs={'stub':hex(pc),'r0':uc.reg_read(UC_ARM_REG_R0)}
   if pc not in (0x55e288,0x55e244):obs['r1']=uc.reg_read(UC_ARM_REG_R1)
   calls.append(obs)
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10ff00:done.append(True);uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x55e389,0,count=10000);assert done
 descriptors=bytes(u.mem_read(0x20000d2c,4*28));states=bytes(u.mem_read(0x2006a02c,4*284));obs={'return':u.reg_read(UC_ARM_REG_R0),'calls':calls,'descriptors_hex':descriptors.hex(),'uart_states_hex':states.hex()}
 for ch in [1,2,3]:
  assert descriptors[ch*28+24]==0
  assert int.from_bytes(descriptors[ch*28+4:ch*28+8],'little')==0x2006a02c+ch*284
  if ch==1:assert states[ch*284+220:ch*284+222]==bytes(2)
 assert [c['args'][0] for c in calls if c.get('provider')=='0x58dae4']==[1,2,3]
 assert [c for c in calls if c.get('provider')=='0x58ddd6'][0]['args'][1:]==[0,0,0,0]
 rows.append(obs)
assert rows[0]==rows[1],{k:(rows[0][k],rows[1][k]) for k in rows[0] if rows[0][k]!=rows[1][k]}
(v.D/'driver-init-results.json').write_text(json.dumps({'status':'PASS','cases':1,'elf_sha256':hashlib.sha256(v.elf.read_bytes()).hexdigest(),'initialized_sram_sha256':init.result['decoded_sha256'],'comparison':rows[0],'limits':'Actual initialized SRAM record and original channel initialization wrapper with original/native HAL initialize and buffer configure. GPIO, power, configure, NVIC and IRQ enable are explicit success stubs. Confirms structural/default state, not physical initialization, achieved baud or activation success.'},indent=2)+'\n');print('PASS driver init composition')
