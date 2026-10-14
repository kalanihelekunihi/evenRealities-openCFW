#!/usr/bin/env python3
"""Bounded native/source Main MSPI FIFO and timed-poll comparison."""
import argparse,hashlib,itertools,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4];BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);args=p.parse_args()
with args.elf.open('rb') as f:
 elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']];syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
NATIVE={'read':0x4bfbbc,'write':0x4bfb72,'poll':0x480826};SOURCE={'read':syms['g2_main_mspi_fifo_read_4bfbbc'],'write':syms['g2_main_mspi_fifo_write_4bfb72'],'poll':syms['g2_main_mspi_status_poll_480826']};NATIVE_POLL=0x480826;SOURCE_POLL=SOURCE['poll'];NATIVE_DELAY=0x4807a0;SOURCE_DELAY=syms['audio_delay_us_selected'];BUF=0x20007000;PORT=0x40060000;RET=0x200ff000;SP=0x200fe000
def word(cpu,address,value):cpu.mem_write(address,int(value).to_bytes(4,'little'))
def run(kind,argv,fx,source):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob);cpu.mem_map(0x800000,0x10000)
 for addr,data in segs:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_map(PORT,0x4000);cpu.mem_write(BUF,bytes(range(32)));word(cpu,PORT+0x90,fx.get('value',0))
 for module in range(4):word(cpu,PORT+(module<<12)+0x14,0x78563412)
 cpu.reg_write(R.UC_ARM_REG_SP,SP);cpu.reg_write(R.UC_ARM_REG_LR,RET|1)
 for reg,value in zip((R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2,R.UC_ARM_REG_R3),argv):cpu.reg_write(reg,value)
 if len(argv)>4:word(cpu,SP,argv[4])
 events=[];ports=[];poll_calls=0;delay_calls=0
 def memory(m,access,address,size,value,user):ports.append([access,address,size,value if access==17 else bytes(m.mem_read(address,size)).hex()])
 def hook(m,pc,size,user):
  nonlocal poll_calls,delay_calls
  if kind!='poll' and pc==(SOURCE_POLL if source else NATIVE_POLL):
   values=[m.reg_read(r) for r in (R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2,R.UC_ARM_REG_R3)];values.append(int.from_bytes(m.mem_read(m.reg_read(R.UC_ARM_REG_SP),4),'little'));events.append(['poll',*values]);statuses=fx['statuses'];status=statuses[min(poll_calls,len(statuses)-1)];poll_calls+=1;m.reg_write(R.UC_ARM_REG_R0,status);m.reg_write(R.UC_ARM_REG_PC,m.reg_read(R.UC_ARM_REG_LR))
  elif kind=='poll' and pc==(SOURCE_DELAY if source else NATIVE_DELAY):
   delay_calls+=1;events.append(['delay',m.reg_read(R.UC_ARM_REG_R0)]);
   if fx['change_after']==delay_calls:word(m,PORT+0x90,fx['changed'])
   m.reg_write(R.UC_ARM_REG_PC,m.reg_read(R.UC_ARM_REG_LR))
  elif pc==RET:m.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,hook);cpu.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory,begin=PORT,end=PORT+0x3fff)
 cpu.emu_start((SOURCE if source else NATIVE)[kind]|1,RET+2,count=10000);assert cpu.reg_read(R.UC_ARM_REG_PC)==RET,(kind,argv,fx,source)
 return {'status':cpu.reg_read(R.UC_ARM_REG_R0),'events':events,'ports':ports,'buffer':bytes(cpu.mem_read(BUF,32)).hex(),'delay_calls':delay_calls}
fixtures=[]
for kind,module,length,statuses in itertools.product(('read','write'),(0,1,3,4,255),(0,1,2,3,4,5,7,8,9,11),((0,),(4,),(4,0),(0,4))):fixtures.append((kind,[module,BUF,length,3],{'statuses':statuses}))
for count,value,equal,change_after in itertools.product((0,1,3),(0,2),(0,1,256,257),(0,1,2,4)):fixtures.append(('poll',[count,PORT+0x90,3,2,equal],{'value':value,'change_after':change_after,'changed':2 if value==0 else 0}))
for i,(kind,argv,fx) in enumerate(fixtures):
 native=run(kind,argv,fx,False);source=run(kind,argv,fx,True);assert native==source,(i,kind,argv,fx,native,source)
report={'status':'PASS_MAIN_MSPI_LOWERS_BOUNDED_NATIVE_SOURCE','cases':len(fixtures),'stock_sha256':hashlib.sha256(blob).hexdigest(),'source_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_sha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (ROOT/'g2/components/main/mspi_status_poll_candidates_20261013/poll.c',ROOT/'g2/components/main/mspi_fifo_candidates_20261013/fifo.c')},'limits':['MMIO registers are synthetic RAM and status polls/delays are injected for FIFO cases.','No physical FIFO, elapsed time, or complete Main image is verified.']}
args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],report['cases'])
