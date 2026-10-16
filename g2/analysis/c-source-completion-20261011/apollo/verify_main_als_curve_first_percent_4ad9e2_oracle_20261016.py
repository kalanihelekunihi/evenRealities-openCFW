#!/usr/bin/env python3
"""Check the stock ALS table getter and C constant against authenticated bytes."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/als_curve_first_percent_4ad9e2.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BASE=0x438000
BODY_SHA=hashlib.sha256(IMAGE[0x4ad9e2-BASE:0x4ad9ea-BASE]).hexdigest()
TABLE_SHA=hashlib.sha256(IMAGE[0x730e24-BASE:0x730e2c-BASE]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-als-curve-first-percent-4ad9e2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if IMAGE[0x730e24-BASE:0x730e2c-BASE]!=(10).to_bytes(4,'little')+(35).to_bytes(4,'little'):
  raise RuntimeError('ALS first table entry changed')
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_als_first_curve_percent_4ad9e2',
                  str(SOURCE),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(BASE,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   start=symbols['audio_als_first_curve_percent_4ad9e2'] if compiled else 0x4ad9e2
   uc.emu_start(start|1,0x600000,count=20)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError('getter did not return')
   return uc.reg_read(A.UC_ARM_REG_R0)
  native=run(False);candidate=run(True)
  if (native,candidate)!=(35,35):raise AssertionError((native,candidate))
  receipt={'status':'PASS_NATIVE_MAIN_ALS_CURVE_FIRST_PERCENT_4AD9E2',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'first_entry_sha256':TABLE_SHA,'cases':1,
           'limits':['The getter and first table entry match stock bytes; final placement and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],1,sha(path))
if __name__=='__main__':main()
