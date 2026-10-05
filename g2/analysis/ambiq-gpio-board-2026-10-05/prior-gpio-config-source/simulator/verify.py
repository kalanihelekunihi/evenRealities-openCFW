#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bounded stock/source GPIO pad configuration; actual PRIMASK and MMIO ordering."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
BASE=0x438000;GPIO=0x40010000;OUT=0x20001000;STOP=0x8000000
FUN={'get':(0x480eee,30,'am_hal_gpio_pinconfig_get','f76f64c0dd07b5e162bd23d4cdc87a1e70735b0db5b61da9fa1c3dd7f6ec942e'),'set':(0x480f0c,126,'am_hal_gpio_pinconfig','a43394486c7d8da946cf692d6f33ddf66f1ebe63683d3a3fd408afb0fdf5e9e2')}
EXT=[0,0x3fe0,0x3ff,0x1ffbfe00,0x7c000,0,0]
DRIVE=[0x8fc007e6,0xe3f3ffff,0x81ffffff,0xffffffff,0xf00fc07f,1,0x189]
sha=lambda b:hashlib.sha256(b).hexdigest()
w=lambda n:struct.pack('<I',n&0xffffffff)
def initial_registers():return b''.join(w(0xabaddeff^(i*0x01010101)) for i in range(224))+b'\xa5'*(0x404-224*4)
def expected(c):
 pin=c['pin'];status=0
 if pin>=224:status=5
 elif c['op']=='get' and c['null']:status=6
 elif c['op']=='set':
  drive=(c['config']>>10)&3;pull=(c['config']>>13)&7;mask=1<<(pin&31)
  if EXT[pin//32]&mask:
   if pull not in [0,1,6]:status=7
  elif drive>1 and not DRIVE[pin//32]&mask:status=7
 regs=bytearray(initial_registers());output=0xabadcafe;io=[];writes=[]
 if not status:
  if c['op']=='get':
   output=struct.unpack_from('<I',regs,pin*4)[0];io=[['read',GPIO+pin*4,output,c['prior']]];writes=[output]
  else:
   io=[['write',GPIO+0x400,0x73,1],['write',GPIO+pin*4,c['config'],1],['write',GPIO+0x400,0,1]]
   struct.pack_into('<I',regs,pin*4,c['config']);struct.pack_into('<I',regs,0x400,0)
 return dict(status=status,output=output,output_writes=writes,mmio=io,registers=bytes(regs).hex(),primask=c['prior'])
def run(segments,entry,c):
 import unicorn as u
 import unicorn.arm_const as arm
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);cpu.ctl_set_cpu_model(arm.UC_CPU_ARM_CORTEX_M4);pages=set()
 for s in segments:
  for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
  cpu.mem_write(s['address'],s['data'])
 for lo,n in [(0x20000000,0x10000),(GPIO,4096),(STOP,4096)]:
  for p in range(lo,lo+n,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
 cpu.mem_write(GPIO,initial_registers());cpu.mem_write(OUT-8,b'\xcc'*8+w(0xabadcafe)+b'\xcc'*8)
 trace={};mmio=[];writes=[]
 def code(uc,pc,size,_):
  s=next(s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data']))
  raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  assert size==4 and a%4==0
  if GPIO<=a<=GPIO+0x400:
   read=access==u.UC_MEM_READ;v=struct.unpack('<I',uc.mem_read(a,4))[0] if read else value
   assert a<GPIO+224*4 or a==GPIO+0x400
   mmio.append(['read' if read else 'write',a,v,uc.reg_read(arm.UC_ARM_REG_PRIMASK)])
   if not read:assert uc.reg_read(arm.UC_ARM_REG_PRIMASK)==1
  else:
   assert access==u.UC_MEM_WRITE and a==OUT;writes.append(value)
 cpu.hook_add(u.UC_HOOK_CODE,code)
 cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem,begin=GPIO,end=GPIO+0x403)
 cpu.hook_add(u.UC_HOOK_MEM_WRITE,mem,begin=OUT-8,end=OUT+11)
 cpu.reg_write(arm.UC_ARM_REG_R0,c['pin']);cpu.reg_write(arm.UC_ARM_REG_R1,(0 if c['null'] else OUT) if c['op']=='get' else c['config'])
 cpu.reg_write(arm.UC_ARM_REG_SP,0x2000f000);cpu.reg_write(arm.UC_ARM_REG_LR,STOP|1);cpu.reg_write(arm.UC_ARM_REG_PRIMASK,c['prior'])
 saved={getattr(arm,'UC_ARM_REG_R'+str(i)):0xa6000000+i for i in range(4,12)}
 for reg,value in saved.items():cpu.reg_write(reg,value)
 cpu.emu_start(entry|1,STOP,count=1000)
 assert cpu.reg_read(arm.UC_ARM_REG_PC)==STOP and cpu.reg_read(arm.UC_ARM_REG_SP)==0x2000f000
 assert all(cpu.reg_read(reg)==value for reg,value in saved.items())
 assert bytes(cpu.mem_read(OUT-8,8))==bytes(cpu.mem_read(OUT+4,8))==b'\xcc'*8
 return dict(status=cpu.reg_read(arm.UC_ARM_REG_R0),output=struct.unpack('<I',cpu.mem_read(OUT,4))[0],output_writes=writes,mmio=mmio,registers=bytes(cpu.mem_read(GPIO,0x404)).hex(),primask=cpu.reg_read(arm.UC_ARM_REG_PRIMASK),trace=trace)
def cases():
 raw=0xb5400389
 for pin in list(range(224))+[224,225,255,0xffffffff]:
  for prior in [0,1]:
   for null in [False,True]:yield dict(op='get',pin=pin,prior=prior,null=null,config=0)
   for drive in range(8):yield dict(op='set',pin=pin,prior=prior,null=False,config=raw|(drive<<10))
   for pull in range(1,8):yield dict(op='set',pin=pin,prior=prior,null=False,config=raw|(pull<<13))
 # Cross-product covering capability classes, sparse bitmap holes, and logical boundaries.
 for pin in [0,1,37,64,74,105,106,117,138,142,208,223]:
  for prior in [0,1]:
   for drive in range(8):
    for pull in range(8):yield dict(op='set',pin=pin,prior=prior,null=False,config=raw|(drive<<10)|(pull<<13))
 for pin,value in [(138,3),(143,0x183),(128,0x183),(142,0x183)]:
  for prior in [0,1]:yield dict(op='set',pin=pin,prior=prior,null=False,config=value,consumer_reference='authenticated radio/display constant')
 for value in [0,0xffffffff,0x0c001000,0x0c001002]:
  for prior in [0,1]:yield dict(op='set',pin=138,prior=prior,null=False,config=value)
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
 for pc,n,_,h in FUN.values():assert sha(blob[32+pc-BASE:32+pc-BASE+n])==h
 for addr,values in [(0x768ba8,EXT),(0x768bc4,DRIVE)]:assert blob[32+addr-BASE:32+addr-BASE+28]==b''.join(w(v) for v in values)
 elf,segs,syms=parser.elf_info(a.elf);stock=[dict(address=address,data=blob[32+address-BASE:32+address-BASE+4096],memory_size=4096,flags=4 if address==0x768000 else 5) for address in [0x480000,0x481000,0x473000,0x768000]]
 for name,values in [('g_ui32CfgDSExt',EXT),('g_ui32DSpintbl',DRIVE)]:
  addr=syms[name];s=next(s for s in segs if s['address']<=addr and addr+28<=s['address']+len(s['data']));assert s['data'][addr-s['address']:addr-s['address']+28]==b''.join(w(v) for v in values)
 results=[];observed={}
 for c in cases():
  pc,n,name,h=FUN[c['op']];x=run(stock,pc,c);y=run(segs,syms[name]&~1,c);trace=x.pop('trace');y.pop('trace');assert x==y,(c,x,y);assert x==expected(c),(c,x,expected(c));observed.update(trace)
  results.append(dict(inputs=c,result=x,original_trace=trace))
 for pc,n,_,_ in FUN.values():assert all(any(a<=b<a+len(bytes.fromhex(v)) for a,v in observed.items()) for b in range(pc,pc+n)),hex(pc)
 comp=Path(__file__).resolve().parents[1]
 report=dict(status='PASS',cases=len(results),results=results,original_trace={hex(a):v for a,v in sorted(observed.items())},unique_original_trace_bytes=sum(len(bytes.fromhex(v)) for v in observed.values()),new_function_body_bytes=156,shared_critical_bytes=8,elf_sha256=sha(elf),firmware_sha256=sha(blob),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},limits='Independent source module and raw MMIO model only; actual PRIMASK helper, no call stubs. Ordered MMIO access and all224logical GPIO/configuration words checked. No physical pad/pinmux capability, clock/NVIC/init/electrical/board sequencing or complete firmware claim. Full optimized tick remains blocked separately.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),'stock/source/model cases;',report['unique_original_trace_bytes'],'original bytes;156 new function bytes')
if __name__=='__main__':main()
