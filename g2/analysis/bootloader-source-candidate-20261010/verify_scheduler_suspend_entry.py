#!/usr/bin/env python3
"""Bounded original/source comparison of the idle scheduler-suspend entry."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[3]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/thread_creation/scheduler_resume.c'
ENTRY=ROOT/'g2/components/bootloader/source_candidate_20261010/scheduler_suspend_entry.c'
EXPECTED_IMAGE='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
STOCK=0x4181d8
PTR=0x2002716c
reader_spec=importlib.util.spec_from_file_location('reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
reader=importlib.util.module_from_spec(reader_spec);reader_spec.loader.exec_module(reader)
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==EXPECTED_IMAGE
body=blob[STOCK-0x410000:STOCK-0x410000+12]
assert body==bytes.fromhex('dff848060168491c01607047')
assert struct.unpack_from('<I',blob,0x418824-0x410000)[0]==PTR
with tempfile.TemporaryDirectory(prefix='boot-suspend-') as d:
 p=Path(d); objs=[]
 for name,src in [('body',SOURCE),('entry',ENTRY)]:
  obj=p/(name+'.o');objs.append(obj)
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=soft','-ffreestanding','-fno-builtin','-std=c11','-O2','-ffunction-sections','-fdata-sections','-c',str(src),'-o',str(obj)],check=True,capture_output=True)
 elf=p/'source.elf'
 subprocess.run(['arm-none-eabi-ld','--gc-sections','--entry=suspend_scheduler','-Ttext=0x430000',*map(str,objs),'-o',str(elf)],check=True,capture_output=True)
 _,segments,symbols=reader.elf_info(elf)
 assert 'suspend_scheduler' in symbols and 'opencfw_bl_scheduler_suspend' in symbols
 def run(source,value,mask,r0,r1):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  for lo,size in [(0x08000000,0x1000),(0x410000,0x25000),(0x430000,0x1000),(0x20000000,0x40000)]:
   try:u.mem_map(lo,size)
   except:pass
  if source:
   for seg in segments:u.mem_write(seg['address'],seg['data'])
  else:u.mem_write(0x410000,blob)
  u.mem_write(PTR,struct.pack('<I',value))
  for reg,val in [(a.UC_ARM_REG_R0,r0),(a.UC_ARM_REG_R1,r1),(a.UC_ARM_REG_SP,0x2003f000),(a.UC_ARM_REG_LR,0x08000001),(a.UC_ARM_REG_PRIMASK,mask)]:u.reg_write(reg,val)
  for i in range(2,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0x10000000+i)
  done=[False];seen=set()
  def hook(cpu,pc,size,_):
   if pc==0x08000000:done[0]=True;cpu.emu_stop()
   if not source and STOCK<=pc<STOCK+12:seen.update(range(pc,pc+size))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(((symbols['suspend_scheduler']&~1) if source else STOCK)|1,0,count=100)
  assert done[0]
  return (struct.unpack('<I',u.mem_read(PTR,4))[0],u.reg_read(a.UC_ARM_REG_PRIMASK),u.reg_read(a.UC_ARM_REG_SP),tuple(u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(2,12))),seen
 cases=0;visited=set()
 for val in [0,1,0x7fffffff,0xffffffff]:
  for mask in [0,1]:
   for r0,r1 in [(0,0),(0x12345678,0xabcdef01)]:
    stock,trace=run(False,val,mask,r0,r1);source,_=run(True,val,mask,r0,r1)
    assert stock==source,(val,mask,r0,r1,stock,source)
    visited|=trace;cases+=1
 assert len(visited)==12
 print(json.dumps({'status':'PASS','cases':cases,'stock_body_bytes':12,'visited_stock_bytes':len(visited),'stock_body_sha256':hashlib.sha256(body).hexdigest(),'image_sha256':EXPECTED_IMAGE}))
