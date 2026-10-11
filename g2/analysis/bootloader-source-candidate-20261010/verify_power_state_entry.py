#!/usr/bin/env python3
"""Compare stock nullable power-state wrapper and selected source entry."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[3]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
BODY=ROOT/'g2/components/bootloader/initializer_callbacks/pcm22_power/spot_sleep_wrappers.c'
ENTRY=ROOT/'g2/components/bootloader/source_candidate_20261010/power_state_entry.c'
LOCKED='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
LO,HI=0x41cd1a,0x41cd34
SLOT=0x20026e3c
spec=importlib.util.spec_from_file_location('reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==LOCKED
body=blob[LO-0x410000:HI-0x410000]
assert len(body)==26 and struct.unpack_from('<I',blob,0x41d11c-0x410000)[0]+4==SLOT
with tempfile.TemporaryDirectory(prefix='boot-power-state-') as d:
 p=Path(d);objs=[]
 for name,src in [('body',BODY),('entry',ENTRY)]:
  obj=p/(name+'.o');objs.append(obj)
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=soft','-ffreestanding','-fno-builtin','-std=c11','-O2','-ffunction-sections','-fdata-sections','-c',str(src),'-o',str(obj)],check=True,capture_output=True)
 elf=p/'source.elf'
 subprocess.run(['arm-none-eabi-ld','--gc-sections','--entry=power_state','-Ttext=0x430000',*map(str,objs),'-o',str(elf)],check=True,capture_output=True)
 _,segments,symbols=reader.elf_info(elf)
 assert 'power_state' in symbols and 'power_state_wrapper' in symbols
 def run(source,callback,mask,r0,r1,arg):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  for base,size in [(0x08000000,0x1000),(0x410000,0x25000),(0x430000,0x1000),(0x20000000,0x40000)]:
   try:u.mem_map(base,size)
   except:pass
  if source:
   for seg in segments:u.mem_write(seg['address'],seg['data'])
  else:u.mem_write(0x410000,blob)
  u.mem_write(SLOT,struct.pack('<I',0x08000201 if callback else 0))
  u.mem_write(0x20001000,bytes([arg]))
  for reg,val in [(a.UC_ARM_REG_R0,r0),(a.UC_ARM_REG_R1,r1),(a.UC_ARM_REG_R2,0x20001000),(a.UC_ARM_REG_SP,0x2003f000),(a.UC_ARM_REG_LR,0x08000001),(a.UC_ARM_REG_PRIMASK,mask)]:u.reg_write(reg,val)
  for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0x10000000+i)
  done=[False];visited=set();events=[]
  def code(cpu,pc,size,_):
   if pc==0x08000000:done[0]=True;cpu.emu_stop();return
   if pc==0x08000200:
    events.append(tuple(cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(3)))
    cpu.reg_write(a.UC_ARM_REG_R0,0x12345678);cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
   if not source and LO<=pc<HI:visited.update(range(pc,pc+size))
  u.hook_add(UC_HOOK_CODE,code)
  u.emu_start(((symbols['power_state']&~1) if source else LO)|1,0,count=100)
  assert done[0]
  state=(events,u.reg_read(a.UC_ARM_REG_R0),bytes(u.mem_read(0x20001000,1)),u.reg_read(a.UC_ARM_REG_PRIMASK),u.reg_read(a.UC_ARM_REG_SP),tuple(u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)))
  return state,visited
 cases=0;visited=set()
 for callback in [False,True]:
  for mask in [0,1]:
   for r0,r1 in [(0,0),(1,1),(0x100,0x101),(0xffffffff,0xabcdef02)]:
    for arg in [0,2]:
     stock,trace=run(False,callback,mask,r0,r1,arg);source,_=run(True,callback,mask,r0,r1,arg)
     assert stock==source,(callback,mask,r0,r1,arg,stock,source)
     visited|=trace;cases+=1
 assert len(visited)==26
 print(json.dumps({'status':'PASS','cases':cases,'stock_body_bytes':26,'visited_stock_bytes':len(visited),'stock_body_sha256':hashlib.sha256(body).hexdigest(),'image_sha256':LOCKED}))
