#!/usr/bin/env python3
"""Bounded original public-entry trace with explicit, unimplemented helper cuts."""
from pathlib import Path
import hashlib, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_READ, UC_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile
import subprocess
ROOT=Path(__file__).resolve().parents[3]
RAW=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
HELPERS={0x58dfee:'rx_abort',0x58dd5c:'dma_abort',0x58dd8a:'get_int_err',0x58dd30:'dma_complete',0x58e618:'read_sm',0x58e534:'write_sm',0x58e352:'fifo_drain',0x58dfb2:'read_abort',0x4807a0:'delay_us'}
H=0x20040000;COUNT=0x20041000;SENTINEL=0x10ff00;CALLBACK=0x10ff10
def load_native_elf(elf):
 global symbols, sections, NATIVE_HELPERS
 elf=Path(elf)
 symbols={x.split()[2]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm','-g',str(elf)],text=True).splitlines() if len(x.split())==3}
 with elf.open('rb') as f:
  sections=[(s['sh_addr'],s.data()) for s in ELFFile(f).iter_sections() if s['sh_flags']&2 and s['sh_size']]
 NATIVE_HELPERS={symbols['uart_irq_'+name]:label for name,label in [('rx_abort','rx_abort'),('dma_abort','dma_abort'),('get_int_err','get_int_err'),('dma_complete','dma_complete'),('read_sm','read_sm'),('write_sm','write_sm'),('fifo_drain','fifo_drain'),('read_abort','read_abort'),('delay_us','delay_us')]}

def run(active,status,callback,count_pointer,primask,native=False,valid=1,raw_count=3,execute_lower=False,ies=0,rsr=0,dcr=0,execute_tx=False,writing=0,tx_len=3,queued=0,occupancy=0,execute_rx_abort=False,cr=0,fr=0,baud=115200,execute_read_abort=False,reading=0,execute_fifo_drain=False,dr_read_limit=0,dr_value=0x42,execute_read_sm=False,rx_len=3,rx_queue=0,rx_occupancy=0,rx_callback=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.mem_map(0x438000,0x360000);u.mem_write(0x438000,RAW)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x4000);u.mem_map(0x100000,0x10000)
 if native:
  for a,b in sections:u.mem_write(a,b)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 def rd(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 w(H,0x01ea9e06 if valid!=2 else 0x12340000);w(H+0x28,1);w(H+0x30,baud);u.mem_write(H+0x11b,bytes([active]));w(H+0xe4,19);w(H+0xe8,COUNT if count_pointer else 0);w(H+0xf0,CALLBACK|1 if callback else 0);w(H+0xf4,0x12345678);w(0x4003a050,raw_count);w(0x4003a03c,ies);w(0x4003a004,rsr);w(0x4003a048,dcr);w(0x4003a030,cr);w(0x4003a018,fr);w(0x4003a000,dr_value);w(COUNT,0xcccccccc)
 if execute_read_abort:
  u.mem_write(H+0x64,bytes([0xa5])*0x38);w(H+0x9c,0x12345678);u.mem_write(H+0x11a,bytes([reading]))
 if execute_tx:
  src=0x20042000;out=0x20044000;queue=0x20043000;u.mem_write(src,bytes(range(1,tx_len+1))+bytes(256-tx_len));w(out,0xcccccccc)
  u.mem_write(H+0x34,struct.pack('<6I',occupancy,0,occupancy,8,1,queue));u.mem_write(queue,bytes(range(0xa0,0xa0+8)))
  u.mem_write(H+0xa0,struct.pack('<13I',src,tx_len,out,0,0,0x12345678,*([0]*7)))
  u.mem_write(H+0xdc,bytes([queued]));u.mem_write(H+0x119,bytes([writing]))
 if execute_read_sm:
  dst=0x20045000;out=0x20046000;queue=0x20047000
  u.mem_write(dst,bytes([0xa5])*256);u.mem_write(queue,bytes(range(0x80,0x88))+bytes(8));w(out,0xcccccccc)
  u.mem_write(H+0x4c,struct.pack('<6I',rx_occupancy,0,rx_occupancy,8,1,queue))
  u.mem_write(H+0x64,struct.pack('<13I',dst,rx_len,out,0,CALLBACK|1 if rx_callback else 0,0x12345678,*([0]*7)))
  w(H+0x9c,0);u.mem_write(H+0xdd,bytes([rx_queue]));u.mem_write(H+0x11a,bytes([reading]))
 u.reg_write(UC_ARM_REG_R0,0 if valid==0 else H);u.reg_write(UC_ARM_REG_R1,status);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,SENTINEL|1);u.reg_write(UC_ARM_REG_PRIMASK,primask)
 calls=[];done=[];tx_writes=[];rx_reads=[];lastpcs=[]
 def memhook(uc,access,address,size,value,_):
  if address==0x4003a000:
   if access==UC_MEM_WRITE:tx_writes.append([size,value])
   else:
    rx_reads.append([size,rd(address)])
    if dr_read_limit and len(rx_reads)>=dr_read_limit:w(0x4003a018,rd(0x4003a018)|0x10)
 def hook(uc,pc,size,_):
  lastpcs.append(pc)
  if execute_read_abort and not native and pc==0x43c0e4:
   dest=uc.reg_read(UC_ARM_REG_R0);length=uc.reg_read(UC_ARM_REG_R1);value=uc.reg_read(UC_ARM_REG_R2)&255
   assert length<=0x100
   uc.mem_write(dest,bytes([value])*length);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  all_helpers=NATIVE_HELPERS if native else HELPERS
  if pc in all_helpers and not ((execute_lower and all_helpers[pc] in ('dma_abort','dma_complete','get_int_err')) or (execute_tx and all_helpers[pc]=='write_sm') or (execute_rx_abort and all_helpers[pc]=='rx_abort') or (execute_read_abort and all_helpers[pc]=='read_abort') or (execute_fifo_drain and all_helpers[pc]=='fifo_drain') or (execute_read_sm and all_helpers[pc]=='read_sm')):
   label=all_helpers[pc]
   args=[uc.reg_read(UC_ARM_REG_R0)]
   if label=='get_int_err':args.append(uc.reg_read(UC_ARM_REG_R1))
   calls.append([label,*args])
   if label=='get_int_err':uc.reg_write(UC_ARM_REG_R0,0x77)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==CALLBACK:
   calls.append(['callback',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)])
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==SENTINEL:done.append(True);uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,memhook);u.hook_add(UC_HOOK_MEM_READ,memhook)
 try:u.emu_start((symbols['codec_irq_service'] if native else 0x58e860)|1,SENTINEL,count=5000)
 except Exception as e:raise RuntimeError(f'{e}; last PCs {[hex(x) for x in lastpcs[-30:]]}') from e
 if not done and u.reg_read(UC_ARM_REG_PC)==SENTINEL:done.append(True)
 assert done,(active,status,calls,[hex(x) for x in lastpcs[-20:]])
 return dict(active=active,status=status,callback=callback,count_pointer=count_pointer,calls=calls,tx_writes=tx_writes,rx_reads=rx_reads,ret=u.reg_read(UC_ARM_REG_R0),count=rd(COUNT),callback_cell=rd(H+0xf0),last_tx=u.mem_read(H+0xde,1)[0],dma_busy=u.mem_read(H+0x11b,1)[0],handle_hex=bytes(u.mem_read(H,0x120)).hex(),uart_hex=bytes(u.mem_read(0x4003a000,0x100)).hex(),queue_hex=bytes(u.mem_read(0x20043000,16)).hex(),tx_out=rd(0x20044000),rx_queue_hex=bytes(u.mem_read(0x20047000,16)).hex(),rx_dst_hex=bytes(u.mem_read(0x20045000,32)).hex(),rx_out=rd(0x20046000),sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK))
if __name__=='__main__':
 rows=[]
 for active in (0,1):
  for status in (0,1,0x10,0x40,0x800,0x1000,0x1841):
   for cb in (0,1):
    for cp in (0,1):rows.append(run(active,status,cb,cp,0))
 out={'status':'PASS_ORIGINAL_ONLY_HELPER_CUTS','cases':len(rows),'official_payload_sha256':hashlib.sha256(RAW).hexdigest(),'rows':rows,'limits':['Authentic public-entry stock body executes, but six lower helper bodies are intercepted with synthetic return; this is not a source comparison or complete side-effect oracle.','No exception delivery or physical interrupt timing.']}
 (Path(__file__).with_name('uart-irq-original-helper-cut.json')).write_text(json.dumps(out,indent=2)+'\n')
 print('PASS',len(rows),'original helper-cut traces')
