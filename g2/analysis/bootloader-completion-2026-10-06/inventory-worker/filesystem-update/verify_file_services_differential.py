#!/usr/bin/env python3
"""Differential stock/source littlefs mount + DFU file-wrapper fixture.

Source formats and populates a synthetic NOR image using the recovered
littlefs profile. Stock binary and compiled source independently mount the
same bytes, then open/read/seek/close the exact DFU OTA path. Only RAM allocator,
mutex calls, log output, and the low NOR transaction boundary are synthetic.
"""
import argparse, importlib.util, json, struct
from pathlib import Path
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
NOR=0x01400000; NOR_SIZE=3008*4096; FS=0x20026878
PATH=0x004336e4; MODE=0x0042dad8; FILE_BUF=0x20009000; FILE_OBJ=0x20008200
STOP=0x08000000; SP=0x2002f000

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

armfs=load('arm_filesystem_verifier',ROOT/'g2/components/bootloader/filesystem/verify_arm.py')
v=armfs.v

# The baseline updater verifier treats these entries as returning file stubs.
# Remove only those four aliases for the original machine in this process.
for addr in (0x4153a4,0x4154d2,0x415484,0x415446):v.PROVIDERS.pop(addr,None)

class Original(v.Machine):
 def __init__(self,nor_bytes):
  super().__init__();self.cpu.mem_map(NOR,NOR_SIZE);self.cpu.mem_write(NOR,nor_bytes)
  self.cpu.mem_map(0x21000000,0x200000)
  self.heap=0x21000000;self.alloc_count=0;self.free_count=0;self.locks=0;self.unlocks=0
  self.nor_counts={'read':0,'program':0,'erase':0};self.events=[]
 def code(self,uc,pc,size,user):
  if pc==0x41552c:
   size=(self.args()[0]+7)&~7;address=self.heap;self.heap+=size
   self.cpu.mem_write(address,b'\0'*size);self.alloc_count+=1;self.ret(address);return
  if pc==0x415558:self.free_count+=1;self.ret();return
  if pc==0x4166aa:
   assert self.args()[1]==1000;self.locks+=1;self.ret(0);return
  if pc==0x416710:self.unlocks+=1;self.ret();return
  if pc==0x415fae:self.ret();return
  if pc==0x420f70:
   address,out,n=self.args()[:3];assert NOR<=address<=address+n<=NOR+NOR_SIZE
   self.cpu.mem_write(out,bytes(self.cpu.mem_read(address,n)));self.nor_counts['read']+=1;self.ret();return
  if pc==0x420b0c:
   address,src,n=self.args()[:3];assert NOR<=address<=address+n<=NOR+NOR_SIZE
   old=bytes(self.cpu.mem_read(address,n));new=bytes(self.cpu.mem_read(src,n));assert all((x&y)==y for x,y in zip(old,new))
   self.cpu.mem_write(address,new);self.nor_counts['program']+=1;self.ret();return
  if pc==0x420a08:
   address=self.args()[0];assert NOR<=address<=address+4096<=NOR+NOR_SIZE and address%4096==0
   self.cpu.mem_write(address,b'\xff'*4096);self.nor_counts['erase']+=1;self.ret();return
  super().code(uc,pc,size,user)
 def call(self,address,args):
  self.events=[];self.finished=False
  for reg,val in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),args+[0]*4):self.cpu.reg_write(reg,val)
  self.cpu.reg_write(a.UC_ARM_REG_SP,SP);self.cpu.reg_write(a.UC_ARM_REG_LR,STOP|1)
  if len(args)>4:self.cpu.mem_write(SP,struct.pack('<'+'I'*(len(args)-4),*args[4:]))
  try:self.cpu.emu_start(address|1,STOP+2,count=10000000)
  except Exception:
   print('stock instruction failure',hex(address),hex(self.cpu.reg_read(a.UC_ARM_REG_PC)),self.args());raise
  assert self.finished,(hex(address),hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
  return self.cpu.reg_read(a.UC_ARM_REG_R0)

def result(machine,source):
 call=(machine.call if source else machine.call)
 def invoke(name,args,stock):
  return call(name,args) if source else call(stock,args)
 mount=invoke('lfs_mount',[FS,machine.symbols['opencfw_boot_lfs_config'] if source else 0x431070],0x415132)
 assert mount==0,('mount',mount)
 handle=invoke('opencfw_boot_file_open',[PATH,MODE],0x4153a4);assert handle
 image=bytes((i*29+11)&255 for i in range(9033))
 prep0=invoke('opencfw_boot_file_prepare',[handle,0,0],0x4154d2);assert prep0==0
 first=bytearray(32);got0=invoke('opencfw_boot_file_read',[FILE_BUF,1,32,handle],0x415484);assert got0==32
 first[:]=machine.cpu.mem_read(FILE_BUF,32)
 prep_payload=invoke('opencfw_boot_file_prepare',[handle,32,0],0x4154d2);assert prep_payload==0
 payload=bytearray(len(image)-32);got1=invoke('opencfw_boot_file_read',[FILE_BUF,1,len(payload),handle],0x415484);assert got1==len(payload)
 payload[:]=machine.cpu.mem_read(FILE_BUF,len(payload))
 invalid=invoke('opencfw_boot_file_prepare',[handle,0,3],0x4154d2)
 closed=invoke('opencfw_boot_file_close',[handle],0x415446)
 return {'mount':mount,'open_nonzero':bool(handle),'prepare_header':prep0,'header_read_count':got0,'header_hex':bytes(first).hex(),'prepare_payload':prep_payload,'payload_read_count':got1,'payload_sha256':__import__('hashlib').sha256(payload).hexdigest(),'payload_matches':bytes(payload)==image[32:],'invalid_whence':invalid,'close':closed}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 _,segments,symbols=armfs.v.elf.elf_info(args.elf)
 src=armfs.Source(segments,symbols)
 cfg=symbols['opencfw_boot_lfs_config']
 assert src.call('lfs_format',[FS,cfg])==0
 assert src.call('lfs_mount',[FS,cfg])==0
 path=0x20008000;file_path=0x20008100;data=0x20009000
 src.cpu.mem_write(path,b'ota\0');src.cpu.mem_write(file_path,b'ota/s200_firmware_ota.bin\0')
 image=bytes((i*29+11)&255 for i in range(9033));src.cpu.mem_write(data,image)
 assert src.call('lfs_mkdir',[FS,path])==0
 assert src.call('lfs_file_open',[FS,FILE_OBJ,file_path,0x502])==0
 assert src.call('lfs_file_write',[FS,FILE_OBJ,data,len(image)])==len(image)
 assert src.call('lfs_file_close',[FS,FILE_OBJ])==0
 assert src.call('lfs_unmount',[FS])==0
 # Use a clean in-memory filesystem instance in the candidate too, to model a
 # cold mount from persistent NOR instead of reusing formatted RAM state.
 nor_bytes=bytes(src.cpu.mem_read(NOR,NOR_SIZE))
 src.cpu.mem_write(FS,b'\0'*256)
 source_result=result(src,True)
 orig=Original(nor_bytes)
 stock_result=result(orig,False)
 assert stock_result==source_result,(stock_result,source_result)
 output={'status':'PASS','cases':1,'locked_image_sha256':armfs.v.SHA,'source_elf_sha256':armfs.v.sha(args.elf),'source_result':source_result,'stock_result':stock_result,'candidate_storage_calls':src.provider_counts,'stock_storage_calls':orig.nor_counts,'stock_sync_provider':'0x4213d4 returns 0; a no-op after successful synchronous NOR callbacks.','fixture_setup':'Source littlefs 2.10.1 formatted and populated an in-memory 0x01400000..0x01fbffff NOR model; the resulting bytes were independently remounted and read by original firmware and ARM-compiled source.','limits':['Stock mount entry 0x415132 executes original code against recovered lfs_config at 0x431070; NOR transactions at 0x420f70/0x420b0c/0x420a08, allocator, mutex, and logging are explicit synthetic providers.','The source side executes ARM-compiled littlefs/config/file-services; allocator/mutex and NOR read/program/erase callbacks are synthetic. Both sides share the same exact disk bytes, path 0x004336e4, and mode string 0x0042dad8 ("r+").','No boot initializer 0x421210 reformat/recovery or marker-update branch is executed by this comparison; mount is called directly on an already formatted test filesystem. No installed NOR filesystem image/device state is claimed. No physical flash or hardware interaction.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:output[k] for k in ['status','cases','stock_storage_calls']}))
if __name__=='__main__':main()
