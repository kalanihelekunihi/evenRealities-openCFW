import verify as v
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib
rows=[]
for status in [0,1,0x20,0x21]:
 observed=[]
 for native in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x100000,0x10000)
  for a,b in v.sections:u.mem_write(a,b)
  u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x2000)
  def w(a,x):u.mem_write(a,struct.pack('<I',x))
  w(v.STATE,0x1ea9e06);w(v.STATE+0x28,1);w(0x20000d2c+28+4,v.STATE);w(0x4003a040,status);u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);done=[]
  def hook(uc,pc,size,user):
   if native and pc==0x58e534:uc.reg_write(UC_ARM_REG_PC,v.syms['nonblocking_write_sm']|1);return
   if pc==0x10ff00:done.append(True);uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x55e2cf,0,count=10000);assert done
  obs={'status':status,'interrupt_clear_word':int.from_bytes(u.mem_read(0x4003a044,4),'little'),'channel_completion':u.mem_read(0x20000d2c+28+25,1)[0],'hal_last_tx_complete':u.mem_read(v.STATE+0xde,1)[0]};assert obs['interrupt_clear_word']==status and obs['channel_completion']==bool(status&1) and obs['hal_last_tx_complete']==bool(status&1);observed.append(obs)
 assert observed[0]==observed[1];rows.append(observed[0])
(v.D/'irq-composition-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(v.elf.read_bytes()).hexdigest(),'comparisons':rows,'limits':'Manually entered original channel1 interrupt wrapper with injected status register; stock status/clear/service providers, original or native inactive-TX state machine. No exception/vector delivery, RX or DMA path, actual interrupt timing or physical TX.'},indent=2)+'\n');print('PASS',len(rows))
