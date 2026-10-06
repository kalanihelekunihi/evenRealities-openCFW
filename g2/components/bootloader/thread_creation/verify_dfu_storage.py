#!/usr/bin/env python3
"""Scheduler-driven reset -> mounted source littlefs -> DFU read/verify/program/handoff.
NOR and installed application are synthetic RAM. No device image/flash operation.
"""
import argparse,importlib.util,json,struct,hashlib,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('runtime',HERE/'verify_dfu_runtime.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);v=r.v;c=r.c
spec=importlib.util.spec_from_file_location('armfs',ROOT/'g2/components/bootloader/filesystem/verify_arm.py');fs=importlib.util.module_from_spec(spec);spec.loader.exec_module(fs)
NOR=fs.NOR;SIZE=fs.SIZE
FILES={'opencfw_provider_421210':0x421210,'opencfw_boot_file_open':0x4153a4,'opencfw_boot_file_prepare':0x4154d2,'opencfw_boot_file_read':0x415484,'opencfw_boot_file_close':0x415446}
def create_disk(elf,vector):
 _,segs,syms=v.elf.elf_info(elf);m=fs.Source(segs,syms);cfg=syms['opencfw_boot_lfs_config'];image=bytearray(32+256);image[32:40]=vector
 for i in range(40,len(image)):image[i]=(i*37)&255
 struct.pack_into('<I',image,0,len(image)|(1<<26));struct.pack_into('<I',image,20,0x438000);struct.pack_into('<I',image,4,zlib.crc32(image[8:]));m.cpu.mem_write(fs.PATH,b'ota\0');assert m.call('lfs_format',[fs.FS,cfg])==0;assert m.call('lfs_mount',[fs.FS,cfg])==0;assert m.call('lfs_mkdir',[fs.FS,fs.PATH])==0;m.cpu.mem_write(fs.PATH,b'ota/s200_firmware_ota.bin\0');m.cpu.mem_write(fs.IMAGE,bytes(image));assert m.call('lfs_file_open',[fs.FS,fs.FILE,fs.PATH,0x502])==0;assert m.call('lfs_file_write',[fs.FS,fs.FILE,fs.IMAGE,len(image)])==len(image);assert m.call('lfs_file_close',[fs.FS,fs.FILE])==0;assert m.call('lfs_unmount',[fs.FS])==0
 return bytes(m.cpu.mem_read(NOR,SIZE)),bytes(image),v.sha(elf)
class Machine(r.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.storage=True;self.executed.update((self.symbols[n]&~1) if self.source else address for n,address in FILES.items());self.cpu.mem_map(NOR,SIZE);self.storage_counts=dict(read=0,program=0,erase=0,image_erase=0,image_read=0,image_program=0);self.file_calls=[]
 def code(self,uc,pc,size,user):
  if pc in (0x4166aa,0x416710):
   if pc==0x4166aa:assert self.args()[1]==1000
   self.ret(0);return
  if pc==0x42de0e:self.boundary_events.append(['dfu-error-before-mram']);self.stop('dfu-dispatch-boundary');return
  if pc==0x41f846:
   # Explicit fixture contract for the still-unclosed platform descriptor.
   desc=0x20003000;self.w(0x200004f0,desc);self.w(desc+4,4096);self.w(desc+0x18,v.READ|1);self.w(desc+0x1c,v.PROGRAM|1);self.w(desc+0x20,v.ERASE|1)
  if pc in (0x420f70,0x420b0c,0x420a08):
   address,data,size,_=self.args();key={0x420f70:'read',0x420b0c:'program',0x420a08:'erase'}[pc];self.storage_counts[key]+=1
   if pc==0x420f70:assert NOR<=address<=address+size<=NOR+SIZE;uc.mem_write(data,bytes(uc.mem_read(address,size)))
   elif pc==0x420b0c:
    assert NOR<=address<=address+size<=NOR+SIZE;old=bytes(uc.mem_read(address,size));new=bytes(uc.mem_read(data,size));assert all((x&y)==y for x,y in zip(old,new));uc.mem_write(address,new)
   else:assert NOR<=address<=address+4096<=NOR+SIZE and address%4096==0;uc.mem_write(address,b'\xff'*4096)
   self.ret();return
  if pc in (v.ERASE,v.READ,v.PROGRAM):
   address,data,size,_=self.args();key={v.ERASE:'image_erase',v.READ:'image_read',v.PROGRAM:'image_program'}[pc];self.storage_counts[key]+=1
   if pc==v.ERASE:assert address==0x438000;uc.mem_write(address,b'\xff'*4096)
   elif pc==v.READ:assert 0x438000<=data<=data+size<=0x439000;uc.mem_write(address,bytes(uc.mem_read(data,size)))
   else:assert 0x438000<=address<=address+size<=0x439000;uc.mem_write(address,bytes(uc.mem_read(data,size)))
   self.ret();return
  if pc==0x41e348:self.boundary_events.append(['runtime-update',*self.args()[:2]]);self.ret();return
  if pc==0x415fae and self.args()[0] not in (0x43198c,0x431468,0x431420):self.ret();return
  if pc==0x4176ce and self.args()[1]==0x433fe0:
   # update_core's fixed task.dfu tag is not materialized in the bounded
   # source ELF. Capture the same logger ABI by its authenticated address.
   self.task_events.append(['dfu-log',self.args()[0],self.u(uc.reg_read(v.a.UC_ARM_REG_SP))]);self.ret();return
  if pc==0x4176ce and self.cstr(self.args()[1])=='file_system':self.ret();return
  for name,address in FILES.items():
   entry=(self.symbols[name]&~1) if self.source else address
   if pc==entry:
    args=self.args();self.file_calls.append([name,self.cstr(args[0]),self.cstr(args[1])] if name=='opencfw_boot_file_open' else [name])
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--seed-elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segs,syms=v.elf.elf_info(a.elf);blob=v.BLOB.read_bytes();app=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';vector=app.read_bytes()[32:40];disk,image,seedhash=create_disk(a.seed_elf,vector);reset=struct.unpack('<2I',vector)[1]&~1;trace={};cases=[]
 for ota in [0,0x55555555]:
  pair=[Machine(),Machine(True,segs,syms)]
  for m in pair:
   m.cpu.mem_write(NOR,disk);m.application_reset=reset;m.cpu.mem_map(reset&~4095,4096);m.cpu.mem_map(0x438000,4096);m.cpu.mem_write(0x438000,vector);m.cpu.mem_map(0x7fe000,4096);m.w(0x7fe000,ota);m.apply_status=0;m.transition_status=0;m.query_status=0;m.query_result=0;m.finish_status=0
   if m.source:m.cpu.mem_write(v.BASE,blob[:4])
   m.stage_status={};m.init_status=0;m.read_status=0;m.mode_result=0;m.created_handle=0x20026ac0;m.w(c.SLOT,c.SLOT_SENTINEL)
   for addr,n in c.INIT_REGIONS:m.cpu.mem_write(addr,b'\xcc'*n)
   m.cpu.reg_write(v.a.UC_ARM_REG_R9,0);c.seed_source_inputs(m,blob)
   for module in range(4):m.w(0x40060000+(module<<12)+0x14,0x00563412);m.w(0x40060000+(module<<12)+0x1c,1)
   try:m.drive()
   except Exception:print('FAILED',m.source,hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)));raise
  results=[dict(task=r.b.state(m),boundary=m.boundary_events,files=m.file_calls,ready=m.u(0x2002711c),file_handle=m.u(0x20027174),nor_sha=hashlib.sha256(m.cpu.mem_read(NOR,SIZE)).hexdigest(),application=bytes(m.cpu.mem_read(0x438000,256)).hex(),counts=m.storage_counts) for m in pair]
  assert results[0]==results[1],{k:[x[k] for x in results] for k in results[0] if results[0][k]!=results[1][k]}
  assert results[0]['ready']==1 and results[0]['boundary'][-1][0]=='application-reset-entry'
  if ota:assert bytes(pair[0].cpu.mem_read(0x438000,256))==image[32:] and results[0]['file_handle']==0 and results[0]['counts']['image_program']>0
  trace.update(pair[0].trace);cases.append(dict(ota_flag=hex(ota),result=results[0]))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,application_sha256=v.sha(app),elf_sha256=v.sha(a.elf),seed_elf_sha256=seedhash,seed_nor_sha256=hashlib.sha256(disk).hexdigest(),synthetic_update_sha256=hashlib.sha256(image).hexdigest(),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for folder in ['thread_creation','filesystem','filesystem/upstream','platform_control','nor_mspi_init','nor_init','update_core','dfu_task'] for p in (ROOT/'g2/components/bootloader'/folder).iterdir() if p.is_file() and p.suffix in ['.c','.h','.S','.ld','.py']},original_trace=trace,comparisons=cases,limits=['Inherited basic-exception and MMIO model. Stock/source reset, mount/directory/boot_count, scheduler/manager/DFU, real littlefs/file wrappers/TLSF, update verify/program/control and architectural handoff execute; application code stops before its first instruction.','Synthetic source-created NOR contains a 288-byte test update whose payload starts with the authenticated vector and then generated pattern. This is not an installed filesystem or official runnable firmware.','Storage NOR read/program/erase and application image erase/read/program remain exact-address synthetic byte callbacks, with NOR1-to0 checks; no physical writes or peripheral coherence/power-loss claim. NOR startup uses actual MSPI/FIFO/status-poll source with modeled port progress.','Platform descriptor supplied by fixture, filesystem/allocator mutex providers and runtime-update call remain synthetic. Filesystem logger adapter omitted from behavioral equality; direct boot-mount error case records its known extra callback.','No complete source closure, byte identity, SBL/ROM or hardware boot.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
