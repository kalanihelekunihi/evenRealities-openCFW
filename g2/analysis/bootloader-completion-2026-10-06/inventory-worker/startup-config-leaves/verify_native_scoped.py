"""Actual copy helper with MMIO-scoped recorder, no copy-answer stub."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5];s=importlib.util.spec_from_file_location('elfread',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(s);s.loader.exec_module(elf)
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();_,segments,symbols=elf.elf_info(args.elf);blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
class M:
 def __init__(self,source):
  self.source=source;self.cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);self.cpu.mem_map(0x410000,0x25000);self.cpu.mem_map(0x20000000,0x40000);self.cpu.mem_map(0x08000000,0x10000);self.cpu.mem_map(0x40050000,0x4000);self.calls=[];self.trace={};self.done=False
  if not source:self.cpu.mem_write(0x410000,blob)
  else:
   for x in segments:
    lo=x['address']&~4095;hi=(x['address']+len(x['data'])+4095)&~4095
    if not(0x410000<=lo<0x435000 or 0x20000000<=lo<0x20040000 or 0x08000000<=lo<0x08010000):self.cpu.mem_map(lo,hi-lo)
    self.cpu.mem_write(x['address'],x['data'])
  self.cpu.hook_add(UC_HOOK_CODE,self.code);self.cpu.hook_add(UC_HOOK_MEM_WRITE,lambda *x:None,begin=0x40050000,end=0x40053fff)
 def code(self,u,pc,n,z):
  if pc==0x08000000:self.done=True;u.emu_stop();return
  for cls,entry in [(4,0x4216d4),(5,0x4217d2),(6,0x421978)]:
   target=(symbols['opencfw_boot_startup_select'+str(cls)]&~1) if self.source else entry
   if pc==target:self.calls.append([cls,u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)]);u.reg_write(a.UC_ARM_REG_R0,0xa0000000|cls);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if not self.source:self.trace[pc]=bytes(u.mem_read(pc,n)).hex()
rows=[];trace={}
for name,entry,vals in [('opencfw_boot_startup_clock_descriptor',0x422416,[ptr,0,0]) for ptr in [0]+list(range(0x20001000,0x20001008))]+[('opencfw_boot_startup_clock_select',0x4222a0,[i,0x12345678,0xabcdef01]) for i in list(range(260))+[0xffffff04,0xffffffff]]:
 obs=[]
 for source in [False,True]:
  m=M(source);u=m.cpu;u.mem_write(0x20001000,bytes(range(64)));u.mem_write(0x20000070,bytes([0xa5])*64);u.reg_write(a.UC_ARM_REG_XPSR,0x01000000);u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001)
  for r,val in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2],vals):u.reg_write(r,val)
  u.emu_start((symbols[name]&~1 if source else entry)|1,0x08000002,count=10000);assert m.done;obs.append({'return':u.reg_read(a.UC_ARM_REG_R0),'region':bytes(u.mem_read(0x20000070,64)).hex(),'calls':m.calls});trace.update(m.trace)
 assert obs[0]==obs[1],(name,vals,obs);rows.append({'function':name,'args':vals,'result':obs[0]})
r={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in trace.items()},'limits':['Original copy41568c executes, recorder scoped to MMIO; no copy expected-answer stub. All8 source alignments and destination guards compare.','Dispatcher children remain injected for wrapper unit coverage; actual children have separate5896-case proof with documented lower generator/request models.','Synthetic coherent memory/M33, not hardware/drain/atomic-publication or source/byte equality.']};args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows))
