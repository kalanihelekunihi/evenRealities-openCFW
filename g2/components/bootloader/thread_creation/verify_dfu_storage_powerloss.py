#!/usr/bin/env python3
"""Synthetic stop/reboot before/after an atomic modeled MRAM page call.

This models persisted bytes at software boundaries, not brownout behavior or
partial ROM transactions. Source/stock reset and update instructions execute.
"""
import argparse,importlib.util,json,struct,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('platform_profile',HERE/'verify_dfu_storage_platform.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.LOCAL_PROVIDERS={'opencfw_boot_coprocessor_enable':0x41ac44,'opencfw_boot_fp_lazy_mode':0x41ac5a,'opencfw_boot_delay_scaled':0x41f9d8,'opencfw_boot_delay_raw':0x41f9e6};s=p.s;v=p.v;c=s.c
class Machine(p.Machine):
 def __init__(self,*a,interrupt=None,**kw):super().__init__(*a,**kw);self.power_cut_phase=interrupt;self.interrupted=False
 def code(self,uc,pc,size,user):
  if pc==0x0200ff20 and self.power_cut_phase is not None:
   key,operation,address,offset=self.args();destination=0x400000+4*offset
   if destination==0x438000:
    if self.power_cut_phase=='after':super().code(uc,pc,size,user)
    self.interrupted=True;self.boundary_events.append(['synthetic-power-cut',self.power_cut_phase]);self.stop('dfu-dispatch-boundary');return
  super().code(uc,pc,size,user)
def setup(m,disk,blob,reset,application,flag):
 m.cpu.mem_write(s.NOR,disk);m.application_reset=reset;m.cpu.mem_map(reset&~4095,4096);m.cpu.mem_map(0x438000,4096);m.cpu.mem_write(0x438000,application);m.cpu.mem_map(0x7fe000,4096);m.cpu.mem_write(0x7fe000,flag);m.apply_status=0;m.transition_status=0;m.query_status=0;m.query_result=0;m.finish_status=0
 if m.source:m.cpu.mem_write(v.BASE,blob[:4])
 m.stage_status={};m.init_status=0;m.read_status=0;m.mode_result=0;m.created_handle=0x20026ac0;m.w(c.SLOT,c.SLOT_SENTINEL)
 for address,size in c.INIT_REGIONS:m.cpu.mem_write(address,b'\xcc'*size)
 m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob)
 for module in range(4):m.w(0x40060000+(module<<12)+0x14,0x00563412);m.w(0x40060000+(module<<12)+0x1c,1)
