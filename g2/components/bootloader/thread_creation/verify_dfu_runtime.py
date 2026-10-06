#!/usr/bin/env python3
"""Reset to actual DFU runtime wrapper and architectural handoff, with named power cuts."""
import argparse,importlib.util,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('bridge',HERE/'verify_manager_bridge.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);v=b.v;c=b.c
EXECUTED={'opencfw_provider_41fe28':0x41fe28,'opencfw_provider_41fe62':0x41fe62,'opencfw_hal_mspi_enable':0x425066,'opencfw_hal_mspi_disable':0x4250f0,'opencfw_hal_mspi_deinitialize':0x42516c,'opencfw_hal_mspi_interrupt_clear':0x426506,'opencfw_hal_mspi_interrupt_enable':0x426450,'opencfw_bl_interrupt_priority':0x41fdde,'opencfw_bl_interrupt_enable':0x41fdc0,'opencfw_bl_irq_guard_initialize':0x41b8e0,'opencfw_boot_dfu_runtime_enable':0x42ddf2,'opencfw_boot_control_mode_two':0x41ba80,'opencfw_boot_control_finish':0x41cd60,'opencfw_hal_mspi_configure':0x424af0,'opencfw_bl_mspi_blocking_transfer':0x4262e0,'opencfw_boot_control_power_apply':0x422ba8,'opencfw_hal_mspi_fifo_read':0x423e8a,'opencfw_hal_mspi_fifo_write':0x423e40,'opencfw_hal_status_poll':0x41d246,'opencfw_boot_control_transition':0x41b954,'opencfw_boot_control_query':0x41c2d8,'opencfw_boot_control_delay_status_change':0x41d21c}
class Machine(b.Machine):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.runtime=True;self.reset=True;self.dispatch=True;self.executed={(self.symbols[name]&~1) if self.source else addr for name,addr in EXECUTED.items() if not self.source or name in self.symbols};self.cpu.mem_map(0x40060000,0x4000);self.cpu.mem_map(0x40010000,0x1000);self.cpu.mem_map(0x40020000,0x2000);self.boundary_events=[]
 def code(self,uc,pc,size,user):
  if pc==self.application_reset:
   self.boundary_events.append(['application-reset-entry',hex(pc),self.u(0xe000ed08),uc.reg_read(v.a.UC_ARM_REG_SP),uc.reg_read(v.a.UC_ARM_REG_PRIMASK)]);self.stop('dfu-dispatch-boundary');return
  if pc==0x08002210:raise AssertionError('accepted power object requires unclosed configure provider')
  if pc==0x08002200:self.boundary_events.append(['finish-callback']);self.ret(self.finish_status);return
  poll_entry=(self.symbols['opencfw_hal_status_poll']&~1) if self.source else 0x41d246
  if pc==poll_entry:
   timeout,address,mask,expected=self.args();equal=self.u(uc.reg_read(v.a.UC_ARM_REG_SP));self.boundary_events.append(['status-poll',timeout,address,mask,expected,equal])
   # Synthetic peripheral progress only: command completed before final poll.
   if (address-0x40060000)%0x1000==0:self.w(address,self.u(address)|2)
  if pc==0x423f28:self.boundary_events.append(['cq-init',*self.args()[:3]]);self.ret();return
  if pc==0x423fac:self.boundary_events.append(['cq-disable',self.args()[0]]);self.ret(0);return
  if pc==0x423f54:self.boundary_events.append(['cq-term',self.args()[0]]);self.ret();return
  if pc==0x41d1c0:
   self.boundary_events.append(['delay-argument',self.args()[0]])
   if self.transition_status==1:self.w(0x40021000,(self.u(0x40021000)&~0x18)|12)
   self.ret();return
  if pc==((self.symbols['opencfw_boot_dfu_runtime_enable']&~1) if self.source else 0x42ddf2):
   self.w(0x20026e40,0x08002201 if self.finish_status else 0);self.w(0x40021008,0x40000 if self.query_result else 0)
   if self.transition_status:self.cpu.mem_write(0x20000552,b'\0')
  if pc in self.executed:
   assert any(lo<=pc<hi for lo,hi in self.exec_ranges),(self.source,hex(pc),'unimplemented execution')
   if not self.source:self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
   return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);blob=v.BLOB.read_bytes();app=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';vector=app.read_bytes()[32:40];reset=struct.unpack('<2I',vector)[1]&~1;trace={};cases=[]
 for mode,ota,apply,transition,query_status,query_result,finish in [(0,0,0,0,0,0,0),(7,0,0,0,0,0,0),(0,0,0,4,0,0,0),(0,0,0,1,0,0,0),(0,0,0,0,0,1,7),(0,0,0,0,0,0,9),(0,0x55555555,0,0,0,0,0),(7,0x55555555,0,0,0,0,0)]:
  pair=[Machine(),Machine(True,segs,syms)]
  for m in pair:
   m.application_reset=reset;m.cpu.mem_map(reset&~4095,4096);m.cpu.mem_map(0x438000,4096);m.cpu.mem_write(0x438000,vector);m.cpu.mem_map(0x7fe000,4096);m.w(0x7fe000,ota);m.apply_status=apply;m.transition_status=transition;m.query_status=query_status;m.query_result=query_result;m.finish_status=finish
   if m.source:m.cpu.mem_write(v.BASE,blob[:4])
   m.stage_status={};m.init_status=0;m.read_status=0;m.mode_result=mode;m.created_handle=0x20026ac0;m.w(c.SLOT,c.SLOT_SENTINEL)
   for addr,n in c.INIT_REGIONS:m.cpu.mem_write(addr,b'\xcc'*n)
   m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob)
   for module in range(4):m.w(0x40060000+(module<<12)+0x14,0x00563412);m.w(0x40060000+(module<<12)+0x1c,1)
   try:m.drive()
   except Exception:
    print('FAILED',m.source,hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)),[(hex(x),hex(m.u(x))) for x in [0x20000474,0x20000478,0x200270dc]]);raise
  results=[dict(state=b.state(m),boundary=m.boundary_events,nor_mutex=m.u(0x200270e0),powered=m.cpu.mem_read(0x200271c6,1)[0],mspi=bytes(m.cpu.mem_read(0x40060000,0x4000)).hex(),power=bytes(m.cpu.mem_read(0x40010000,0x1000)).hex(),primask=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK)) for m in pair]
  assert results[0]==results[1],{k:[r[k] if k not in ('mspi','power') else [(i,x,y) for i,(x,y) in enumerate(zip(results[0][k],results[1][k])) if x!=y][:20] for r in results] for k in results[0] if results[0][k]!=results[1][k]}
  if not ota:assert results[0]['boundary'][-1]==['application-reset-entry',hex(reset),0x438000,struct.unpack('<I',vector[:4])[0],1]
  else:assert results[0]['state']['task_events'][-1][1]=='0x4153a4'
  trace.update(pair[0].trace);cases.append(dict(mode=mode,ota_flag=hex(ota),power_object_null=True,transition_status=transition,query_result=query_result,finish_status=finish,boundary=results[0]['boundary'],task_events=results[0]['state']['task_events']))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,application_sha256=v.sha(app),elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for folder in ['startup','thread_creation','manager_task','flags_runtime','clock_manager','dfu_task','update_core','filesystem','platform_control','nor_init','nor_mspi_init'] for p in (ROOT/'g2/components/bootloader'/folder).iterdir() if p.is_file() and p.suffix in ['.c','.h','.S','.ld','.py']},original_trace=trace,comparisons=cases,limits=['Basic exceptions modeled by inherited bridge. Source machine never loads stock executable code; authenticated inputs are initialSP4B, compressedinitializer695B, applicationvector8B. Runtime registerIDs/values are reconstructed C scalar data at their original addresses.','Actual source runtime-enable/critical-save/mode-one register updates/mode-two/cleanup and vector handoff execute. Power-apply executes its original/source null-object rejection (returns2) because the earlier platform-init cut leaves its object null. Valid-object configuration remains unexecuted external code; actual transition/query/optional-hook dispatch execute. One case forces saved-mode0 and models mode acknowledgement during delay; another forces saved-mode0 with no acknowledgement, proving actual20-delay timeout4 is ignored by runtime-enable. Query tests use real descriptor20 MMIOmask40000. Optional finish callback and delay remain observed cuts. Runtime-enable ignores their failures; handoff continues with PRIMASK1. Application executable code does not run.','Actual NOR static mutex construction/power bookkeeping and MSPI enable/disable/deinit/interrupt/NVIC/PRIMASK providers execute. Actual HALconfigure writes canonical module state, configured byte and TCB settings; CQ downstream callbacks remain cuts. Actual blocking transfer control/IRQ save-restore executes, including real source FIFO byte movement and status polling; synthetic ports hold RXword00563412/count1, TXstatus0, and command-complete bit2 is asserted at final poll. This is modeled peripheral progress; CQ callbacks, delay and hardware MMIO behavior remain external.','Update branch still stops before file-open4153a4. No filesystem state or firmware programming/hardware boot/byte identity is proved.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
