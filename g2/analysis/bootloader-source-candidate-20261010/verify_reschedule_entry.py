#!/usr/bin/env python3
"""Compare stock kernel reschedule with the source-backed idle entry."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[3]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
BODY=ROOT/'g2/components/bootloader/thread_creation/kernel_runtime.c'
ENTRY=ROOT/'g2/components/bootloader/source_candidate_20261010/reschedule_entry.c'
LOCKED='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
LO,HI=0x41b3d0,0x41b3e2
MMIO=0xe000ed04
spec=importlib.util.spec_from_file_location('reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==LOCKED
body=blob[LO-0x410000:HI-0x410000]
assert body==bytes.fromhex('5ff0805056490860bff34f8fbff36f8f7047')
assert struct.unpack_from('<I',blob,0x41b530-0x410000)[0]==MMIO
with tempfile.TemporaryDirectory(prefix='boot-reschedule-') as d:
 p=Path(d);objs=[]
 for name,src in [('body',BODY),('entry',ENTRY)]:
  obj=p/(name+'.o');objs.append(obj)
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=soft','-ffreestanding','-fno-builtin','-std=c11','-O2','-ffunction-sections','-fdata-sections','-c',str(src),'-o',str(obj)],check=True,capture_output=True)
 elf=p/'source.elf'
 subprocess.run(['arm-none-eabi-ld','--gc-sections','--entry=reschedule','-Ttext=0x430000',*map(str,objs),'-o',str(elf)],check=True,capture_output=True)
 _,segments,symbols=reader.elf_info(elf)
 assert 'reschedule' in symbols and 'opencfw_bl_kernel_reschedule' in symbols
 def run(source,initial,mask,r0,r1):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  for base,size in [(0x08000000,0x1000),(0x410000,0x25000),(0x430000,0x1000),(0x20000000,0x40000),(0xe000e000,0x1000)]:
   try:u.mem_map(base,size)
   except:pass
  if source:
   for seg in segments:u.mem_write(seg['address'],seg['data'])
  else:u.mem_write(0x410000,blob)
  u.mem_write(MMIO,struct.pack('<I',initial))
  for reg,val in [(a.UC_ARM_REG_R0,r0),(a.UC_ARM_REG_R1,r1),(a.UC_ARM_REG_SP,0x2003f000),(a.UC_ARM_REG_LR,0x08000001),(a.UC_ARM_REG_PRIMASK,mask)]:u.reg_write(reg,val)
  for i in range(2,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0x10000000+i)
  done=[False];visited=set();writes=[]
  def code(cpu,pc,size,_):
   if pc==0x08000000:done[0]=True;cpu.emu_stop()
   if not source and LO<=pc<HI:visited.update(range(pc,pc+size))
  def write(cpu,access,address,size,value,_):
   if address==MMIO:writes.append((size,value))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start(((symbols['reschedule']&~1) if source else LO)|1,0,count=100)
  assert done[0]
  state=(struct.unpack('<I',u.mem_read(MMIO,4))[0],writes,u.reg_read(a.UC_ARM_REG_PRIMASK),u.reg_read(a.UC_ARM_REG_SP),tuple(u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(2,12)))
  return state,visited
 cases=0;visited=set()
 for value in [0,1,0xffffffff,0x80000000]:
  for mask in [0,1]:
   for r0,r1 in [(0,0),(0x12345678,0xabcdef01)]:
    stock,trace=run(False,value,mask,r0,r1);source,_=run(True,value,mask,r0,r1)
    assert stock==source,(value,mask,r0,r1,stock,source)
    visited|=trace;cases+=1
 assert len(visited)==18
 print(json.dumps({'status':'PASS','cases':cases,'executed_stock_body_bytes':18,'visited_stock_bytes':len(visited),'stock_body_sha256':hashlib.sha256(body).hexdigest(),'image_sha256':LOCKED}))
