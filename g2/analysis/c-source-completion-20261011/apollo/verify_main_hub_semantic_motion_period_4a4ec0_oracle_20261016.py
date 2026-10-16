#!/usr/bin/env python3
"""Compare stock and C semantic motion period cell writes."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/hub_semantic_motion_period_4a4ec0.c'
IMAGE=(G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BASE=0x438000
BODY_SHA=hashlib.sha256(IMAGE[0x4a4ec0-BASE:0x4a4ed0-BASE]).hexdigest()
OUT=G2/'build/c-firmware/20261016/main-hub-semantic-motion-period-4a4ec0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def u32(v):return (v&0xffffffff).to_bytes(4,'little')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  elf=Path(tmp)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                  '-std=c11','-ffreestanding','-fno-builtin','-O2','-w','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_hub_semantic_motion_period_4a4ec0',
                  str(SOURCE),'-o',str(elf)],check=True)
  with elf.open('rb') as fh:
   parsed=ELFFile(fh)
   segments=[(s['p_vaddr'],s.data()) for s in parsed.iter_segments() if s['p_type']=='PT_LOAD']
   symbols={s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
  def run(compiled,period,duration,old_period,old_duration):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(BASE,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   cells=((symbols['audio_hub_motion_period_cell'],symbols['audio_hub_motion_duration_cell'])
          if compiled else (0x20000e68,0x20000e6c))
   uc.mem_write(cells[0],u32(old_period));uc.mem_write(cells[1],u32(old_duration))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,period);uc.reg_write(A.UC_ARM_REG_R1,duration)
   start=symbols['audio_hub_semantic_motion_period_4a4ec0'] if compiled else 0x4a4ec0
   uc.emu_start(start|1,0x600000,count=30)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:raise RuntimeError(('no return',compiled))
   return (uc.reg_read(A.UC_ARM_REG_R0),
           tuple(int.from_bytes(uc.mem_read(cell,4),'little') for cell in cells))
  cases=0
  for period in (0,1,0x12345678,0xffffffff):
   for duration in (0,2,0x87654321,0xffffffff):
    for old_period,old_duration in ((0,0),(0xa5a5a5a5,0x5a5a5a5a)):
     args=(period,duration,old_period,old_duration)
     native=run(False,*args);candidate=run(True,*args)
     if native!=candidate:raise AssertionError((args,native,candidate))
     cases+=1
  receipt={'status':'PASS_NATIVE_MAIN_HUB_SEMANTIC_MOTION_PERIOD_4A4EC0',
           'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
           'official_payload_sha256':IMAGE_SHA,'native_body_sha256':BODY_SHA,
           'cases':cases,
           'limits':['The two writes and zero return match stock; final RAM placement and hardware behavior remain open.']}
  path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
