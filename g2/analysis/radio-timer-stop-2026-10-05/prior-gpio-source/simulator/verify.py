#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Unified GPIO config/state/radio board chain; actual PRIMASK and MMIO order."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
BASE=0x438000;GPIO=0x40010000;OUT=0x20001000;STOP=0x8000000
FUN={'state':(0x480fd6,218,'opencfw_gpio_state_write_raw','e768e90540355f1c1e9fcd7477765c5bacf0c91e8b2fc3daa6d4794cbd0fc9ef'),'board':(0x52dd7c,24,'opencfw_radio_gpio_idle_pins','305a68c45e61102444d5ccab1fad6ed41903a05985e2323223acc1c92c92f9bc'),'get':(0x480eee,30,'am_hal_gpio_pinconfig_get','f76f64c0dd07b5e162bd23d4cdc87a1e70735b0db5b61da9fa1c3dd7f6ec942e'),'set':(0x480f0c,126,'am_hal_gpio_pinconfig','a43394486c7d8da946cf692d6f33ddf66f1ebe63683d3a3fd408afb0fdf5e9e2')}
EXT=[0,0x3fe0,0x3ff,0x1ffbfe00,0x7c000,0,0]
DRIVE=[0x8fc007e6,0xe3f3ffff,0x81ffffff,0xffffffff,0xf00fc07f,1,0x189]
sha=lambda b:hashlib.sha256(b).hexdigest()
w=lambda n:struct.pack('<I',n&0xffffffff)
FAMILIES={'RD':0x404,'WT':0x420,'EN':0x474,'WTS':0x43c,'WTC':0x458,'ENS':0x490,'ENC':0x4ac}
def initial_registers(c=None):
 c=c or {};regs=bytearray(b''.join(w(0xabaddeff^(i*0x01010101)) for i in range(224))+b'\xa5'*(0x4cc-224*4))
 for family,offset in FAMILIES.items():
  for bank in range(7):struct.pack_into('<I',regs,offset+4*bank,c.get(family.lower(),0xa5a5a5a5))
 return bytes(regs)
