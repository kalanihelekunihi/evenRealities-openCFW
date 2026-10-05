#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""General GPIO interrupt control plus actual radio control/gate/shutdown slice."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[5];BASE=0x438000;GPIO=0x40010000;IN=0x20002000;STOP=0x8000000
spec=importlib.util.spec_from_file_location('gpio',Path(__file__).with_name('verify.py'));gpio=importlib.util.module_from_spec(spec);spec.loader.exec_module(gpio)
w=gpio.w;sha=gpio.sha
FUN={'control':(0x4810b0,'opencfw_gpio_interrupt_control_raw'),'enable':(0x52dd58,'opencfw_radio_irq_enable_exact'),'disable':(0x52dd6a,'opencfw_radio_irq_disable_exact'),'gate':(0x52eece,'opencfw_radio_pin136_gate_raw'),'phase':(0x4b49d8,'opencfw_radio_gpio_shutdown_phase')}
BODIES=[(0x4810b0,582),(0x480ed8,22),(0x52dd58,18),(0x52dd6a,18),(0x52eece,28)]
# The helper always returns0; caller's 4810ee..4810f2 failure branch is unreachable.
UNREACHABLE=range(0x4810ee,0x4810f2)
def init(c):
 regs=bytearray(gpio.initial_registers(c)+b'\xa5'*(0x610-0x4cc))
 for i in range(14):
  a=0x530+i*16;regs[a:a+16]=w(c['enabled']^(i*0x01010101))+w(0x81234567)+w(0x11111111)+w(0x22222222)
 return regs

