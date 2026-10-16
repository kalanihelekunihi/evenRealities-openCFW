#!/usr/bin/env python3
"""Compare stock/C TPF1 header, endian helpers, and CRC32."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_build_header_48ed00.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-build-header-48ed00';OUT.mkdir(parents=True,exist_ok=True)
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PINNED
with tempfile.TemporaryDirectory() as td:
 p=Path(td);shim=p/'shim.c';elf=p/'test.elf';shim.write_text('#include <stdint.h>\nuint32_t audio_tracepoint_version_47dd08(void){return 0;}\n')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tracepoint_build_header_48ed00',str(SOURCE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 funcs={'header':('audio_tracepoint_build_header_48ed00',0x48ed00),
        'le16':('audio_tracepoint_put_le16_48ece2',0x48ece2),
        'le32':('audio_tracepoint_put_le32_48ecec',0x48ecec),
        'crc':('audio_tracepoint_crc32_48ecae',0x48ecae)}
 def run(compiled,kind,a,b=0,c=0):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for addr,data in segs:u.mem_write(addr,data)
  u.mem_map(0x20000000,0x100000)
  dst=0x2007e000;u.mem_write(dst,bytes((i*73+11)&255 for i in range(128)))
  calls=[];version_pc=syms['audio_tracepoint_version_47dd08']&~1 if compiled else 0x47dd08
  def hook(cpu,pc,size,data):
   if pc!=version_pc:return
   calls.append('version');cpu.reg_write(A.UC_ARM_REG_R0,c)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  for reg,val in [(A.UC_ARM_REG_R0,dst),(A.UC_ARM_REG_R1,a),(A.UC_ARM_REG_R2,b)]:u.reg_write(reg,val)
  name,native=funcs[kind];entry=syms[name] if compiled else native
  try:u.emu_start(entry|1,0x600000,count=100000)
  except Exception as exc:raise AssertionError((compiled,kind,a,b,c,hex(u.reg_read(A.UC_ARM_REG_PC)))) from exc
  return bytes(u.mem_read(dst,128)),u.reg_read(A.UC_ARM_REG_R0) if kind=='crc' else None,calls
 cases=[]
 for sequence in (0,1,0xffffffff):
  for generation in (0,5,0xffffffff):
   for version in (0,0x010203,0xffffffff):
    n=run(False,'header',sequence,generation,version);c=run(True,'header',sequence,generation,version)
    if n!=c:raise AssertionError(('header',sequence,generation,version,n,c))
    cases.append(('header',sequence,generation,version))
 for value in (0,1,0x1234,0xffffffff):
  for kind in ('le16','le32'):
   n=run(False,kind,value);c=run(True,kind,value)
   if n!=c:raise AssertionError((kind,value,n,c))
   cases.append((kind,value))
 for length in (0,1,2,7,28,64,128):
  n=run(False,'crc',length);c=run(True,'crc',length)
  if n!=c:raise AssertionError(('crc',length,n,c))
  cases.append(('crc',length))
 row={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_TPF1_HEADER_NATIVE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      'payload_sha256':PINNED,'native_c_cases':len(cases),
      'scope':'TPF1 32-byte header, little-endian helpers and CRC32 across controlled version, sequence and generation values.'}
 path=OUT/'oracle.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
