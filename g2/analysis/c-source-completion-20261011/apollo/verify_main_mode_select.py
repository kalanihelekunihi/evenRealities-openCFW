#!/usr/bin/env python3
"""Bounded Main native/source MX25U mode selector comparison."""
import argparse,hashlib,itertools,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as R
ROOT=Path(__file__).resolve().parents[4];BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);args=p.parse_args()
with args.elf.open('rb') as f:
 elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz']];syms={s.name:s['st_value']&~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
NATIVE=0x46f6ba;SOURCE=syms['g2_norflash_mode_select_46f6ba'];RET=0x200ff000;SP=0x200fe000;CONFIG=0x20000820;CELL=0x20074544;STUB=syms['g2_norflash_config_transfer_4c0f78'];SOURCE_CELL=syms['g2_norflash_controller_handle_20074544']
def run(source,mode,handle):
 cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.mem_map(0x430000,0x380000);cpu.mem_write(0x437fe0,blob);cpu.mem_map(0x800000,0x10000)
 for addr,data in segs:cpu.mem_write(addr,data)
 cpu.mem_map(0x20000000,0x100000);cpu.mem_write(CONFIG,bytes(range(16)));cpu.mem_write(CELL,handle.to_bytes(4,'little'));cpu.mem_write(SOURCE_CELL,handle.to_bytes(4,'little'));cpu.reg_write(R.UC_ARM_REG_SP,SP);cpu.reg_write(R.UC_ARM_REG_LR,RET|1);cpu.reg_write(R.UC_ARM_REG_R0,mode)
 events=[]
 def hook(m,pc,size,user):
  if pc==(STUB if source else 0x4c0f78):
   values=[m.reg_read(r) for r in (R.UC_ARM_REG_R0,R.UC_ARM_REG_R1,R.UC_ARM_REG_R2)];events.append([*values,bytes(m.mem_read(values[2],16)).hex()]);m.reg_write(R.UC_ARM_REG_R0,7);m.reg_write(R.UC_ARM_REG_PC,m.reg_read(R.UC_ARM_REG_LR))
  elif pc==RET:m.emu_stop()
 cpu.hook_add(UC_HOOK_CODE,hook);cpu.emu_start((SOURCE if source else NATIVE)|1,RET+2,count=1000);assert cpu.reg_read(R.UC_ARM_REG_PC)==RET
 return {'events':events,'configuration':bytes(cpu.mem_read(CONFIG,16)).hex()}
for mode,handle in itertools.product((0,1,2,255,256,257,0xffffffff),(0,0x20070000)):
 native=run(False,mode,handle);source=run(True,mode,handle);assert native==source,(mode,handle,native,source)
report={'status':'PASS_MAIN_MODE_SELECT_BOUNDED_NATIVE_SOURCE','cases':14,'stock_sha256':hashlib.sha256(blob).hexdigest(),'source_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'limits':['Configuration transfer is injected equally; no hardware command delivery is verified.','Absolute SRAM state and pointer placement still require full-image ownership checks.']}
args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(report['status'],report['cases'])
