#!/usr/bin/env python3
"""Service guard/mutex wrappers and record reset; lower RTOS APIs explicit.
Original fill can run natively or be isolated as the known Unicorn boundary.
"""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
s=importlib.util.spec_from_file_location('base',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
SLOT,RECORDS=0x200270e8,0x20026700
ENTRIES={'guard':('opencfw_bl_service_guard',0x41a684),'initialize':('opencfw_boot_service_mutex_initialize',0x41a648),'acquire':('opencfw_boot_service_mutex_acquire',0x41a65c),'release':('opencfw_boot_service_mutex_release',0x41a672),'wake':('opencfw_bl_service_wake',0x41a69a),'sleep':('opencfw_bl_service_sleep',0x41a6a2),'commit':('opencfw_bl_service_commit',0x4175b4)}
class Machine(v.Machine):
 def __init__(self,source,segs,syms,f):super().__init__(source,segs,syms);self.fixture=f;self.calls=[];self.records=[];self.fill_calls=[]
 def memwrite(self,uc,access,address,size,value,user):
  if address==SLOT or RECORDS<=address<RECORDS+256:self.records.append([address,size,value&((1<<(size*8))-1)])
 def code(self,uc,pc,size,user):
  create=(self.symbols.get("opencfw_bl_mutex_create",0)&~1) if self.source else 0x416610
  take=(self.symbols.get("opencfw_boot_fs_mutex_acquire",0)&~1) if self.source else 0x4166aa
  give=(self.symbols.get("opencfw_boot_fs_mutex_release",0)&~1) if self.source else 0x416710
  if pc in (create,take,give):
   args=[uc.reg_read(x) for x in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1)];kind='create' if pc==create else 'take' if pc==take else 'give';event=[kind,args[0]]
   if kind=='create':event.append(bytes(uc.mem_read(args[0],16)).hex())
   if kind=='take':event.append(args[1])
   self.calls.append(event);uc.reg_write(a.UC_ARM_REG_R0,self.fixture['created'] if kind=='create' else self.fixture['kernel_status']);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc==0x41560c:
   p,n,fill=[uc.reg_read(x) for x in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2)];self.fill_calls.append([p,n,fill&255])
   if self.fixture.get('model_fill'):
    uc.mem_write(p,bytes([fill&255])*n);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def call(self,kind):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000);self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1);self.cpu.reg_write(a.UC_ARM_REG_R0,0x12345678);name,original=ENTRIES[kind];self.cpu.emu_start((self.symbols[name]&~1 if self.source else original)|1,v.STOP+2,count=10000);assert self.done,(kind,self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)));return self.cpu.reg_read(a.UC_ARM_REG_R0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--native-fill',action='store_true');args=ap.parse_args();_,segs,syms=v.elf.elf_info(args.elf);cases=[];trace={};blob=v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.LOCKED_SHA
 def compare(label,seq,slot=0,created=0x2002a000,kernel_status=0):
  obs=[]
  for source in (False,True):
   m=Machine(source,segs,syms,dict(created=created,kernel_status=kernel_status,model_fill=not args.native_fill));m.cpu.mem_write(SLOT,struct.pack('<I',slot));m.cpu.mem_write(RECORDS,bytes(range(256)));m.records.clear();status=[m.call(k) for k in seq];o=dict(guard_results=[value for k,value in zip(seq,status) if k=='guard'],slot=int.from_bytes(m.cpu.mem_read(SLOT,4),'little'),calls=m.calls,records=bytes(m.cpu.mem_read(RECORDS,256)).hex(),explicit_stores=[x for x in m.records if x[0]==SLOT or x[1]==1 and (x[0]-RECORDS-0x31)%33==0 or x[1]==1 and (x[0]-RECORDS-0x51)%33==0]);obs.append(o)
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  # Reset-byte store widths/order differ inside generic memset; compare final
  # 256-byte state and the owned record marker stores, not compiler loop shape.
  if 'commit' in seq:
   for o in obs:o.pop('explicit_stores')
  assert obs[0]==obs[1],(label,obs);cases.append(dict(label=label,observation=obs[0]));return obs[0]
 for kind,slot,created,status in itertools.product(('guard','initialize','acquire','release','wake','sleep'),(0,0x2002a000,0x2002a001),(0,0x2002b000),(0,1,0xffffffff)):
  o=compare(str((kind,slot,created,status)),[kind],slot,created,status)
  if kind=='guard':assert o['guard_results']==[0]
 for created in (0,0x2002b000):compare('repeat-guard-'+str(created),['guard','guard','wake','sleep'],0,created,0xffffffff)
 for slot in (0,0x2002a000):
  o=compare('record-clear-'+str(slot),['commit','commit'],slot);expected=bytearray(range(256))
  for i in range(5):expected[0x31+33*i:0x52+33*i]=bytes(33)
  assert o['records']==expected.hex() and o['slot']==slot
 for pc,raw in trace.items():p=int(pc,16);assert bytes.fromhex(raw)==blob[p-v.BASE:p-v.BASE+len(bytes.fromhex(raw))]
 ranges={kind:[p,{'initialize':0x41a65c,'acquire':0x41a672,'release':0x41a684,'guard':0x41a692,'wake':0x41a6a2,'sleep':0x41a6aa,'commit':0x41760a}[kind]] for kind,(_,p) in ENTRIES.items()};visited={k:sum(len(bytes.fromhex(raw)) for pc,raw in trace.items() if lo<=int(pc,16)<hi) for k,(lo,hi) in ranges.items()}
 r=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,original_trace=trace,body_ranges=ranges,visited_body_bytes=visited,comparisons=cases,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['Original/source guard, initializer, take/give and wake/sleep wrappers and record loop execute. Mutex create/take/give are explicit injected APIs, not native RTOS/kernel closure.','Original41560c fill is '+('native' if args.native_fill else 'modeled by exact requested bytes because of the previously reproduced Unicorn IT/STM carry bug')+'; source uses native shared memset. Whole256-byte region and retained sentinel bytes compare.','Guard returns0 even if mutex creation returns0. Repeated failed creation retries; existing handle bypasses creation. Kernel take/give statuses are ignored; 1000 is an unconverted API timeout value, not proven milliseconds.','No real exclusion, priority inheritance, allocator ownership, IRQ/task delivery or asynchronous drain proof.']);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256','visited_body_bytes']}))
if __name__=='__main__':main()