def persistent(m):return bytes(m.cpu.mem_read(s.NOR,s.SIZE)),bytes(m.cpu.mem_read(0x438000,4096)),bytes(m.cpu.mem_read(0x7fe000,4096))
def record(m):
 disk,app,flag=persistent(m);writes=m.canonical_peripheral_writes()
 return dict(source=m.source,raw_peripheral_write_sha256=hashlib.sha256(json.dumps(m.peripheral_writes,separators=(',',':')).encode()).hexdigest(),initializer_sort_comparator_visits=p.initv.split_initializer_native_visits(getattr(m,'initializer_visits',{}))[1],raw_nor_transport=m.nor_transport,reason=getattr(m,'reason',None),nor_sha256=hashlib.sha256(disk).hexdigest(),application_page_sha256=hashlib.sha256(app).hexdigest(),flag_page_sha256=hashlib.sha256(flag).hexdigest(),ota_flag=flag[:4].hex(),application_prefix=app[:32].hex(),interrupted=m.interrupted,boundary=m.boundary_events,task_events=getattr(m,'task_events',[]),file_calls=getattr(m,'file_calls',[]),nor_transport=m.canonical_nor_transport(),nor_native_visits=getattr(m,'nor_native_visits',{}),kernel_state_native_visits=m.kernel_state_native_visits,initializer_events=p.initv.normalize_initializer_events(getattr(m,'initializer_events',[])),initializer_native_visits=p.initv.split_initializer_native_visits(getattr(m,'initializer_visits',{}))[0],initializer_table=getattr(m,'normalized_init_table',None),initializer_state=p.initializer_state(m),peripheral_write_count=len(writes),peripheral_write_sha256=hashlib.sha256(json.dumps(writes,separators=(',',':')).encode()).hexdigest())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--seed-elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segments,syms=v.elf.elf_info(args.elf);p.configure_profiles(syms)
 # Keep legacy snapshots reproducible. A source image opts into these native
 # bodies only when the corresponding implementation symbol is present.
 if 'opencfw_boot_device_info_query' in syms:
  p.NATIVE_DEVICE_INFO=True;p.NATIVE_DELAY_MATH=True;p.LOCAL_PROVIDERS['opencfw_boot_delay_us_math']=0x41d1c0
 if 'opencfw_boot_icache_enable' in syms:p.LOCAL_PROVIDERS.update(opencfw_boot_icache_enable=0x41e1e8,opencfw_boot_dcache_enable=0x41e266,opencfw_read_mspi_register_id=0x41d90e)
 if 'opencfw_publish_mspi_mode' in syms:p.LOCAL_PROVIDERS['opencfw_publish_mspi_mode']=0x41fadc
 blob=v.BLOB.read_bytes();app=s.ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';vector=app.read_bytes()[32:40];reset=struct.unpack('<2I',vector)[1]&~1;disk,image,seedhash=s.create_disk(args.seed_elf,vector);trace={};cases=[]
 for phase in ['before','after']:
  first=[Machine(False,interrupt=phase),Machine(True,segments,syms,interrupt=phase)]
  for m in first:setup(m,disk,blob,reset,vector.ljust(4096,b'\0'),(0x55555555).to_bytes(4,'little').ljust(4096,b'\0'));m.drive();assert m.interrupted
  records=[record(m) for m in first]
  assert records[0]['nor_sha256']==records[1]['nor_sha256'] and records[0]['application_page_sha256']==records[1]['application_page_sha256'] and records[0]['flag_page_sha256']==records[1]['flag_page_sha256'],(phase,records)
  assert records[0]['ota_flag']=='55555555'
  second=[Machine(False),Machine(True,segments,syms)]
  reboot_runs=[]
  for m,previous in zip(second,first):
   saved=persistent(previous);setup(m,saved[0],blob,reset,saved[1],saved[2])
   try:m.drive();error=None
   except Exception as exc:error=f'{type(exc).__name__}: {exc}'
   run=record(m);run['exception']=error;run['application_reset_reached']=bool(m.boundary_events and m.boundary_events[-1][0]=='application-reset-entry');run['application_payload_matches_fixture']=bytes(m.cpu.mem_read(0x438000,256))==image[32:];reboot_runs.append(run)
  restarted=reboot_runs
  def observable_record(x):
   return {key:value for key,value in x.items() if key not in ('source','raw_peripheral_write_sha256','initializer_sort_comparator_visits','raw_nor_transport')}
  stopped_match=observable_record(records[0])==observable_record(records[1])
  reboot_match=observable_record(restarted[0])==observable_record(restarted[1])
  def persisted_signature(x):return (x['nor_sha256'],x['application_page_sha256'],x['flag_page_sha256'],x['ota_flag'])
  assert persisted_signature(restarted[0])==persisted_signature(restarted[1]),(phase,restarted)
  for m in first+second:
   if not m.source:trace.update(m.trace)
  cases.append(dict(interruption=phase,stopped_stock=records[0],stopped_source=records[1],stopped_persistence_match=persisted_signature(records[0])==persisted_signature(records[1]),stopped_observable_match=stopped_match,reboot_stock=restarted[0],reboot_source=restarted[1],reboot_persistence_match=persisted_signature(restarted[0])==persisted_signature(restarted[1]),reboot_observable_match=reboot_match))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 matched=all(c['stopped_persistence_match'] and c['reboot_persistence_match'] and c['stopped_observable_match'] and c['reboot_observable_match'] for c in cases)
 report=dict(status='PASS' if matched else 'PARTIAL',cases=len(cases),stock_source_full_observable_match=matched,distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(args.elf),seed_elf_sha256=seedhash,source_sha256={str(Path(__file__).relative_to(s.ROOT)):v.sha(Path(__file__))},comparisons=cases,original_trace=trace,limits=['Synthetic persistence retains NOR, the full application page and flag page; other SRAM/MMIO resets. Cuts occur immediately before or after a modeled atomic ROM page write. No partial write, silicon reset, brownout, real page atomicity, cache visibility, physical recovery or cancellation proof.','Same generated 288-byte update as normal integration. Stock/source stop and reboot records compare all recorded observable state (persistent pages, task events, file calls, ordered boundaries, peripheral writes and exception/endpoint state), excluding the source-identification boolean and separately retained raw FIFO-padding/unused-comparator diagnostics. Initializer event registers outside proven ABI arguments and sorting comparator invocation counts are diagnostic rather than semantic equality; normalized callback tables and state compare. Peripheral comparison follows the explicitly recorded shared-profile recorded FIFO-padding boundary. Recovery is measured from the resulting endpoint; application handoff is not required as an assumption. No actual application instructions execute.'])
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
