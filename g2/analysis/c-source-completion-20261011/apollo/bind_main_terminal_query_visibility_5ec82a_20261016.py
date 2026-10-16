#!/usr/bin/env python3
"""Bind the stock-compared query dialog and its source-owned image asset."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-query-session-name-5ec7f0/apollo-main-terminal-query-session-name-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-visibility-5ec82a'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_visibility_5ec82a.c'
IMAGE=G2/'components/audio/uart_thread_source_candidate/terminal_query_image_770890.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
RESOLVED={'audio_terminal_query_visibility_5ec82a'}
ADDED={'audio_terminal_query_root_5e4f54','audio_uart_page_44119c','audio_uart_page_441180'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def compile(source,obj):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
def image_contract(obj,blob):
 with obj.open('rb') as f:
  e=ELFFile(f);symtab=e.get_section_by_name('.symtab')
  by_name={s.name:s for s in symtab.iter_symbols()}
  def data(name):
   s=by_name[name];return e.get_section(s['st_shndx']).data()[s['st_value']:s['st_value']+s['st_size']]
  pixels=data('audio_terminal_query_image_pixels_6ce6b8')
  descriptor=data('audio_terminal_query_image_770890')
  stock_pixels=blob[0x6ce6b8-0x438000:0x6ce6b8-0x438000+256]
  stock_descriptor=blob[0x770890-0x438000:0x770890-0x438000+28]
  if len(pixels)!=256 or pixels!=stock_pixels or len(descriptor)!=28 or descriptor[:16]!=stock_descriptor[:16] or descriptor[20:]!=stock_descriptor[20:]:raise RuntimeError('image bytes changed')
  desc=by_name['audio_terminal_query_image_770890'];sec=e.get_section(desc['st_shndx'])
  rel=e.get_section_by_name('.rel'+sec.name)
  if rel is None or not any(r['r_offset']==desc['st_value']+16 and symtab.get_symbol(r['r_info_sym']).name=='audio_terminal_query_image_pixels_6ce6b8' for r in rel.iter_relocations()):raise RuntimeError('image data relocation missing')
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 oracle=OUT/'oracle-receipt.json';d=json.loads(oracle.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_VISIBILITY_C_ORACLE' or d['cases']!=32 or d['source_sha256']!=sha(SOURCE):raise RuntimeError('query oracle changed')
 before=imports(BASE)
 if len(before)!=187 or not RESOLVED<=before:raise RuntimeError('main frontier changed')
 obj=OUT/'terminal-query-visibility.o';image_obj=OUT/'terminal-query-image.o'
 compile(SOURCE,obj);compile(IMAGE,image_obj);image_contract(image_obj,blob)
 linked=OUT/'apollo-main-terminal-query-visibility-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),str(image_obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=189:raise RuntimeError(f'query binding changed: {before-after=} {after-before=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_VISIBILITY_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'image_source':str(IMAGE.relative_to(ROOT)),'image_source_sha256':sha(IMAGE),'image_stock_descriptor':hex(0x770890),'image_stock_pixels':hex(0x6ce6b8),'image_exact_bytes':True,'oracle_receipt':str(oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(oracle),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'image_object':str(image_obj.relative_to(ROOT)),'image_object_sha256':sha(image_obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':187,'unresolved_after':189,'imports_resolved':sorted(RESOLVED),'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Root-creation and two LVGL style calls remain unresolved; other LVGL effects isolated in oracle. RAM layout and whole payload remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
