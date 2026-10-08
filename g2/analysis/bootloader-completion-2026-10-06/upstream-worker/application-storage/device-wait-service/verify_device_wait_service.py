#!/usr/bin/env python3
"""Compare stock INFO-word dispatch 0x4213e6 with C plus the ROM thunk."""
import argparse, hashlib, importlib.util, json, random, struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_READ
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
COMP=ROOT/'g2/components/bootloader/application_storage'
spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
BASE,IMAGE,SHA=v.BASE,v.BLOB,v.SHA
STOP,ROM_STUB=0x08000000,0x080002a0
OUT,STACK=0x20001000,0x2003f000
WAIT_CONTROL,KERNEL_CONTROL=0x400201bc,0x40021008

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Machine:
 def __init__(self,source,segments=(),symbols=None):
  self.source,self.symbols=source,symbols or {};self.uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);self.uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  self.uc.mem_map(BASE,0x25000);self.uc.mem_map(0,0x1000);self.exec=[]
  if source:
   for s in segments:
    lo=s['address']&~4095;hi=(s['address']+s['memory_size']+4095)&~4095
    if not BASE<=lo<BASE+0x25000:self.uc.mem_map(lo,hi-lo)
    self.uc.mem_write(s['address'],s['data'])
    if s['flags']&1:self.exec.append((s['address'],s['address']+len(s['data'])))
  else:self.uc.mem_write(BASE,IMAGE.read_bytes());self.exec=[(BASE,BASE+IMAGE.stat().st_size)]
  self.uc.mem_map(0x20000000,0x40000);self.uc.mem_map(0x40020000,0x2000);self.uc.mem_map(STOP,0x10000)
  self.trace={};self.reads=[];self.calls=[];self.finished=False
  self.uc.hook_add(UC_HOOK_CODE,self.code);self.uc.hook_add(UC_HOOK_MEM_READ,self.read)
 def read(self,uc,access,address,size,value,user):
  if address in (WAIT_CONTROL,KERNEL_CONTROL):self.reads.append([address,size])
 def ret(self,result):self.uc.reg_write(a.UC_ARM_REG_R0,result&0xffffffff);self.uc.reg_write(a.UC_ARM_REG_PC,self.uc.reg_read(a.UC_ARM_REG_LR))
 def code(self,uc,pc,size,user):
  if STOP<=pc<STOP+4:self.finished=True;uc.emu_stop();return
  if (self.source and pc==ROM_STUB) or (not self.source and pc==0x48):
   address,out,word_count=[uc.reg_read(r) for r in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2)]
   self.calls.append([address,out,word_count,self.fixture['resident_status'],self.fixture['resident_result']])
   if out and word_count:
    uc.mem_write(out,struct.pack('<I',self.fixture['resident_result']))
   self.ret(self.fixture['resident_status']);return
  if self.source:assert any(lo<=pc<hi for lo,hi in self.exec),('source escaped ELF',hex(pc),self.fixture)
  else:
   assert (0x4213d8<=pc<0x421548) or (0x41d28a<=pc<0x41d292),('stock escaped function',hex(pc))
   self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
 def setup(self,selector,word_offset,word_count,control,kernel,out=OUT,resident_status=0,resident_result=0):
  self.trace.clear();self.reads.clear();self.calls.clear();self.finished=False
  self.fixture=dict(selector=selector,word_offset=word_offset,word_count=word_count,control=control,kernel=kernel,out=out,resident_status=resident_status,resident_result=resident_result)
  if out:self.uc.mem_write(out,struct.pack('<I',0xdecafbad))
  self.uc.mem_write(WAIT_CONTROL,struct.pack('<I',control));self.uc.mem_write(KERNEL_CONTROL,struct.pack('<I',kernel))
  for reg,val in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),(selector,word_offset,word_count,out)):self.uc.reg_write(reg,val)
  self.uc.reg_write(a.UC_ARM_REG_SP,STACK);self.uc.reg_write(a.UC_ARM_REG_LR,STOP|1)
 def run(self):
  start=0x4213e6 if not self.source else self.symbols['opencfw_boot_device_wait_service']&~1
  self.uc.emu_start(start|1,STOP+0x10000,count=100000)
  assert self.finished,('not returned',hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
  return dict(result=self.uc.reg_read(a.UC_ARM_REG_R0),output=struct.unpack('<I',self.uc.mem_read(OUT,4))[0],reads=self.reads,calls=self.calls)
 def run_thunk(self,r7_value):
  self.trace.clear();self.calls.clear();self.finished=False
  self.fixture=dict(resident_status=0x5a5aa5a5,resident_result=0xc001d00d)
  self.uc.mem_write(OUT,struct.pack('<I',0xdecafbad))
  for reg,val in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2),(0x42006000,OUT,7)):
   self.uc.reg_write(reg,val)
  self.uc.reg_write(a.UC_ARM_REG_R7,r7_value);self.uc.reg_write(a.UC_ARM_REG_SP,STACK)
  self.uc.reg_write(a.UC_ARM_REG_LR,STOP|1)
  start=0x41d28a if not self.source else self.symbols['opencfw_boot_info_rom_read']&~1
  self.uc.emu_start(start|1,STOP+0x10000,count=10000)
  assert self.finished,('thunk did not return',hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
  return dict(result=self.uc.reg_read(a.UC_ARM_REG_R0),sp=self.uc.reg_read(a.UC_ARM_REG_SP),
              output=struct.unpack('<I',self.uc.mem_read(OUT,4))[0],calls=self.calls)

def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 assert sha(IMAGE)==SHA
 _,segments,symbols=elf.elf_info(args.elf);rng=random.Random(0x4213e6)
 selectors=[0,1,2,3,4,5,6,0x100,0x101,0x102,0x103,0x104,0x105,0xffffffff]
 word_offsets=[0,1,0x1ff,0x200,0x244,0x2c0,0x600,0xffffffff]
 word_counts=[0,1,0x3f,0x40,0x2bf,0x2c0,0x5ff,0x600,0xffffffff]
 cases=[];trace={}
 for selector in selectors:
  for bits in [(b3<<3)|(b4<<4) for b3 in (0,1) for b4 in (0,1)]:
   for ready in (0,1):
    for word_offset in word_offsets:
     for word_count in word_counts:
      rows=[]
      # Randomize unrelated bits while pinning the three decoded controls.
      control=(rng.getrandbits(32)&~0x18)|bits
      kernel=(rng.getrandbits(32)&~(1<<27))|(ready<<27)
      status=rng.getrandbits(32);result=rng.getrandbits(32)
      for source in (False,True):
       m=Machine(source,segments,symbols);m.setup(selector,word_offset,word_count,control,kernel,OUT,status,result);rows.append(m.run());trace.update(m.trace)
      assert rows[0]==rows[1],(selector,hex(control),ready,hex(word_offset),hex(word_count),rows)
      cases.append(dict(selector=selector,control_bits=bits,bit27_gate=ready,word_offset=hex(word_offset),word_count=hex(word_count),result=rows[0]['result'],output=hex(rows[0]['output']),rom_calls=len(rows[0]['calls']),rom_arguments=rows[0]['calls']))
 # Null output is checked after both global register reads.
 null_cases=[]
 for selector in (0,1,5,6):
  rows=[]
  for source in (False,True):
   m=Machine(source,segments,symbols);m.setup(selector,0x244,1,0x18,1,out=0);rows.append(m.run())
  assert rows[0]==rows[1],(selector,rows)
  null_cases.append(dict(selector=selector,result=rows[0]['result'],reads=rows[0]['reads']))
 thunk_cases=[]
 for saved_r7 in (0x11223344,0xdeadbeef):
  rows=[]
  for source in (False,True):
   m=Machine(source,segments,symbols);rows.append(m.run_thunk(saved_r7))
  assert rows[0]==rows[1],(hex(saved_r7),rows)
  assert rows[0]['result']==saved_r7 and rows[0]['sp']==STACK
  thunk_cases.append(dict(saved_r7=hex(saved_r7),result=hex(rows[0]['result']),sp=hex(rows[0]['sp']),rom_arguments=rows[0]['calls']))
 used={int(pc,0)+i for pc,data in trace.items() for i in range(len(bytes.fromhex(data)))}
 tracked=[COMP/'device_wait_service.c',COMP/'device_wait_service.h',COMP/'info_read_rom_thunk.S',HERE/'device_wait_service.ld',HERE/'Makefile',HERE/'verify_device_wait_service.py']
 report=dict(status='PASS',cases=len(cases),null_cases=len(null_cases),thunk_cases=len(thunk_cases),distinct_original_instruction_bytes=len(used),original_sha256=SHA,source_elf_sha256=sha(args.elf),source_sha256={str(x.relative_to(ROOT)):sha(x) for x in tracked},function={'stock':'0x4213e6','source_dispatch':hex(symbols['opencfw_boot_info_read_dispatch']&~1),'compatibility_alias':hex(symbols['opencfw_boot_device_wait_service']&~1),'stock_rom_thunk':'0x41d28a..0x41d292','source_rom_thunk':hex(symbols['opencfw_boot_info_rom_read']&~1),'rom_entry':'0x48'},thunk_fixtures=thunk_cases,limits=['The selector dispatch and internal word-offset helper execute as original stock instructions for the comparison. The original ROM thunk at 0x41d28a and the source assembly thunk both execute; only ROM entry 0x48 and a source-linked stand-in at 0x080002a0 are intercepted.','The resident ROM implementation is unavailable. Its boundary is passed (INFO address, destination pointer, word count); tests control its written first word and return value. The thunk preserves stock push {r7,lr}/BL/pop {r0,pc} behavior, including discarding the ROM return value in favor of saved R7. Direct thunk fixtures verify saved R7 is returned and SP is restored.','The word at 0x400201bc, the stock bit-27 gate read at 0x40021008, destination memory, and ROM effects are synthetic. SDK evidence supports INFO-space selector names and word units, but the stock bit-27 guard is reported as a raw gate without asserting it is identical to an SDK API readiness check.','No physical OTP power state, storage timing, or complete resident-ROM copy/error behavior is established.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','cases','null_cases','distinct_original_instruction_bytes')},indent=2))
if __name__=='__main__':main()
