import verify as v
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib
allowed=[]
for line in (v.R/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines():
 d=json.loads(line)
 if d['entry'] in {'005415c2','0044a43c','0055e7fa','0048949c','0058e3f8','00491102'}:allowed.extend((int(a,16),int(b,16)+1) for a,b in d['ranges'])
allowed.append((0x4d555c,0x4d558e))
rows=[]
for n in [0,3,205]:
 for completion in [False,True]:
  observations=[]
  for native in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x100000,0x10000)
   for a,b in v.sections:u.mem_write(a,b)
   u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x2000)
   def w(a,x):u.mem_write(a,struct.pack('<I',x))
   u.mem_write(v.SRC,b'A'*n+b'\0');w(v.STATE,0x1ea9e06);w(v.STATE+0x28,1);w(0x20000d2c+28+4,v.STATE);u.mem_write(0x20000d2c+28+24,b'\1');u.reg_write(UC_ARM_REG_R0,v.SRC);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01)
   fifo=[];delays=[];stop=[];trace=[]
   def memhook(uc,access,a,size,value,user):
    if a==0x4003a000:fifo.append(value&255)
   def hook(uc,pc,size,user):
    trace.append(hex(pc));trace[:]=trace[-40:]
    if native and pc==0x58e454:uc.reg_write(UC_ARM_REG_PC,v.syms['blocking_write']|1);return
    if pc==0x4807a0:
     arg=uc.reg_read(UC_ARM_REG_R0);delays.append(arg)
     if completion and arg==10:uc.mem_write(0x20000d2c+28+25,b'\1')
     uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if pc==0x10ff00:stop.append(True);uc.emu_stop();return
    if native:assert 0x100000<=pc<0x101000 or any(a<=pc<b for a,b in allowed),hex(pc)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,memhook);u.reg_write(UC_ARM_REG_PC,0x5415c3);steps=0
   while not stop:
    u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1);steps+=1;assert steps<200000
   assert stop and fifo==[65]*n
   obs={'hal_and_wrapper_return':u.reg_read(UC_ARM_REG_R0),'source_bytes_consumed':int.from_bytes(u.mem_read(v.STATE+0xd8,4),'little'),'writing_flag':u.mem_read(v.STATE+0x119,1)[0],'completion_flag':u.mem_read(0x20000d2c+28+25,1)[0],'wrapper_delays':len(delays),'delay_arguments':sorted(set(delays)),'fifo_bytes':fifo}
   assert obs['hal_and_wrapper_return']==0 and obs['source_bytes_consumed']==n and obs['writing_flag']==0
   assert obs['wrapper_delays']==(1 if completion else 1000)
   observations.append(obs)
  assert observations[0]==observations[1]
  rows.append({'length':n,'synthetic_completion_after_first_delay':completion,'observed':observations[0]})
(v.D/'sink-composition-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(v.elf.read_bytes()).hexdigest(),'comparisons':rows,'limits':'Original logger sink/strlen/channel wrapper/HAL type dispatch plus original or native TX providers. Instruction-stepped original/native composition, including original memzero tail4D555C (continuous Unicorn IT execution was inconclusive). Synthetic always-ready UART1 FIFO, delay returns, and optional completion flag. No physical TX or actual interrupt delivery.'},indent=2)+'\n');print('PASS',len(rows))
