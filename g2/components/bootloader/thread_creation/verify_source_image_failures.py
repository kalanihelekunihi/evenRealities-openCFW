#!/usr/bin/env python3
"""Malformed updates on the same native source image as normal/update tests."""
import argparse,importlib.util,json,hashlib,struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('platform_profile',HERE/'verify_dfu_storage_platform.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.LOCAL_PROVIDERS={'opencfw_boot_coprocessor_enable':0x41ac44,'opencfw_boot_fp_lazy_mode':0x41ac5a,'opencfw_boot_delay_scaled':0x41f9d8,'opencfw_boot_delay_raw':0x41f9e6,'opencfw_boot_delay_us_math':0x41d1c0,'opencfw_boot_icache_enable':0x41e1e8,'opencfw_boot_dcache_enable':0x41e266,'opencfw_read_mspi_register_id':0x41d90e,'opencfw_publish_mspi_mode':0x41fadc};p.NATIVE_DELAY_MATH=True;p.NATIVE_DEVICE_INFO=True;s=p.s;v=p.v;c=s.c
spec=importlib.util.spec_from_file_location('failure_fixture',HERE/'verify_dfu_storage_failures.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class Machine(p.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.cpu.mem_map(0x40000000,0x1000);self.in_failure=False;self.reset_observed=False;self.cleanup=[];self.failure_entry=(self.symbols['opencfw_boot_dfu_error_transaction']&~1) if self.source else 0x42de0e;self.terminal_entry=(self.symbols.get('opencfw_boot_terminal_mode',0)&~1) if self.source else 0x42e4a0;self.actual_read.update(entry for entry in [self.failure_entry,self.terminal_entry] if entry)
  self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.failure_write,begin=0x40000000,end=0x40021fff)
 def failure_write(self,uc,access,address,size,value,user):
  if self.in_failure:
   if address in [0x40014008,0x40014024,0x40000008]:self.cleanup.append([address,size,value&0xffffffff])
   if address==0x40021014:self.w(0x40021018,(self.u(0x40021018)|0x80) if value&0x20 else (self.u(0x40021018)&~0x80))
 def code(self,uc,pc,size,user):
  if self.in_failure and self.u(0x40000008)==0xd4:self.reset_observed=True;self.boundary_events.append(['terminal-reset-store',0xd4,uc.reg_read(v.a.UC_ARM_REG_PRIMASK)]);self.stop('dfu-dispatch-boundary');return
  if pc==self.failure_entry:self.in_failure=True;self.w(0x200271a7,1);self.w(0x40021018,0);self.boundary_events.append(['dfu-error-transaction'])
  if pc==0x08002130 and self.in_failure:self.task_events.append(['dfu-log',*self.args()[:2]]);self.ret();return
  super().code(uc,pc,size,user)
def setup(m,disk,blob,reset,vector):
 m.cpu.mem_write(s.NOR,disk);m.application_reset=reset;m.cpu.mem_map(reset&~4095,4096);m.cpu.mem_map(0x438000,4096);m.cpu.mem_write(0x438000,vector);m.cpu.mem_map(0x7fe000,4096);m.w(0x7fe000,0x55555555);m.apply_status=0;m.transition_status=0;m.query_status=0;m.query_result=0;m.finish_status=0
 if m.source:m.cpu.mem_write(v.BASE,blob[:4])
 m.stage_status={};m.init_status=0;m.read_status=0;m.mode_result=0;m.created_handle=0x20026ac0;m.w(c.SLOT,c.SLOT_SENTINEL)
 for address,size in c.INIT_REGIONS:m.cpu.mem_write(address,b'\xcc'*size)
 m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob)
 for module in range(4):m.w(0x40060000+(module<<12)+0x14,0x00563412);m.w(0x40060000+(module<<12)+0x1c,1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--seed-elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segments,syms=v.elf.elf_info(args.elf);p.configure_profiles(syms);blob=v.BLOB.read_bytes();app=s.ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';vector=app.read_bytes()[32:40];reset=struct.unpack('<2I',vector)[1]&~1;cases=[];trace={}
 for scenario,status in [('missing-file',0),('short-header',7),('bad-crc',0x55)]:
  disk,seedhash=f.make_disk(args.seed_elf,vector,scenario);pair=[Machine(False),Machine(True,segments,syms)]
  for m in pair:setup(m,disk,blob,reset,vector);m.rom_status=status;m.drive();assert m.reset_observed
  records=[dict(boundary=m.boundary_events,files=m.file_calls,logs=m.task_events,cleanup=m.cleanup,nor_transport=m.canonical_nor_transport(),nor_native_visits=getattr(m,'nor_native_visits',{}),kernel_state_native_visits=m.kernel_state_native_visits,initializer_events=p.initv.normalize_initializer_events(getattr(m,'initializer_events',[])),initializer_native_visits=p.initv.split_initializer_native_visits(getattr(m,'initializer_visits',{}))[0],initializer_table=getattr(m,'normalized_init_table',None),initializer_state=p.initializer_state(m),flag=bytes(m.cpu.mem_read(0x7fe000,16)).hex(),nor_sha256=hashlib.sha256(m.cpu.mem_read(s.NOR,s.SIZE)).hexdigest(),peripheral_write_sha256=hashlib.sha256(json.dumps(m.canonical_peripheral_writes(),separators=(',',':')).encode()).hexdigest()) for m in pair]
  assert records[0]==records[1],(scenario,{key:[record[key] for record in records] for key in records[0] if records[0][key]!=records[1][key]})
  assert records[0]['cleanup'][-4:]==[[0x40014008,4,0xc3],[0x40014024,4,0],[0x40014008,4,0],[0x40000008,4,0xd4]]
  trace.update(pair[0].trace);cases.append(dict(scenario=scenario,synthetic_rom_status=status,result=records[0],raw_peripheral_write_sha256=[hashlib.sha256(json.dumps(m.peripheral_writes,separators=(',',':')).encode()).hexdigest() for m in pair],initializer_sort_comparator_visits=[p.initv.split_initializer_native_visits(getattr(m,'initializer_visits',{}))[1] for m in pair],raw_nor_transport=[m.nor_transport for m in pair]))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(args.elf),seed_elf_sha256=seedhash,comparisons=cases,original_trace=trace,source_sha256={str(Path(__file__).relative_to(s.ROOT)):v.sha(Path(__file__))},limits=['Same native source ELF as normal/update profile. Source machine has no stock executable image; modeled ROM writes flag only when injected status is zero. Actual guard/bridge/error/terminal instructions execute; register0xd4 observation is not silicon reset.','Malformed synthetic files only; pointer addresses of relocated source stacks are represented by ROM payload hash/arguments rather than raw equality. MMIO-only hooks, no broad RAM instrumentation. Initializer events compare only proven ABI arguments/results; sorting comparator invocation counts are diagnostic, while callback tables, semantic native-entry counts and state compare. Peripheral comparison follows the explicitly recorded shared-profile recorded FIFO-padding boundary. No physical programming, partial-write atomicity, cache coherence or hardware timing proof.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
