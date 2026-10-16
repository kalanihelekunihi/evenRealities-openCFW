#!/usr/bin/env python3
"""Compare stock errno-location return with C-owned errno cell address."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/file_errno_location_439cc4.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-file-errno-location-439cc4';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
assert int.from_bytes(blob[0x439cd8-0x438000:0x439cdc-0x438000],'little')==0x20074f14
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf';shim.write_text('#include <stdint.h>\nvolatile uint32_t audio_uart_ring_errno_20074f14;\n')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_file_errno_location_439cc4',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,value):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  cell=syms['audio_uart_ring_errno_20074f14'] if compiled else 0x20074f14
  u.mem_write(cell,value.to_bytes(4,'little'));u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  entry=syms['audio_file_errno_location_439cc4'] if compiled else 0x439cc4
  u.emu_start(entry|1,0x600000,count=10000)
  result=u.reg_read(A.UC_ARM_REG_R0)
  return result==cell,int.from_bytes(u.mem_read(result,4),'little')
 cases=[]
 for value in (0,5,22,0xffffffff):
  n=run(False,value);c=run(True,value)
  if n!=c or n!=(True,value):raise AssertionError((value,n,c))
  cases.append(value)
 receipt={'status':'PASS_BOUNDED_MAIN_FILE_ERRNO_LOCATION_NATIVE_C','native_c_cases':len(cases),'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'payload_sha256':PINNED,'native_cell_address':'0x20074f14','limits':['Pointer target compared to already owned errno cell; final whole-image placement remains open.']}
 path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
