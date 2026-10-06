#!/usr/bin/env python3
"""Instruction comparison of finite HAL MMIO/NVIC/PRIMASK providers."""
import argparse,importlib.util,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('base',HERE/'verify_nor_mspi_init.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);v=n.v
ENTRIES={"opencfw_bl_mspi_blocking_transfer":0x4262e0}
HANDLE=0x20006000
PIO=0x20007800
class Machine(v.Machine):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cpu.mem_map(0x40060000,0x4000)
 def code(self,uc,pc,size,user):
  if pc in (0x423e8a,0x423e40):self.events.append(['fifo-read' if pc==0x423e8a else 'fifo-write',*self.args()]);self.ret(self.fifo_status);return
  if pc==0x41d246:self.events.append(['poll',*self.args(),self.u(uc.reg_read(v.a.UC_ARM_REG_SP))]);self.ret(self.poll_status);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);fixtures=[];trace={};cases=[]
 for mode,direction,flags,busy,fifo,poll in itertools.product([0,10,11],[0,1,2,255],[0,1,3],[0,1,2,3,4],[0,7],[0,4]):fixtures.append(('opencfw_bl_mspi_blocking_transfer',[HANDLE,PIO,1000000],dict(mode=mode,direction=direction,flags=flags,busy=busy,fifo=fifo,poll=poll)))
 fixtures += [('opencfw_bl_mspi_blocking_transfer',[0,PIO,0],{}),('opencfw_bl_mspi_blocking_transfer',[HANDLE,PIO,0],dict(magic=0))]
 for entry,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];results=[]
  for m in pair:
   m.fifo_status=f.get('fifo',0);m.poll_status=f.get('poll',0);m.cpu.mem_write(HANDLE,bytes(0x8d0));m.w(HANDLE,f.get('magic',0x01bebebe));m.w(HANDLE+4,1);m.w(HANDLE+16,8);m.cpu.mem_write(HANDLE+10,bytes([f.get('mode',0)]));m.cpu.mem_write(HANDLE+13,b'\x05');m.w(HANDLE+32,1 if f.get('busy')==1 else 0);m.w(HANDLE+0x840,1 if f.get('busy')==2 else 0);m.cpu.mem_write(HANDLE+0x82c,bytes([2 if f.get('busy')==3 else 0]));m.w(PIO,17);m.cpu.mem_write(PIO+4,bytes([2,1,f.get('direction',0),1]));m.w(PIO+8,0x12340000|f.get('flags',0));m.cpu.mem_write(PIO+12,bytes.fromhex('01009f000103'));m.cpu.mem_write(PIO+18,bytes([1 if f.get('busy')==4 else 0,0]));m.w(PIO+20,0x20007000);m.cpu.mem_write(0x40060000,bytes([0xa5])*0x4000);m.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
   for r,x in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3],args+[0]*4):m.cpu.reg_write(r,x)
   m.cpu.emu_start((syms[entry] if m.source else ENTRIES[entry])|1,v.STOP+2,count=10000);assert m.finished
   results.append(dict(events=m.events,handle=bytes(m.cpu.mem_read(HANDLE,0x8d0)).hex(),state=bytes(m.cpu.mem_read(0x2001caa0,3*0x8d0)).hex(),mmio=bytes(m.cpu.mem_read(0x40060000,0x4000)).hex(),nvic=bytes(m.cpu.mem_read(0xe000e000,0x2000)).hex(),primask=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),result=None if entry in ['opencfw_bl_interrupt_enable','opencfw_bl_interrupt_priority'] else m.cpu.reg_read(v.a.UC_ARM_REG_R0)))
  assert results[0]==results[1],(entry,args,f,[(r['result'],r['events']) for r in results]);trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=f,result=results[0]['result'],events=results[0]['events']))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'blocking_transfer.c',HERE/'blocking_module.ld',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['MMIO registers are synthetic RAM; control composition, errors and IRQ save/restore observed. FIFO read/write and timed status polling are explicit provider cuts; no transfer/timing/IRQ delivery proved.','Return comparison covers declared statusR0 only. Stock incidentally restores R1 from saved timeout or overwritten1; it is not treated as a second public result.','No full boot, byte equality or actual hardware.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
