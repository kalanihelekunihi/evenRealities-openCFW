#!/usr/bin/env python3
"""Original-instruction differential; termination remains an explicit call cut."""
from pathlib import Path
import hashlib,json,struct,importlib.util,argparse
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[6]
P=Path(__file__).parent
image=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
blob=image.read_bytes(); sha=hashlib.sha256(blob).hexdigest()
assert sha=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec=importlib.util.spec_from_file_location('er',ROOT/'g2/components/bootloader/update_core/elf_reader.py');er=importlib.util.module_from_spec(spec);spec.loader.exec_module(er)
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path);args=ap.parse_args()
elf=args.elf or ROOT/'g2/build/bootloader-completion/initialized-teardown/2d35a0b0b1d6663417cd4bfa42b09cc1326fea5b405221becaec59fc2e43a533/addon.elf';_,segments,symbols=er.elf_info(elf)
coverage={};rows=[]
for name,start,end,handle,table in [('dfu',0x42ddda,0x42ddf2,0x200004d4,0x200004d0),('manager',0x42e3ca,0x42e3e0,0x200004fc,0x200004f8)]:
 coverage[name]=set()
 for value in [0,1,0x20001234,0xffffffff]:
  for status in [0,0xfffffffd,0x777]:
   for changed in [False,True]:
    results=[]
    for stock in [True,False]:
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x30000,0x10000);u.mem_map(0x410000,0x30000);u.mem_map(0x20000000,0x40000)
     if stock:u.mem_write(0x410000,blob)
     else:
      for s in segments:
       if s['data']:u.mem_write(s['address'],s['data'])
     u.mem_write(handle,struct.pack('<I',value));calls=[];writes=[]
     u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x3f001);u.reg_write(UC_ARM_REG_R4,0xabcdef01);u.reg_write(UC_ARM_REG_PRIMASK,1)
     def code(uc,a,size,_):
      if stock and start<=a<end:coverage[name].update(range(a,a+size))
      if a==0x3f000:uc.emu_stop();return
      if a==0x416200:
       calls.append(uc.reg_read(UC_ARM_REG_R0))
       if changed:uc.mem_write(handle,struct.pack('<I',0x12345678))
       uc.reg_write(UC_ARM_REG_R0,status);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if not stock and 0x410000<=a<0x440000:raise AssertionError(hex(a))
     def write(uc,access,a,size,v,_):
      if a==handle:writes.append([a,size,v])
     u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
     entry=start if stock else symbols['opencfw_boot_'+name+'_thread_deinit']
     u.emu_start(entry|1,0x3f000,count=1000)
     assert u.reg_read(UC_ARM_REG_PC)==0x3f000
     results.append(dict(calls=calls,writes=writes,handle=struct.unpack('<I',u.mem_read(handle,4))[0],r0=u.reg_read(UC_ARM_REG_R0),r4=u.reg_read(UC_ARM_REG_R4),sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK)))
    assert results[0]==results[1],(name,value,status,changed,results)
    rows.append(dict(name=name,handle=value,termination_status=status,termination_mutates_handle=changed,result=results[0]))
body={name:dict(start=hex(start),end_exclusive=hex(end),sha256=hashlib.sha256(blob[start-0x410000:end-0x410000]).hexdigest(),visited_bytes=len(coverage[name]),extent_bytes=end-start) for name,start,end in [('dfu',0x42ddda,0x42ddf2),('manager',0x42e3ca,0x42e3e0)]}
out=dict(status='PASS',cases=len(rows),image_sha256=sha,addon_elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),coverage=body,comparisons=rows,limits=['External target416200 (inherited termination label unverified) is an explicit call cut with controlled return and optional handle mutation; no real termination, scheduler, cancellation or quiescence proof.','Only wrapper behavior and stored-handle clearing established; not integrated into frozen4b candidate.'])
(P/'comparison.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),body)
