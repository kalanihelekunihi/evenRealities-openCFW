#!/usr/bin/env python3
"""Compare stock/C tracepoint version packing from the authenticated ROM string."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_version_47dd08.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-version-47dd08';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
assert blob[0x78c740-0x438000:0x78c749-0x438000]==b'2.2.6.10\0'
with tempfile.TemporaryDirectory() as td:
 p=Path(td);elf=p/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_version_47dd08',str(SOURCE),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,version):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  addr=syms['audio_tracepoint_version_string_78c740'] if compiled else 0x78c740
  u.mem_write(addr,version.encode()+b'\0'*(9-len(version)))
  if not compiled:
   def hook(cpu,pc,size,data):
    if pc==0x43c0e4:
     dst=cpu.reg_read(A.UC_ARM_REG_R0);count=cpu.reg_read(A.UC_ARM_REG_R1)
     cpu.mem_write(dst,b'\0'*count);cpu.reg_write(A.UC_ARM_REG_R0,dst)
    elif pc==0x48d874:
     src=cpu.reg_read(A.UC_ARM_REG_R0);endptr=cpu.reg_read(A.UC_ARM_REG_R1)
     value=0;ptr=src
     while True:
      digit=cpu.mem_read(ptr,1)[0]-48
      if not 0<=digit<=9:break
      value=min(0xffffffff,value*10+digit);ptr+=1
     cpu.mem_write(endptr,ptr.to_bytes(4,'little'))
     cpu.reg_write(A.UC_ARM_REG_R0,value)
    else:return
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_tracepoint_version_47dd08'] if compiled else 0x47dd08
  try:u.emu_start(entry|1,0x600000,count=100000)
  except Exception as exc:raise AssertionError((compiled,version,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  return u.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for version in ('2.2.6.10','3.4.5','v1.2.3','12-34-56','0.0.0','x','9','99.88.77','1x2y3z4'):
  n=run(False,version);c=run(True,version)
  if n!=c:raise AssertionError((version,hex(n),hex(c)))
  cases.append(version)
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_VERSION_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'stock_version_string':'2.2.6.10','stock_string_address':'0x78c740',
      'scope':'first three decimal components of authenticated stock string and eight bounded same-length variants.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
