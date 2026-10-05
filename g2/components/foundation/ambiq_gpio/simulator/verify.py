#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""ARM32 stock GPIO IRQ family; real PRIMASK, synthetic callback/W1C fixtures."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
BASE,GPIO,OUT,HANDLERS,ARGS,CB,STOP=0x438000,0x40010000,0x20001000,0x20068228,0x20068928,0x9000000,0x8000000
FUN={'status':(0x481574,126,'44ef85302249c0f2479542c1367427676b4d28807779c83655a65c17504f88e5','am_hal_gpio_interrupt_irq_status_get'),'clear':(0x4815f2,58,'e1a650a0b76b4b7d1a07f3f8f895e6c6daf2f058afe4498d97ac1b7c2c7da29c','am_hal_gpio_interrupt_irq_clear'),'register':(0x48162c,154,None,'am_hal_gpio_interrupt_register'),'service':(0x4816c6,116,'8cd8748a19317a5bbc241ec3cfd761d57060af842509910b05b8e42e3b4601b1','am_hal_gpio_interrupt_service')}
def sha(b):return hashlib.sha256(b).hexdigest()
def word(n):return struct.pack('<I',n)
def bank(irq):return irq-56 if 56<=irq<=62 else irq-125+7 if 125<=irq<=131 else None

def run(segments,entry,c):
 import unicorn as u
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);pages=set()
 for s in segments:
  for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
  cpu.mem_write(s['address'],s['data'])
 for lo,n in [(0x20000000,0x10000),(0x20068000,0x3000),(GPIO,4096),(CB,8192),(STOP,4096)]:
  for p in range(lo,lo+n,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
 cpu.mem_write(OUT-8,b'\xcc'*8+word(0xabadcafe)+b'\xcc'*8)
 for i in range(14):
  addr=GPIO+0x530+i*0x10;cpu.mem_write(addr,word(c['enable'])+word(c['status'])+word(0))
  for bit in range(32):
   slot=i*32+bit;ptr=CB+slot*16|1;cpu.mem_write(ptr&~1,b'\x70\x47')
   cpu.mem_write(HANDLERS+slot*4,word(0 if c['missing']>>bit&1 else ptr));cpu.mem_write(ARGS+slot*4,word(0xa5000000|i<<8|bit))
 initial_tables=bytes(cpu.mem_read(HANDLERS,0xe00));mmio=[];calls=[];output_writes=[];trace={};critical_reads=[]
 def code(uc,address,size,_):
  if CB<=address<CB+8192:
   assert address%16==0 and size==2
   slot=(address-CB)//16;arg=uc.reg_read(UC_ARM_REG_R0);calls.append([slot,arg,uc.reg_read(UC_ARM_REG_PRIMASK)])
   if c['mutate'] and slot%32==0:
    uc.mem_write(HANDLERS+(slot+31)*4,word(0));uc.mem_write(ARGS+(slot+31)*4,word(0xbabecafe))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  matches=[s for s in segments if s['flags']&1 and s['address']<=address<address+size<=s['address']+len(s['data'])];assert len(matches)==1,hex(address)
  s=matches[0];raw=bytes(uc.mem_read(address,size));assert raw==s['data'][address-s['address']:address-s['address']+size];trace[address]=raw.hex()
 def mem(uc,access,address,size,value,_):
  if GPIO<=address<GPIO+4096:
   assert size==4 and 0x530<=address-GPIO<0x610
   v=struct.unpack('<I',uc.mem_read(address,4))[0] if access==u.UC_MEM_READ else value
   mmio.append(['read' if access==u.UC_MEM_READ else 'write',address,v])
   if access==u.UC_MEM_READ:
    critical_reads.append(uc.reg_read(UC_ARM_REG_PRIMASK));assert critical_reads[-1]==1
   else:
    assert (address-GPIO-0x530)%16==8
    status=struct.unpack('<I',uc.mem_read(address-4,4))[0];uc.mem_write(address-4,word(status&~value)) # synthetic W1C
  if OUT-8<=address<OUT+12 and access==u.UC_MEM_WRITE:
   assert address==OUT and size==4;output_writes.append(value)
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem)
 params=[c['irq'],c['mask'],0,0]
 if c['op']=='status':params=[c['irq'],int(c['enabled_only']),0 if c['null'] else OUT,0]
 if c['op']=='register':params=[c['channel'],c['pin'],c['handler'],c['argument']]
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],params):cpu.reg_write(reg,val)
 cpu.reg_write(UC_ARM_REG_PRIMASK,c['prior']);cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,STOP|1);
 try:cpu.emu_start(entry|1,STOP,count=10000)
 except Exception as error:raise RuntimeError((c,'pc',hex(cpu.reg_read(UC_ARM_REG_PC)),'bytes',bytes(cpu.mem_read(cpu.reg_read(UC_ARM_REG_PC),4)).hex())) from error
 assert cpu.reg_read(UC_ARM_REG_PC)==STOP
 assert bytes(cpu.mem_read(OUT-8,8))==bytes(cpu.mem_read(OUT+4,8))==b'\xcc'*8
 return dict(status=cpu.reg_read(UC_ARM_REG_R0),output=struct.unpack('<I',cpu.mem_read(OUT,4))[0],output_writes=output_writes,mmio=mmio,calls=calls,final_primask=cpu.reg_read(UC_ARM_REG_PRIMASK),critical_reads=critical_reads,tables=bytes(cpu.mem_read(HANDLERS,0xe00)).hex(),initial_tables=initial_tables.hex(),registers=bytes(cpu.mem_read(GPIO+0x530,0xe0)).hex(),trace=trace)