def register_role(address):
 offset=address-GPIO
 return next(((name,(offset-start)//4) for name,start in FAMILIES.items() if start<=offset<start+28 and (offset-start)%4==0),None)
def device_effect(regs,address,value,c):
 """Explicit synthetic device fixture. Output-active condition is external input.

 Register addresses determine side effects, including bank7 aliases. Write-only
 command cells remain synthetic latches; their readback is not a hardware claim.
 """
 if c.get('model','raw')!='side_effects':return None
 role=register_role(address)
 if not role:return None
 family,bank=role
 if family not in ['WTS','WTC','ENS','ENC']:return None
 target=FAMILIES['WT' if family in ['WTS','WTC'] else 'EN']+4*bank
 old=struct.unpack_from('<I',regs,target)[0]
 effective=value&c.get('output_active_mask',0xffffffff) if family in ['WTS','WTC'] else value
 new=(old|effective) if family in ['WTS','ENS'] else (old&~effective)&0xffffffff
 struct.pack_into('<I',regs,target,new)
 return target,new

def expected(c):
 regs=bytearray(initial_registers(c));output=0xabadcafe;io=[];writes=[];calls=[];status=0
 def put(address,value,mask):
  io.append(['write',address,value,mask]);device_effect(regs,address,value,c);struct.pack_into('<I',regs,address-GPIO,value)
 def get(address,mask):
  value=struct.unpack_from('<I',regs,address-GPIO)[0];io.append(['read',address,value,mask]);return value
 def config(pin,value):
  calls.append(['config',pin,value,c['prior']])
  if pin>=224:return 5
  bank=pin//32;bit=1<<(pin&31);pull=value>>13&7;drive=value>>10&3
  if (EXT[bank]&bit and pull not in [0,1,6]) or (not EXT[bank]&bit and drive>=2 and not DRIVE[bank]&bit):return 7
  put(GPIO+0x400,0x73,1);put(GPIO+4*pin,value,1);put(GPIO+0x400,0,1)
  return 0
 def state(pin,operation):
  operation&=255;calls.append(['state',pin,operation,c['prior']])
  if operation>5:return 0
  bank=(pin>>5)&7;bit=1<<(pin&31);family=['WTC','WTS','WT','ENC','ENS','EN'][operation];a=GPIO+FAMILIES[family]+4*bank
  if operation in [2,5]:put(a,get(a,1)^bit,1)
  else:put(a,bit,c['prior'])
  return 0
 if c['op']=='get':
  calls.append(['get',c['pin'],0 if c['null'] else OUT,c['prior']])
  if c['pin']>=224:status=5
  elif c['null']:status=6
  else:output=get(GPIO+4*c['pin'],c['prior']);writes=[output]
 elif c['op']=='set':status=config(c['pin'],c['config'])
 elif c['op']=='state':status=state(c['pin'],c['operation'])
 else:
  state(93,0);config(138,c['board_config']);status=None # void stock helper; no defined R0 result
 return dict(status=status,output=output,output_writes=writes,mmio=io,registers=bytes(regs).hex(),primask=c['prior'],calls=calls)

def run(segments,entry,c,entries=None,board_word=None):
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
 cpu.mem_write(GPIO,initial_registers(c));cpu.mem_write(OUT-8,b'\xcc'*8+w(0xabadcafe)+b'\xcc'*8)
 if c['op']=='board':
  assert board_word is not None;cpu.mem_write(board_word,w(c['board_config'])) # explicitly synthetic failure/data perturbation
 trace={};mmio=[];writes=[];calls=[];entries=entries or {'get':0x480eee,'set':0x480f0c,'state':0x480fd6}
 def code(uc,pc,size,_):
  if pc in entries.values():
   operation=next(name for name,a in entries.items() if a==pc)
   a=uc.reg_read(arm.UC_ARM_REG_R0);b=uc.reg_read(arm.UC_ARM_REG_R1)
   calls.append([{'get':'get','set':'config','state':'state'}[operation],a,b&255 if operation=='state' else b,uc.reg_read(arm.UC_ARM_REG_PRIMASK)])
  s=next(s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data']))
  raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  assert size==4 and a%4==0
  if GPIO<=a<GPIO+0x4cc:
   read=access==u.UC_MEM_READ;v=struct.unpack('<I',uc.mem_read(a,4))[0] if read else value
   assert a<GPIO+224*4 or a==GPIO+0x400 or GPIO+0x404<=a<GPIO+0x4cc
   prior=uc.reg_read(arm.UC_ARM_REG_PRIMASK);mmio.append(['read' if read else 'write',a,v,prior])
   if not read:
    if a<GPIO+224*4 or a==GPIO+0x400:
     assert prior==1
     if a<GPIO+224*4:assert struct.unpack('<I',uc.mem_read(GPIO+0x400,4))[0]==0x73
    # Host-side register fixture effects never replace guest instructions.
    regs=bytearray(uc.mem_read(GPIO,0x4cc));effect=device_effect(regs,a,value,c)
    if effect:offset,changed=effect;uc.mem_write(GPIO+offset,w(changed))
  else:
   assert access==u.UC_MEM_WRITE and a==OUT;writes.append(value)
 cpu.hook_add(u.UC_HOOK_CODE,code)
 cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem,begin=GPIO,end=GPIO+0x4cb)
 cpu.hook_add(u.UC_HOOK_MEM_WRITE,mem,begin=OUT-8,end=OUT+11)
 arg=0 if c['null'] else OUT
 if c['op']=='set':arg=c['config']
 elif c['op']=='state':arg=c['operation']
 cpu.reg_write(arm.UC_ARM_REG_R0,c['pin']);cpu.reg_write(arm.UC_ARM_REG_R1,arg)
 cpu.reg_write(arm.UC_ARM_REG_SP,0x2000f000);cpu.reg_write(arm.UC_ARM_REG_LR,STOP|1);cpu.reg_write(arm.UC_ARM_REG_PRIMASK,c['prior'])
 saved={getattr(arm,'UC_ARM_REG_R'+str(i)):0xa6000000+i for i in range(4,12)}
 for reg,value in saved.items():cpu.reg_write(reg,value)
 cpu.emu_start(entry|1,STOP,count=1000)
 assert cpu.reg_read(arm.UC_ARM_REG_PC)==STOP and cpu.reg_read(arm.UC_ARM_REG_SP)==0x2000f000
 assert all(cpu.reg_read(reg)==value for reg,value in saved.items())
 assert bytes(cpu.mem_read(OUT-8,8))==bytes(cpu.mem_read(OUT+4,8))==b'\xcc'*8
 return dict(status=None if c['op']=='board' else cpu.reg_read(arm.UC_ARM_REG_R0),output=struct.unpack('<I',cpu.mem_read(OUT,4))[0],output_writes=writes,mmio=mmio,registers=bytes(cpu.mem_read(GPIO,0x4cc)).hex(),primask=cpu.reg_read(arm.UC_ARM_REG_PRIMASK),calls=calls,trace=trace)
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
def board_cases():
 default=dict(pin=0,prior=0,null=False,config=0,operation=0,board_config=3,wt=0xa5a55a5a,en=0x5a5aa5a5,output_active_mask=0xffffffff)
 for pin in range(224):
  for operation in range(6):
   for prior in [0,1]:
    for model in ['raw','side_effects']:yield dict(default,op='state',pin=pin,operation=operation,prior=prior,model=model)
 boundaries=[0,31,32,63,64,93,103,127,128,138,142,143,191,192,223]
 for pin in boundaries:
  for operation in range(6):
   for prior in [0,1]:
    for pattern in [0,0xffffffff,0x80000001]:
     for active in [0,0xffffffff]:yield dict(default,op='state',pin=pin,operation=operation,prior=prior,model='side_effects',wt=pattern,en=pattern,output_active_mask=active)
 # Unknown operation bytes are success/no-op; high bits are truncated by stock.
 for pin in [0,93,223,224,255,256,257,0x10000,0xffffffff]:
  for operation in [0,1,2,3,4,5,6,7,255,256,257,261,262,0xffffffff]:
   for prior in [0,1]:yield dict(default,op='state',pin=pin,operation=operation,prior=prior,model='raw',diagnostic='masked-bank/byte ABI; not valid physical pin evidence')
 # Only3 is the authenticated board constant. Other words are injected tests.
 for value in [3,0x183,0x800,0xffffffff]:
  for prior in [0,1]:
   for model in ['raw','side_effects']:
    for pattern in [0,0xffffffff,0xa5a55a5a]:
     for active in [0,0xffffffff]:yield dict(default,op='board',board_config=value,prior=prior,model=model,wt=pattern,en=pattern,output_active_mask=active,diagnostic='stock constant' if value==3 else 'synthetic board-config perturbation')
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
 for pc,n,_,h in FUN.values():assert sha(blob[32+pc-BASE:32+pc-BASE+n])==h
 for addr,values in [(0x768ba8,EXT),(0x768bc4,DRIVE)]:assert blob[32+addr-BASE:32+addr-BASE+28]==b''.join(w(v) for v in values)
 elf,segs,syms=parser.elf_info(a.elf);stock=[dict(address=address,data=blob[32+address-BASE:32+address-BASE+4096],memory_size=4096,flags=4 if address in [0x768000,0x52e000,0x78e000] else 5) for address in [0x480000,0x481000,0x473000,0x768000,0x52d000,0x52e000,0x78e000]]
 for name,values in [('g_ui32CfgDSExt',EXT),('g_ui32DSpintbl',DRIVE)]:
  addr=syms[name];s=next(s for s in segs if s['address']<=addr and addr+28<=s['address']+len(s['data']));assert s['data'][addr-s['address']:addr-s['address']+28]==b''.join(w(v) for v in values)
 results=[];observed={}
 for c in list(cases())+list(board_cases()):
  pc,n,name,h=FUN[c['op']];x=run(stock,pc,c,board_word=0x78ee48);y=run(segs,syms[name]&~1,c,entries={'get':syms['am_hal_gpio_pinconfig_get']&~1,'set':syms['am_hal_gpio_pinconfig']&~1,'state':syms['am_hal_gpio_state_write']&~1},board_word=syms['opencfw_radio_pin138_idle_config']);trace=x.pop('trace');y.pop('trace');assert x==y,(c,x,y);assert x==expected(c),(c,x,expected(c));observed.update(trace)
  results.append(dict(inputs=c,result=x,original_trace=trace))
 for pc,n,_,_ in FUN.values():assert all(any(a<=b<a+len(bytes.fromhex(v)) for a,v in observed.items()) for b in range(pc,pc+n)),hex(pc)
 comp=Path(__file__).resolve().parents[1]
 report=dict(status='PASS',cases=len(results),results=results,original_trace={hex(a):v for a,v in sorted(observed.items())},unique_original_trace_bytes=sum(len(bytes.fromhex(v)) for v in observed.values()),new_function_body_bytes=242,prior_config_function_bytes=156,shared_critical_bytes=8,elf_sha256=sha(elf),firmware_sha256=sha(blob),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},limits='Unified config/state/radio helper source; actual PRIMASK and original/source instructions, no call stubs. Ordered MMIO/masks/fullregister state retained. W1 command effects and external output-active mask are synthetic fixtures; physical enable derivation, pin readiness, clock/NVIC/fullshutdown and hardware are unproven. Bank7 addresses/operation truncation are diagnostics, not valid pins. Board words other than3 are injected perturbations; voidR0 unspecified. Optimized tick remains blocked.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),'stock/source/model cases;',report['unique_original_trace_bytes'],'original bytes;242 new function bytes')
if __name__=='__main__':main()
