import verify as v
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib
STAGING=0x200b9c20;SBHANDLE=0x200748bc
rows=[]
for count in [0,3,15,16,32,205]:
 for head in [0,2046,2048]:
  observations=[]
  for native in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x100000,0x10000)
   for a,b in v.sections:u.mem_write(a,b)
   u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x2000)
   def w(a,x):u.mem_write(a,struct.pack('<I',x))
   u.mem_write(v.DATA,b'\xa5'*2049);u.mem_write(v.SB,struct.pack('<7I',0,head,2049,1,0,0,v.DATA)+bytes(8));w(SBHANDLE,v.SB);w(v.UART+40,1);w(0x20000d2c+28+4,v.UART);w(0x20000d2c+28+16,0x20000cfc);w(0x20000d2c+28+20,0x5415e7);w(0x20000cfc+12,STAGING);u.mem_write(STAGING,b'\xa5'*512)
   payload=bytes((i*17+3)&255 for i in range(count));rx=iter(payload);current=[None];reads=[];done=[];stream_returns=[];after_stream=[False]
   def readhook(uc,access,a,size,value,user):
    if a==0x4003a018:
     if current[0] is None:current[0]=next(rx,None)
     w(a,0x10 if current[0] is None else 0)
    elif a==0x4003a000:
     x=current[0];w(a,0 if x is None else x);reads.append(x);current[0]=None
   def hook(uc,pc,size,user):
    if pc==0x57e05e and native:uc.reg_write(UC_ARM_REG_PC,v.syms['xStreamBufferSendFromISR']|1);return
    if pc==0x58e2d8 and native:uc.reg_write(UC_ARM_REG_PC,v.syms['am_hal_uart_fifo_read']|1);return
    if pc==0x5415fe:stream_returns.append(uc.reg_read(UC_ARM_REG_R0))
    if pc==0x10ff00:done.append(True);uc.emu_stop();return
    if native:assert 0x100000<=pc<0x102000 or 0x55e4ec<=pc<0x55e5bc or 0x5415e6<=pc<0x541600,hex(pc)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,readhook)
   def invoke(n,flush):
    done.clear();u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_R2,flush);u.reg_write(UC_ARM_REG_PC,0x55e4ed);steps=0
    while not done:u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1);steps+=1;assert steps<200000
   remaining=count
   while remaining>16:invoke(15,0);remaining-=15
   invoke(16,1)
   accepted=min(count,2048-head);newhead=(head+accepted)%2049
   assert int.from_bytes(u.mem_read(v.SB+4,4),'little')==newhead
   assert int.from_bytes(u.mem_read(0x20000cfc+8,4),'little')==0
   data=bytes(u.mem_read(v.DATA,2049));assert data[head:head+accepted]==payload[:accepted]
   # After callback, immediately reuse staging; stream storage must remain independent.
   u.mem_write(STAGING,b'Z'*max(count,1));assert bytes(u.mem_read(v.DATA,2049))==data
   observations.append({'input_bytes':count,'initial_head':head,'accepted_bytes':accepted,'discarded_suffix':count-accepted,'new_head':newhead,'staging_count_after':0,'send_returns_before_callback_discards':stream_returns,'fifo_reads':len(reads),'stream_sha256':hashlib.sha256(data).hexdigest(),'staging_reuse_preserves_stream':True})
  assert observations[0]==observations[1];rows.append(observations[0])
(v.D/'rx-composition-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(v.elf.read_bytes()).hexdigest(),'comparisons':rows,'limits':'Original channel1 accumulate/flush and callback plus original/native FIFO-read/stream-send. Synthetic RX byte/status sequence; actual caller ignores accepted-byte count and resets staging count. No physical overruns, live stream pressure, IRQ delivery or scheduling claim.'},indent=2)+'\n');print('PASS',len(rows))
