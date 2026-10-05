#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare reconstructed radio consumer with authenticated original instructions.
Only scheduler event submission is intercepted; GPIO W1C is synthetic.
"""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/foundation/touch_scb/simulator/verify.py');elfparser=importlib.util.module_from_spec(spec);spec.loader.exec_module(elfparser)
BASE=0x438000;STOP=0x8000000;H=0x20068228;A=0x20068928;COUNTER=0x20074640;ID=0x20074fcb
sha=lambda b:hashlib.sha256(b).hexdigest()
w=lambda n:struct.pack('<I',n)
def run(segments,entry,end,callback,event,c,stock):
 import unicorn as u
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);pages=set()
 for s in segments:
  for p in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
  cpu.mem_write(s['address'],s['data'])
 for lo,n in [(0x20000000,0x80000),(0x40010000,4096),(STOP,4096),(0xe000e000,4096)]:
  for p in range(lo,lo+n,4096):
   if p not in pages:cpu.mem_map(p,4096);pages.add(p)
 cpu.mem_write(COUNTER,w(c['counter']));cpu.mem_write(ID,bytes([c['id']]))
 for i in range(14):cpu.mem_write(0x40010530+i*16,w(c['enabled'])+w(c['mask'] if i==3 else 0x80000000|i)+w(0))
 if c['op'] not in ['register','setup']:cpu.mem_write(H+117*4,w(callback|1))
 mmio=[];events=[];publication=[];trace={};nvic=[]
 def code(uc,pc,size,_):
  if pc==(event&~1):
   events.append([uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),struct.unpack('<I',uc.mem_read(COUNTER,4))[0],uc.reg_read(UC_ARM_REG_PRIMASK)])
   uc.reg_write(UC_ARM_REG_R0,0x1234);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  ss=[s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data'])];assert len(ss)==1,hex(pc)
  raw=bytes(uc.mem_read(pc,size));s=ss[0];assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,addr,size,value,_):
  if 0x40010000<=addr<0x40011000:
   assert size==4
   read=access==u.UC_MEM_READ;v=struct.unpack('<I',uc.mem_read(addr,4))[0] if read else value
   mmio.append(['read' if read else 'write',addr,v,uc.reg_read(UC_ARM_REG_PRIMASK)])
   if read:assert uc.reg_read(UC_ARM_REG_PRIMASK)==1
   else:
    assert addr in [0x40010568,0x40010560]
    if addr==0x40010568:uc.mem_write(addr-4,w(struct.unpack('<I',uc.mem_read(addr-4,4))[0]&~value))
  if 0xe000e000<=addr<0xe000f000:
   assert access==u.UC_MEM_WRITE and (addr,size) in [(0xe000e43b,1),(0xe000e104,4)];nvic.append([addr,size,value,uc.reg_read(UC_ARM_REG_PRIMASK)])
  if access==u.UC_MEM_WRITE and (H<=addr<H+0x700 or A<=addr<A+0x700):
   publication.append([addr,'radio_callback' if value==(callback|1) else value])
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem)
 cpu.reg_write(UC_ARM_REG_R0,0xfeedface);cpu.reg_write(UC_ARM_REG_SP,0x2000f000);cpu.reg_write(UC_ARM_REG_LR,STOP|1);cpu.reg_write(UC_ARM_REG_PRIMASK,c['prior'])
 cpu.emu_start(entry|1,end,count=20000);assert cpu.reg_read(UC_ARM_REG_PC)==end
 tables=bytearray(cpu.mem_read(H,0xe00));ptr=struct.unpack_from('<I',tables,117*4)[0];assert ptr==callback|1;struct.pack_into('<I',tables,117*4,1)
 return dict(nvic=nvic,counter=struct.unpack('<I',cpu.mem_read(COUNTER,4))[0],events=events,mmio=mmio,publication=publication,tables=tables.hex(),registers=bytes(cpu.mem_read(0x40010530,0xe0)).hex(),primask=cpu.reg_read(UC_ARM_REG_PRIMASK),trace=trace)
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';data=blob[32:]
 stock=[dict(address=BASE,data=data,memory_size=len(data),flags=5)];elf,segs,syms=elfparser.elf_info(args.elf)
 entries={'irq':(0x4b80be,'GPIO0_607F_IRQHandler'),'callback':(0x4b4a98,'opencfw_radio_gpio_callback'),'register':(0x4b49a8,'opencfw_radio_gpio_register'),'enable':(0x52dd58,'opencfw_radio_gpio_enable'),'disable':(0x52dd6a,'opencfw_radio_gpio_disable'),'setup':(0x4b49a8,'opencfw_radio_gpio_irq_setup')}
 cases=[]
 for op in entries:
  for prior in [0,1]:
   for counter in [0,0x7fffffff,0xffffffff]:
    for hid in [0,7,255]:
     for mask in ([0,1,1<<21,(1<<21)|1,0xffffffff] if op=='irq' else [0]):cases.append(dict(op=op,prior=prior,counter=counter,id=hid,mask=mask,enabled=0xffffffff if op=='disable' else 0x80400001 if op=='enable' else 0))
 results=[];observed={}
 for c in cases:
  pc,name=entries[c['op']];x=run(stock,pc,0x4b49b6 if c['op']=='register' else 0x4b49c8 if c['op']=='setup' else STOP,0x4b4a98,0x52b91e,c,True);y=run(segs,syms[name],STOP,syms['opencfw_radio_gpio_callback'],syms['opencfw_radio_scheduler_event'],c,False)
  t=x.pop('trace');y.pop('trace');assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});observed.update(t)
  fired=c['op']=='callback' or c['op']=='irq' and bool(c['mask']&(1<<21));assert x['counter']==(c['counter']+fired)&0xffffffff
  assert x['events']==([[c['id'],1,x['counter'],c['prior']]] if fired else []);assert x['primask']==c['prior']
  if c['op']=='irq':
   assert [v[1] for v in x['mmio']]==[0x40010534+i*16 for i in range(7)]+[0x40010564,0x40010568]
   assert x['mmio'][-1][2]==c['mask'] and x['mmio'][-1][3]==c['prior']
  if c['op'] in ['enable','disable','setup']:
   mask=(c['enabled']|1<<21) if c['op']!='disable' else c['enabled']&~(1<<21)
   assert x['mmio']==[['read',0x40010560,c['enabled'],1],['write',0x40010560,mask,1]]
  assert x['nvic']==([[0xe000e43b,1,0x40,c['prior']],[0xe000e104,4,1<<27,c['prior']]] if c['op']=='setup' else [])
  if c['op'] in ['register','setup']:assert x['publication']==[[H+117*4,'radio_callback'],[A+117*4,0]]
  results.append(dict(inputs=c,result=x,original_trace=t))
 comp=Path(__file__).resolve().parents[1]
 report=dict(status='PASS',case_count=len(cases),cases=results,unique_original_trace_bytes=sum(len(bytes.fromhex(v)) for v in observed.values()),original_trace={hex(k):v for k,v in sorted(observed.items())},firmware_sha256=sha(blob),elf_sha256=sha(elf),source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},limits='Scheduler provider intercepted on both sides: validates submitted ID/mask, counter-before-event and PRIMASK only. Synthetic W1C and serialized execution; no asynchronous pad/NVIC delivery, boot scheduler initialization, cancellation or ownership/race proof. Registration and IRQ setup tail only, not full HciDrvRadioBoot; pin disable leaves callback/NVIC/pending untouched. Snapshot reconstruction implements only channel0/raw branch.')
 args.output.parent.mkdir(parents=True,exist_ok=True)
 with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(cases),'consumer comparisons',report['unique_original_trace_bytes'],'unique original bytes')
if __name__=='__main__':main()
