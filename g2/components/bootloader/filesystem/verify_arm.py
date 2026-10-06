#!/usr/bin/env python3
"""Execute real ARM-compiled littlefs + source glue over a synthetic NOR.
This is source integration execution, not original/full-firmware equivalence.
"""
import argparse, importlib.util, json, struct, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('boot_update_verifier',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
NOR=0x01400000;SIZE=3008*4096;FS=0x20026878;FILE=0x20006000;PATH=0x20008000;READOUT=0x20009000;IMAGE=0x20010000
PROVIDERS={0x41552c:'alloc',0x415558:'free',0x4166aa:'lock',0x416710:'unlock',0x420f70:'nor_read',0x420b0c:'nor_prog',0x420a08:'nor_erase',0x415fae:'error',0x4176ce:'log',0x41e348:'runtime'}
class Source(v.Machine):
 def __init__(self,segments,symbols,real_allocator=False,real_queue=False,real_queue_runtime=False,real_nor_read=False,real_mutex=False):
  super().__init__(True,segments,symbols);self.cpu.mem_map(NOR,SIZE);self.cpu.mem_write(NOR,b'\xff'*SIZE);self.cpu.mem_map(0x21000000,0x200000);self.heap=0x21000000;self.provider_counts={k:0 for k in list(PROVIDERS.values())+['image_erase','image_read','image_program']};self.runs=[]
  self.real_allocator=real_allocator;self.real_queue=real_queue;self.real_queue_runtime=real_queue_runtime;self.task_messages=[];self.queue_kernel_calls=0
  if real_queue_runtime:self.w(0x20027150,0);self.w(0x2002716c,0)
  self.real_nor_read=real_nor_read;self.nor_pio_calls=0
  self.real_mutex=real_mutex;self.mutex_kernel_calls={'take':0,'give':0}
  if real_nor_read:self.w(0x200270dc,0x72)
  self.w(0x2002712c,0x51)
  if real_allocator:self.cpu.mem_map(0x20040000,0xc0000);self.w(0x20027130,0x61)
 def code(self,uc,pc,size,_):
  if self.real_mutex:
   if pc==(self.symbols['opencfw_boot_mutex_acquire']&~1):self.provider_counts['lock']+=1
   if pc==(self.symbols['opencfw_boot_mutex_release']&~1):self.provider_counts['unlock']+=1
   if pc in [0x419e22,0x41a24e]:
    r0,r1,r2,r3=self.args();assert r0 in [0x50,0x60] and r1==1000
    self.mutex_kernel_calls['take']+=1;self.ret(1);return
   if pc in [0x419de2,0x419ec0]:
    r0,r1,r2,r3=self.args();assert r0 in [0x50,0x60]
    if pc==0x419ec0:assert r1==r2==r3==0
    self.mutex_kernel_calls['give']+=1;self.ret(1);return
  if self.real_nor_read:
   if pc==(self.symbols['opencfw_boot_nor_read']&~1):self.provider_counts['nor_read']+=1
   if pc in [0x41ff08,0x420e8c,0x4207f4,0x41ff1e]:self.ret();return
   if pc==0x4262e0:
    handle,command,timeout,_arg=self.args();assert handle==0x72 and timeout==1000000
    raw=bytes(self.cpu.mem_read(command,24));length=self.u(command);address=self.u(command+8);buffer=self.u(command+20)
    assert raw[4:8]==b'\0\0\0\x01' and raw[12:20]==b'\x01\0\x6c\0\x01\0\0\0'
    assert NOR<=address<=address+length<=NOR+SIZE
    self.cpu.mem_write(buffer,bytes(self.cpu.mem_read(address,length)));self.nor_pio_calls+=1;self.ret();return
  if self.real_queue and pc==0x418b56:
   assert not self.real_queue_runtime,'Runtime query still intercepted'
   self.ret(1);return
  if self.real_queue and pc==0x41a114:
   r0,r1,r2,r3=self.args();assert r0==0x62 and r2==0
   self.queue_kernel_calls+=1
   if self.task_messages:self.cpu.mem_write(r1,struct.pack('<10I',self.task_messages.pop(0),*([0]*9)));self.ret(1)
   else:self.ret(0)
   return
  if pc==0x416920:
   assert not self.real_queue,'Wrapper still intercepted in real-queue profile'
   r0,r1,r2,r3=self.args();assert r0==0x62 and r2==0 and r3==0
   if self.task_messages:self.cpu.mem_write(r1,struct.pack('<10I',self.task_messages.pop(0),*([0]*9)));self.ret()
   else:self.ret(1)
   return
  if pc==0x42ddf2:self.events.append(['dfu_runtime_enable_synthetic']);self.ret();return
  if pc==0x42de0e:raise AssertionError('Unexpected DFU terminal error boundary')
  if pc==0x08002120:self.provider_counts['log']+=1;self.ret();return
  if self.real_allocator:
   if pc==(self.symbols['opencfw_boot_fs_alloc']&~1):self.provider_counts['alloc']+=1
   if pc==(self.symbols['opencfw_boot_fs_free']&~1):self.provider_counts['free']+=1
   if pc==0x08002100:self.provider_counts['log']+=1;self.ret();return
   if pc==0x08002110:raise AssertionError('Unexpected allocator diagnostic')
  if pc in [v.ERASE,v.READ,v.PROGRAM]:
   self.provider_counts[{v.ERASE:'image_erase',v.READ:'image_read',v.PROGRAM:'image_program'}[pc]]+=1;super().code(uc,pc,size,_);return
  if pc in PROVIDERS:
   k=PROVIDERS[pc];self.provider_counts[k]+=1;r0,r1,r2,r3=self.args()
   if k=='alloc':
    n=(r0+7)&~7;at=self.heap;self.heap+=n;assert self.heap<=0x21200000;self.cpu.mem_write(at,b'\0'*n);self.ret(at)
   elif k in ['free','unlock','runtime','error']:self.ret()
   elif k=='lock':assert r0 in ([0x51,0x61] if self.real_allocator else [0x51]) and r1==1000;self.ret()
   elif k=='nor_read':assert NOR<=r0<=r0+r2<=NOR+SIZE;self.cpu.mem_write(r1,bytes(self.cpu.mem_read(r0,r2)));self.ret()
   elif k=='nor_prog':
    assert NOR<=r0<=r0+r2<=NOR+SIZE;old=bytes(self.cpu.mem_read(r0,r2));new=bytes(self.cpu.mem_read(r1,r2));assert all((a&b)==b for a,b in zip(old,new));self.cpu.mem_write(r0,new);self.ret()
   elif k=='nor_erase':assert NOR<=r0<=r0+4096<=NOR+SIZE and not (r0&4095);self.cpu.mem_write(r0,b'\xff'*4096);self.ret()
   elif k=='log':self.events.append(['log',r0,self.u(uc.reg_read(v.a.UC_ARM_REG_SP))]);self.ret()
   return
  # Existing synthetic open/prepare/read/close addresses are not returning
  # providers here: source functions own those paths in this integrated ELF.
  assert pc not in v.PROVIDERS or pc in [v.RESET,v.STOP],hex(pc)
  super().code(uc,pc,size,_)
 def call(self,name,args):
  self.events=[];self.finished=False
  for reg,val in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3],args+[0]*4):self.cpu.reg_write(reg,val)
  self.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
  if len(args)>4:self.cpu.mem_write(v.SP,struct.pack('<'+'I'*(len(args)-4),*args[4:]))
  self.cpu.emu_start(self.symbols[name]|1,v.STOP+2,count=10000000);assert self.finished,(name,'execution budget');result=self.cpu.reg_read(v.a.UC_ARM_REG_R0);self.runs.append([name,args,result]);return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--real-allocator',action='store_true');ap.add_argument('--real-task',action='store_true');ap.add_argument('--real-queue',action='store_true');ap.add_argument('--real-queue-runtime',action='store_true');ap.add_argument('--real-nor-read',action='store_true');ap.add_argument('--real-mutex',action='store_true');args=ap.parse_args();assert not args.real_task or args.real_allocator;assert not args.real_queue or args.real_task;assert not args.real_queue_runtime or args.real_queue;_,seg,sym=v.elf.elf_info(args.elf);assert not args.real_mutex or args.real_queue_runtime;m=Source(seg,sym,args.real_allocator,args.real_queue,args.real_queue_runtime,args.real_nor_read,args.real_mutex)
 if args.real_allocator:assert m.call('opencfw_boot_allocator_init',[])==0;assert m.u(0x2002718c)==0x20081000
 cfg=sym['opencfw_boot_lfs_config'];assert bytes(m.cpu.mem_read(cfg+20,64))==v.BLOB.read_bytes()[0x21084:0x210c4]
 assert m.call('lfs_format',[FS,cfg])==0;assert m.call('lfs_mount',[FS,cfg])==0;m.cpu.mem_write(PATH,b'ota\0');assert m.call('lfs_mkdir',[FS,PATH])==0
 image=bytearray(9033)
 for i in range(32,len(image)):image[i]=(i*37)&255
 image[0:4]=struct.pack('<I',len(image)|(1<<26 if args.real_task else 0));image[20:24]=struct.pack('<I',v.FLASH);image[4:8]=struct.pack('<I',v.zlib.crc32(image[8:]))
 m.cpu.mem_write(PATH,b'ota/s200_firmware_ota.bin\0');m.cpu.mem_write(IMAGE,bytes(image));assert m.call('lfs_file_open',[FS,FILE,PATH,0x502])==0;assert m.call('lfs_file_write',[FS,FILE,IMAGE,len(image)])==len(image);assert m.call('lfs_file_close',[FS,FILE])==0
 m.cpu.mem_write(v.HEADER,bytes(image[:32]));result=m.call('opencfw_boot_verify',[v.HANDLE,v.HEADER]);assert result==1;assert m.u(v.HANDLE)==0
 # Remount proves the bytes are read through metadata/block callbacks, not a
 # synthetic file provider returning preselected data.
 assert m.call('lfs_unmount',[FS])==0;m.cpu.mem_write(FS,b'\0'*256);assert m.call('lfs_mount',[FS,cfg])==0
 assert m.call('opencfw_boot_verify',[v.HANDLE,v.HEADER])==1
 m.call('opencfw_boot_program',[v.HANDLE,v.HEADER]);assert m.u(v.HANDLE)==0;assert bytes(m.cpu.mem_read(v.FLASH,len(image)-32))==image[32:]
 m.call('opencfw_boot_file_open',[sym['opencfw_boot_update_path'],0x42dad8]);handle=m.runs[-1][2];assert handle
 assert m.call('opencfw_boot_file_prepare',[handle,32,0])==0;assert m.call('opencfw_boot_file_read',[READOUT,1,9001,handle])==9001;assert bytes(m.cpu.mem_read(READOUT,9001))==image[32:];assert m.call('opencfw_boot_file_close',[handle])==0;assert m.call('lfs_unmount',[FS])==0
 if args.real_allocator:assert m.call('tlsf_check',[0x20081000])==0
 task_observation=None
 if args.real_task:
  assert m.call('lfs_mount',[FS,cfg])==0
  if args.real_queue:
   m.cpu.mem_write(READOUT,b'\xa5'*40)
   assert m.call('opencfw_bl_queue_get',[0x62,READOUT,0,0])==0xfffffffd
   assert bytes(m.cpu.mem_read(READOUT,40))==b'\xa5'*40
  m.cpu.mem_map(0x438000,4096);m.w(0x438000,0x2007fb00);m.w(0x438004,v.RESET|1);m.w(0x200004d8,0x62);m.task_messages=[1]
  m.call('opencfw_boot_dfu_task',[])
  assert ['handoff',0x438000,0x2007fb00,v.RESET] in m.events,m.events
  assert bytes(m.cpu.mem_read(v.FLASH,len(image)-32))==image[32:]
  assert m.u(0x20027174)==0 and m.u(0x20026ef8+20)==0x438000
  task_observation={'events':m.events,'destination':m.u(0x20026ef8+20),'handle':m.u(0x20027174),'real_architectural_handoff':True}
 sources=[p for root in ['filesystem','update_core']+(['dfu_task'] if args.real_task else [])+(['allocator'] if args.real_allocator else [])+(['queue'] if args.real_queue else [])+(['nor_read'] if args.real_nor_read else []) for p in (ROOT/'g2/components/bootloader'/root).rglob('*') if p.suffix in ['.c','.h','.py','.S','.ld'] or p.name=='Makefile']
 d={'status':'PASS','real_source_mutex_wrappers':args.real_mutex,'mutex_kernel_calls':m.mutex_kernel_calls,'real_source_nor_read':args.real_nor_read,'nor_pio_calls':m.nor_pio_calls,'real_source_queue_runtime':args.real_queue_runtime,'real_source_queue_wrapper':args.real_queue,'queue_kernel_calls':m.queue_kernel_calls,'real_task_observation':task_observation,'real_source_allocator':args.real_allocator,'source_sha256':{str(p.relative_to(ROOT)):v.sha(p) for p in sources},'calls':m.runs,'provider_counts':m.provider_counts,'source_elf_sha256':v.sha(args.elf),'recovered_numeric_config_64_bytes_match':True,'image_bytes':len(image),'limits':['Real ARM source littlefs, file wrappers, image verification and update loop execute. Heap is real pinned TLSF only when real_source_allocator is true; mutex wrappers execute when real_source_mutex_wrappers is true, with kernel take/give providers synthetic; image erase/program/readback providers remain synthetic.','NOR is an offline byte model with one-to-zero program checks; real-nor-read profile executes the stock read-command source but setup/teardown and lower HAL remain synthetic, not silicon timing/coherence/power-loss behavior.','No original end-to-end bootloader comparison, exact IAR ABI/build or hardware bootability claim.','This candidate littlefs profile disables diagnostic/assert macros; exact stock configuration beyond recovered struct is unverified.','DFU task instructions execute only in real-task profile; queue wrappers execute only in real-queue profile with kernel receive providers synthetic; runtime-mode query executes when real-source-queue-runtime is enabled. No RTOS task scheduling, IRQ/SBL/ROM/flash driver execution or firmware writes.']};args.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':d['status'],'calls':len(m.runs),'provider_counts':m.provider_counts},indent=2))
if __name__=='__main__':main()
