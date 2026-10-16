#!/usr/bin/env python3
"""Prove stock-initialized 19-frame table and relocatable C asset identity."""
import hashlib,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R9,UC_ARM_REG_SP,UC_ARM_REG_LR
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_frames_200014e8.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/terminal_voice_frames_placement.ld'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-frames-200014e8'
WRAPPED=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
COUNT=19;DESC=0x76bfb8;PIXELS=0x6cd2b8;RAM=0x200014e8
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 wrapped=WRAPPED.read_bytes();blob=wrapped[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 # Execute the authenticated main-image low-RAM scatter record, not a guessed table.
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,0x360000);u.mem_write(0x437fe0,wrapped)
 u.mem_map(0x10000000,0x1000);u.mem_map(0x20000000,0x4000000)
 u.reg_write(UC_ARM_REG_SP,0x203ff000);u.reg_write(UC_ARM_REG_R9,0)
 u.reg_write(UC_ARM_REG_LR,0x10000001);u.reg_write(UC_ARM_REG_R0,0x75d3f4)
 u.emu_start(0x43a11f,0x10000000,count=20_000_000)
 if u.reg_read(UC_ARM_REG_R0)!=0x75d400:raise RuntimeError('scatter row did not complete')
 stock_table=struct.unpack('<19I',u.mem_read(RAM,COUNT*4))
 expected_table=tuple(DESC+i*28 for i in range(COUNT))
 if stock_table!=expected_table:raise RuntimeError('stock runtime frame table changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'terminal-voice-frames.o';elf=OUT/'terminal-voice-frames-placement.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 with obj.open('rb') as f:
  e=ELFFile(f);symtab=e.get_section_by_name('.symtab');symbols={s.name:s for s in symtab.iter_symbols()}
  def data(name):
   s=symbols[name];return e.get_section(s['st_shndx']).data()[s['st_value']:s['st_value']+s['st_size']]
  pix=data('audio_terminal_voice_frame_pixels_6cd2b8')
  desc=data('audio_terminal_voice_frame_descriptors_76bfb8')
  table=data('audio_terminal_voice_style_200014e8')
  if len(pix)!=COUNT*256 or pix!=blob[PIXELS-0x438000:PIXELS-0x438000+COUNT*256]:raise RuntimeError('frame pixel bytes changed')
  if len(desc)!=COUNT*28 or len(table)!=COUNT*4:raise RuntimeError('frame extent changed')
  for i in range(COUNT):
   native=blob[DESC+i*28-0x438000:DESC+(i+1)*28-0x438000];rebuilt=desc[i*28:(i+1)*28]
   if native[:16]!=rebuilt[:16] or native[20:]!=rebuilt[20:]:raise RuntimeError(f'descriptor {i} changed')
  ds=symbols['audio_terminal_voice_frame_descriptors_76bfb8'];ts=symbols['audio_terminal_voice_style_200014e8']
  dsec=e.get_section(ds['st_shndx']);tsec=e.get_section(ts['st_shndx'])
  drel=e.get_section_by_name('.rel'+dsec.name);trel=e.get_section_by_name('.rel'+tsec.name)
  drels=list(drel.iter_relocations());trels=list(trel.iter_relocations())
  if len(drels)!=COUNT or len(trels)!=COUNT:raise RuntimeError('frame relocation count changed')
  for i,(dr,tr) in enumerate(zip(drels,trels)):
   if dr['r_offset']!=ds['st_value']+i*28+16 or symtab.get_symbol(dr['r_info_sym']).name!='audio_terminal_voice_frame_pixels_6cd2b8' or struct.unpack_from('<I',desc,i*28+16)[0]!=i*256:raise RuntimeError(f'descriptor relocation {i} changed')
   if tr['r_offset']!=ts['st_value']+i*4 or symtab.get_symbol(tr['r_info_sym']).name!='audio_terminal_voice_frame_descriptors_76bfb8' or struct.unpack_from('<I',table,i*4)[0]!=i*28:raise RuntimeError(f'table relocation {i} changed')
 subprocess.run(['arm-none-eabi-ld','-T',str(LINKER),'-e','audio_terminal_voice_style_200014e8',str(obj),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);symbols={s.name:s for s in e.get_section_by_name('.symtab').iter_symbols()}
  if symbols['audio_terminal_voice_style_200014e8']['st_value']!=RAM:raise RuntimeError('RAM fragment placement changed')
  base=symbols['audio_terminal_voice_frame_descriptors_76bfb8']['st_value']
  table_sec=e.get_section(symbols['audio_terminal_voice_style_200014e8']['st_shndx'])
  image_table=struct.unpack('<19I',table_sec.data()[:COUNT*4])
  if image_table!=tuple(base+i*28 for i in range(COUNT)):raise RuntimeError('linked frame table relocation changed')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_FRAMES_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'linker':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),'payload_sha256':PIN,'stock_scatter_entry':'0x43a11e','stock_scatter_descriptor':'0x75d3f4','stock_table_address':hex(RAM),'stock_table_count':COUNT,'stock_table_first':hex(stock_table[0]),'stock_table_last':hex(stock_table[-1]),'pixel_bytes':len(pix),'descriptor_bytes':len(desc),'pointer_table_bytes':len(table),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'placement_elf':str(elf.relative_to(ROOT)),'placement_elf_sha256':sha(elf),'scope':'Stock scatter-executed pointer table; exact 19 frame descriptors/pixels; source relocations and bounded RAM placement','limits':['This proves a placement fragment and initialized table, not integration into full main scatter/layout, LVGL runtime frame effects or hardware.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],COUNT,sha(path))
if __name__=='__main__':main()
