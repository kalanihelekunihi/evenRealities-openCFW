#!/usr/bin/env python3
"""Instruction comparison of finite HAL MMIO/NVIC/PRIMASK providers."""
import argparse,importlib.util,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('base',HERE/'verify_nor_mspi_init.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);v=n.v
ENTRIES={'opencfw_hal_mspi_interrupt_enable':0x426450,'opencfw_hal_mspi_interrupt_clear':0x426506,'opencfw_hal_mspi_deinitialize':0x42516c,'opencfw_bl_interrupt_enable':0x41fdc0,'opencfw_bl_interrupt_priority':0x41fdde,'opencfw_bl_irq_guard_initialize':0x41b8e0,'opencfw_hal_mspi_enable':0x425066,'opencfw_hal_mspi_disable':0x4250f0,'opencfw_hal_mspi_configure':0x424af0}
HANDLE=0x20006000
class Machine(v.Machine):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cpu.mem_map(0x40060000,0x4000)
 def code(self,uc,pc,size,user):
  if pc==0x423f28:self.events.append(['cq-init',*self.args()[:3]]);self.ret();return
  if pc==0x423fac:self.events.append(['cq-disable',self.args()[0]]);self.ret(self.disable_status);return
  if pc==0x423f54:self.events.append(['cq-term',self.args()[0]]);self.ret();return
  if pc==0x41d1c0:self.events.append(['delay-us-argument',self.args()[0]]);self.ret();return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);fixtures=[];trace={};cases=[]
 for entry in list(ENTRIES)[:3]:
  for handle,magic,module,mask,status in itertools.product([0,HANDLE],[0,0x01bebebe,0x03bebebe,0xffbebebe],[0,1,2],[0,0xa55a],[0,7]):fixtures.append((entry,[handle,mask],dict(magic=magic,module=module,status=status)))
 for entry,configured,cq,busy,status,delayed in itertools.product(['opencfw_hal_mspi_enable','opencfw_hal_mspi_disable'],[0,1],[0,4],[0,1,2],[0,7],[0,1]):fixtures.append((entry,[HANDLE],dict(magic=0x03bebebe,module=1,status=status,configured=configured,cq=cq,busy=busy,delayed=delayed)))
 for magic,module,words,cq in itertools.product([0,0x01bebebe,0x03bebebe],[0,1,2],[0,8,256,10000],[0,0x20007000]):fixtures.append(('opencfw_hal_mspi_configure',[HANDLE,0x20007800],dict(magic=magic,module=module,words=words,cq=cq)))
 for irq,priority in itertools.product([0,21,31,32,63,255,0xffff,0xfffc,0x10015,0x18000],[0,1,4,15,16,255]):fixtures.append(('opencfw_bl_interrupt_priority',[irq,priority],{}))
 for irq in [0,21,31,32,63,255,0xffff,0x10015,0x18000]:fixtures.append(('opencfw_bl_interrupt_enable',[irq],{}))
 for primask in [0,1]:fixtures.append(('opencfw_bl_irq_guard_initialize',[],dict(primask=primask)))
 for entry,args,f in fixtures:
  pair=[Machine(),Machine(True,segs,syms)];results=[]
  for m in pair:
   m.disable_status=f.get('status',0);m.cpu.mem_write(HANDLE,bytes([0xcc])*0x8d0);m.w(HANDLE+8,f.get('configured',1));m.w(0x20007800,f.get('words',256));m.w(0x20007804,f.get('cq',0));m.w(0x20007808,0xaabbcc01);m.w(HANDLE+20,f.get('words',256));m.w(HANDLE+24,f.get('cq',0));m.w(HANDLE+28,0xaabbccdd);m.w(HANDLE+32,1 if f.get('busy')==1 else 0);m.w(HANDLE+0x840,1 if f.get('busy')==2 else 0);m.w(HANDLE+0x8cc,17);m.w(HANDLE,f.get('magic',0));m.w(HANDLE+4,f.get('module',0));m.cpu.mem_write(0x40060000,bytes([0xa5])*0x4000);m.w(0x40060000+(f.get('module',0)<<12)+0x90,f.get('delayed',0));m.cpu.mem_write(0xe000e000,bytes([0x5a])*0x2000);m.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK,f.get('primask',0));m.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
   for r,x in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3],args+[0]*4):m.cpu.reg_write(r,x)
   m.cpu.emu_start((syms[entry] if m.source else ENTRIES[entry])|1,v.STOP+2,count=10000);assert m.finished
   results.append(dict(events=m.events,handle=bytes(m.cpu.mem_read(HANDLE,0x8d0)).hex(),state=bytes(m.cpu.mem_read(0x2001caa0,3*0x8d0)).hex(),mmio=bytes(m.cpu.mem_read(0x40060000,0x4000)).hex(),nvic=bytes(m.cpu.mem_read(0xe000e000,0x2000)).hex(),primask=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),result=None if entry in ['opencfw_bl_interrupt_enable','opencfw_bl_interrupt_priority'] else m.cpu.reg_read(v.a.UC_ARM_REG_R0)))
  assert results[0]==results[1],(entry,args,f,[(r['result'],r['events']) for r in results]);trace.update(pair[0].trace);cases.append(dict(entry=entry,args=args,fixture=f,result=results[0]['result'],events=results[0]['events']))
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'hal_leaves.c',HERE/'irq_guard.S',HERE/'leaves_module.ld',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['MMIO/NVIC registers are ordinary synthetic RAM: writes/read addresses and results tested, no hardware W1C semantics or interrupt delivery.','Actual configure/enable/disable/deinitialize execute. Configure tests include unsigned slot-count underflow/saturation and separate canonical state versus input handle; null/config-pointer faults are outside the accepted fixture inputs. CQ init/disable/terminate and delay-us are observed external call cuts; no CQ hardware progress or delay timing proved. Deinitialize ignores actual disable failure as stock does.','Bounded valid module indices0..2 only; raw stock has no index range guard. Priority negative exception numbers use stock low nibble mapping. PRIMASK read+enable is unconditional stock assembly, no decompiler privilege checks.','No byte identity or physical boot.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