def expected(c,result):
 i=bank(c['irq']);valid=i is not None;status=0;table=bytearray.fromhex(result['initial_tables']);output=0xabadcafe;calls=[];mmio=[]
 if c['op']=='status':
  if not valid or c['null']:status=6
  else:
   addr=GPIO+0x530+i*16
   if c['enabled_only']:mmio.append(['read',addr,c['enable']])
   mmio.append(['read',addr+4,c['status']]);output=c['status']&(c['enable'] if c['enabled_only'] else 0xffffffff)
 elif c['op']=='clear':
  if not valid:status=6
  else:mmio=[['write',GPIO+0x538+i*16,c['mask']]]
 elif c['op']=='register':
  if c['channel']>2:status=6
  else:
   for ch in ([0,1] if c['channel']==2 else [c['channel']]):
    slot=(c['pin']//32+ch*7)*32+c['pin']%32;struct.pack_into('<I',table,slot*4,c['handler']);struct.pack_into('<I',table,0x700+slot*4,c['argument'])
 else:
  if not valid:status=5
  else:
   missing=c['missing'] | (0x80000000 if c['mutate'] and c['mask']&1 and not c['missing']&1 else 0)
   for bit in range(32):
    if c['mask']>>bit&1:
     if missing>>bit&1:status=7
     else:calls.append([i*32+bit,0xa5000000|i<<8|bit,c['prior']])
   if c['mutate'] and c['mask']&1 and not c['missing']&1:
    slot=i*32+31;struct.pack_into('<I',table,slot*4,0);struct.pack_into('<I',table,0x700+slot*4,0xbabecafe)
 assert result['status']==status and result['output']==output,(c,result['status'],status,result['output'],output)
 assert result['mmio']==mmio and result['calls']==calls
 assert bytes.fromhex(result['tables'])==bytes(table)
 assert result['final_primask']==c['prior']

def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
 # Authenticate all bodies including registration using the fixed symbol census.
 import csv
 rows={int(x['address'],16):x for x in csv.DictReader((ROOT/'g2/symbols/apollo_main.tsv').open(),delimiter='\t')}
 for pc,n,digest,_ in FUN.values():assert sha(blob[pc-BASE+32:pc-BASE+32+n])==(digest or rows[pc]['stock_sha256'])
 assert sha(blob[0x473940-BASE+32:0x473948-BASE+32])=='720733fcf19a5635fcab0791fcc2b007294712bb27536443ff79490821c168cf'
 stock=[dict(address=pc,data=blob[pc-BASE+32:pc-BASE+32+4096],memory_size=4096,flags=5) for pc in [0x481000,0x473000]]
 elf,segs,syms=parser.elf_info(a.elf)
 default=dict(irq=59,mask=0x80000001,enable=0x55aa55aa,status=0xf0f0ff0f,enabled_only=False,null=False,missing=0,mutate=False,prior=0,channel=0,pin=0,handler=CB|1,argument=0x12345678)
 cases=[]
 irqs=list(range(56,63))+list(range(125,132))+[0,55,63,64,124,132,0xffffffff]
 for irq in irqs:
  for prior in [0,1]:
   for enabled in [False,True]:cases.append(dict(default,op='status',irq=irq,prior=prior,enabled_only=enabled))
   cases.append(dict(default,op='status',irq=irq,prior=prior,null=True));cases.append(dict(default,op='clear',irq=irq,prior=prior))
  for mask in [0,1,0x80000000,0x80000001,0xffffffff,0x13579bdf]:
   for missing in [0,1,0x80000000,0xffffffff]:cases.append(dict(default,op='service',irq=irq,mask=mask,missing=missing,prior=irq&1))
  cases.append(dict(default,op='service',irq=irq,mutate=True))
 for pin in [0,31,32,63,96,127,192,223]:
  for channel in [0,1,2,3,0xffffffff]:
   for handler in [0,CB|1]:cases.append(dict(default,op='register',pin=pin,channel=channel,handler=handler))
 results=[];observed={}
 for c in cases:
  pc,_,_,name=FUN[c['op']];x=run(stock,pc,c);y=run(segs,syms[name],c);trace=x.pop('trace');y.pop('trace');assert x==y,(c,x,y);expected(c,x);observed.update(trace);results.append(dict(inputs=c,result=x,original_trace=trace))
 ranges={name:dict(address=hex(pc),declared_bytes=n,executed_bytes=sum(len(bytes.fromhex(b)) for addr,b in observed.items() if pc<=addr<pc+n),sha256=sha(blob[pc-BASE+32:pc-BASE+32+n])) for name,(pc,n,_,_) in FUN.items()}
 # Exercise every reachable instruction; report the proven impossible six bytes separately.
 missing=[hex(addr) for addr in range(0x4816c6,0x48173a,2) if not any(pc<=addr<pc+len(bytes.fromhex(raw)) for pc,raw in observed.items())]
 # Guard accepts only56..62 or125..131.
 # 4816ea requiresirq<63 AND>=125; 4816fa requires63<=irq<125.
 # Both paths are unreachable for any input accepted by the original guard.
 assert missing==['0x4816ea','0x4816ec','0x4816fa'],missing
 assert all(x['declared_bytes']==x['executed_bytes'] for name,x in ranges.items() if name!='service'),ranges
 assert ranges['service']['executed_bytes']==110
 component=Path(__file__).resolve().parents[1]
 report=dict(status='PASS',case_count=len(cases),ranges=ranges,new_family_declared_instruction_bytes=sum(x['declared_bytes'] for x in ranges.values()),new_family_executed_instruction_bytes=sum(x['executed_bytes'] for x in ranges.values()),unreachable_original_ranges=[[0x4816ea,0x4816ee],[0x4816fa,0x4816fc]],unreachable_bytes=6,unreachable_proof='Guard allows only IRQ56..62 or125..131. First unreachable branch requires IRQ<63 and>=125; second requires IRQ63..124, rejected by guard.',shared_critical_instruction_bytes=8,cases=results,elf_sha256=sha(elf),firmware_sha256=sha(blob),verifier_sha256=sha(Path(__file__).read_bytes()),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(component.rglob('*')) if p.suffix in ['.c','.h','.ld']},shared_critical_source_sha256=sha((ROOT/'g2/components/foundation/ambiq_mspi/ambiq_interrupt_mask.c').read_bytes()),limits='All reachable paths across four original GPIO bodies and actual PRIMASK entry/restore execute;6 service bytes are statically unreachable after the validated IRQ guard. Only fixture callback functions intercepted; MMIO W1C is synthetic. Serialized fixtures prove bank mapping, status/clear accesses, live callback table behavior and return codes, not GPIO setup/physical pins/IRQ delivery/callback concurrency. Compile-fwrapv retained for stock signed-negation behavior; no full compiler byte equality claim.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(cases),'GPIO cases;',ranges)
if __name__=='__main__':main()