def expected(c):
 regs=init(c);mmio=[];calls=[];borrow=[];status=None
 def read(a):
  v=struct.unpack_from('<I',regs,a-GPIO)[0];mmio.append(['read',a,v,1]);return v
 def put(a,v,mask):
  mmio.append(['write',a,v,mask]);gpio.device_effect(regs,a,v,c);struct.pack_into('<I',regs,a-GPIO,v)
 def control(ch,op,data):
  ch&=255;op&=255;calls.append(['control',ch,op,None if data is None else data if op in [2,3] else data[:1],c['prior']])
  if data is None or op>3:return 6
  if op<2:
   pin=data[0]
   if c['op']=='control':borrow.append([0,pin,c['prior']])
   if pin>=224:return 5
   banks=[(1 if ch==1 else 0,pin//32)]
   if ch==2:banks.append((1,pin//32))
   masks=[1<<(pin&31)]*len(banks)
  else:
   banks=[(chx,b) for chx in [0,1] if (ch!=1 if chx==0 else ch!=0) for b in range(7)];masks=[data[b] for chx,b in banks]
  for (chx,b),mask in zip(banks,masks):
   if op>=2 and c['op']=='control':borrow.append([b*4,mask,1])
   a=GPIO+0x530+chx*0x70+b*16;v=read(a);put(a,(v|mask) if op in [1,3] else (v&~mask)&0xffffffff,1)
  return 0
 def state(pin,op):
  calls.append(['state',pin,op,c['prior']]);a=GPIO+gpio.FAMILIES['WTS' if op else 'WTC']+(pin//32)*4;put(a,1<<(pin&31),c['prior'])
 if c['op']=='control':status=control(c['channel'],c['control'],None if c['null'] else c['input'])
 elif c['op'] in ['enable','disable']:control(0,1 if c['op']=='enable' else 0,[117])
 elif c['op']=='gate':state(136,1 if c['value']&255 else 0)
 else:
  control(0,0,[117]);state(136,0);state(93,0);calls.append(['config',138,3,c['prior']]);put(GPIO+0x400,0x73,1);put(GPIO+4*138,3,1);put(GPIO+0x400,0,1)
 return dict(status=status,mmio=mmio,calls=calls,input_reads=borrow,registers=regs.hex(),primask=c['prior'])

def run(segments,entry,c,entries,stock):
 import unicorn as u
 import unicorn.arm_const as arm
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);cpu.ctl_set_cpu_model(arm.UC_CPU_ARM_CORTEX_M4);pages=set()
 for s in segments:
  for a in range(s['address']&~4095,(s['address']+s['memory_size']+4095)&~4095,4096):
   if a not in pages:cpu.mem_map(a,4096);pages.add(a)
  cpu.mem_write(s['address'],s['data'])
 for lo,n in [(0x20000000,0x10000),(GPIO,4096),(STOP,4096)]:
  for a in range(lo,lo+n,4096):
   if a not in pages:cpu.mem_map(a,4096);pages.add(a)
 cpu.mem_write(GPIO,bytes(init(c)));input_bytes=b''.join(w(v) for v in c['input']);cpu.mem_write(IN-8,b'\xcc'*8+input_bytes+b'\xcc'*8)
 trace={};mmio=[];calls=[];borrow=[]
 def code(uc,pc,size,_):
  if pc in entries.values():
   name=next(k for k,a in entries.items() if pc==a);r0=uc.reg_read(arm.UC_ARM_REG_R0);r1=uc.reg_read(arm.UC_ARM_REG_R1);mask=uc.reg_read(arm.UC_ARM_REG_PRIMASK)
   if name=='control':
    ptr=uc.reg_read(arm.UC_ARM_REG_R2);op=r1&255;data=None if ptr==0 else list(struct.unpack('<'+('I'*7 if op in [2,3] else 'I'),uc.mem_read(ptr,28 if op in [2,3] else 4)));calls.append(['control',r0&255,op,data,mask])
   else:calls.append([name,r0,r1&255 if name=='state' else r1,mask])
  s=next(s for s in segments if s['flags']&1 and s['address']<=pc<pc+size<=s['address']+len(s['data']));raw=bytes(uc.mem_read(pc,size));assert raw==s['data'][pc-s['address']:pc-s['address']+size];trace[pc]=raw.hex()
 def mem(uc,access,a,size,value,_):
  assert size==4 and a%4==0
  if GPIO<=a<GPIO+0x610:
   read=access==u.UC_MEM_READ;v=struct.unpack('<I',uc.mem_read(a,4))[0] if read else value;prior=uc.reg_read(arm.UC_ARM_REG_PRIMASK);mmio.append(['read' if read else 'write',a,v,prior])
   if a>=GPIO+0x530 or a<GPIO+224*4 or a==GPIO+0x400:assert prior==1
   if not read:
    if a<GPIO+224*4:assert struct.unpack('<I',uc.mem_read(GPIO+0x400,4))[0]==0x73
    regs=bytearray(uc.mem_read(GPIO,0x610));effect=gpio.device_effect(regs,a,value,c)
    if effect:offset,v=effect;uc.mem_write(GPIO+offset,w(v))
  else:
   assert access==u.UC_MEM_READ and IN<=a<IN+28;borrow.append([a-IN,struct.unpack('<I',uc.mem_read(a,4))[0],uc.reg_read(arm.UC_ARM_REG_PRIMASK)])
 cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem,begin=GPIO,end=GPIO+0x60f);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem,begin=IN-8,end=IN+35)
 for reg,value in [(arm.UC_ARM_REG_R0,c['channel'] if c['op']=='control' else c['value']),(arm.UC_ARM_REG_R1,c['control']),(arm.UC_ARM_REG_R2,0 if c['null'] else IN),(arm.UC_ARM_REG_SP,0x2000f000),(arm.UC_ARM_REG_LR,STOP|1),(arm.UC_ARM_REG_PRIMASK,c['prior'])]:cpu.reg_write(reg,value)
 saved={getattr(arm,'UC_ARM_REG_R'+str(i)):0xa6000000+i for i in range(4,12)}
 for reg,value in saved.items():cpu.reg_write(reg,value)
 end=0x4b49e6 if stock and c['op']=='phase' else STOP;cpu.emu_start(entry|1,end,count=2000)
 assert cpu.reg_read(arm.UC_ARM_REG_PC)==end and cpu.reg_read(arm.UC_ARM_REG_SP)==0x2000f000
 assert all(cpu.reg_read(reg)==value for reg,value in saved.items());assert bytes(cpu.mem_read(IN-8,44))==b'\xcc'*8+input_bytes+b'\xcc'*8
 return dict(status=cpu.reg_read(arm.UC_ARM_REG_R0) if c['op']=='control' else None,mmio=mmio,calls=calls,input_reads=borrow,registers=bytes(cpu.mem_read(GPIO,0x610)).hex(),primask=cpu.reg_read(arm.UC_ARM_REG_PRIMASK),trace=trace)

def cases():
 d=dict(op='control',channel=0,control=0,input=[0]*7,null=False,prior=0,enabled=0xa5a55a5a,value=0,wt=0xa5a55a5a,en=0x5a5aa5a5,model='raw',output_active_mask=0xffffffff)
 for pin in range(224):
  for ch in range(3):
   for op in range(2):
    for prior in [0,1]:
     for pattern in [0,0xffffffff]:yield dict(d,input=[pin]+[0]*6,channel=ch,control=op,prior=prior,enabled=pattern)
 patterns=[[0]*7,[0xffffffff]*7,[1<<(b*5%32) for b in range(7)],[0xaaaaaaaa,0x55555555,0,1,0xffffffff,0x80000000,0x12345678]]
 for ch in [0,1,2,3,255,256,257,258,0xffffffff]:
  for op in [2,3,0x102,0x103]:
   for masks in patterns:
    for prior in [0,1]:yield dict(d,channel=ch,control=op,input=masks,prior=prior)
 for ch in [0,1,2,3,255,256,257,258,0xffffffff]:
  for op in [0,1,4,255,256,257,260,0xffffffff]:
   for pin in [0,223,224,255,256,0xffffffff]:
    for null in [False,True]:yield dict(d,channel=ch,control=op,input=[pin]+[0]*6,null=null)
 for op in ['enable','disable','gate','phase']:
  for prior in [0,1]:
   for pattern in [0,0xffffffff,0xa5a55a5a]:
    for model in ['raw','side_effects']:
     for value in ([0,1,2,255,256,257,0xffffffff] if op=='gate' else [0]):yield dict(d,op=op,prior=prior,enabled=pattern,value=value,model=model)

def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';elf,segs,syms=gpio.parser.elf_info(a.elf)
 stock=[dict(address=addr,data=blob[32+addr-BASE:32+addr-BASE+4096],memory_size=4096,flags=5) for addr in [0x480000,0x481000,0x473000,0x52d000,0x52e000,0x78e000,0x768000,0x4b4000]]
 old={'control':0x4810b0,'state':0x480fd6,'config':0x480f0c};new={'control':syms['am_hal_gpio_interrupt_control']&~1,'state':syms['am_hal_gpio_state_write']&~1,'config':syms['am_hal_gpio_pinconfig']&~1};results=[];observed={}
 for c in cases():
  pc,name=FUN[c['op']];x=run(stock,pc,c,old,True);y=run(segs,syms[name]&~1,c,new,False);t=x.pop('trace');y.pop('trace');assert x==y,(c,{k:(x[k],y[k]) for k in x if x[k]!=y[k]});z=expected(c);assert x==z,(c,{k:(x[k],z[k]) for k in x if x[k]!=z[k]});observed.update(t);results.append(dict(inputs=c,result=x,original_trace=t))
 executed={a+i for a,raw in observed.items() for i in range(len(bytes.fromhex(raw)))}
 for pc,n in BODIES:assert set(range(pc,pc+n))-set(UNREACHABLE)<=executed,hex(pc)
 assert not executed&set(UNREACHABLE);assert set(range(0x4b49d8,0x4b49e6))<=executed
 comp=Path(__file__).resolve().parents[1];report=dict(status='PASS',cases=len(results),results=results,original_trace={hex(a):raw for a,raw in sorted(observed.items())},unique_original_trace_bytes=len(executed),unreachable_original_bytes=[hex(a) for a in UNREACHABLE],source_manifest={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(comp.rglob('*')) if p.suffix in ['.c','.h','.ld','.py']},firmware_sha256=sha(blob),elf_sha256=sha(elf),limits='Full control body except4 statically unreachable helper-failure bytes; actual helper/PRIMASK/state/config and void wrappers, no call stubs. GPIO-only shutdown slice ends before caller state clearing/transport release; prior timer stop excluded. Input read order/masks/unchanged borrowed data checked; synthetic W1 device effects and externally supplied output-active mask, no physical IRQ/pad/NVIC/shutdown or concurrency proof. Optimized tick remains blocked.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS',len(results),'original/source/model cases;',len(executed),'unique original bytes')
if __name__=='__main__':main()
