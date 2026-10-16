#!/usr/bin/env python3
"""Bind result-area constructor and exact source-owned ASR icon."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-asr-final-5e5aae/apollo-main-terminal-ui-action-asr-final-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-result-area-5ebff8'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_result_area_prepare_5ebff8.c'
ICON=G2/'components/audio/uart_thread_source_candidate/terminal_result_icon_773258.c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def compile(source,obj):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
def validate_icon(obj,blob):
 with obj.open('rb') as f:
  e=ELFFile(f);symtab=e.get_section_by_name('.symtab');symbols={s.name:s for s in symtab.iter_symbols()}
  def data(name):
   s=symbols[name];return e.get_section(s['st_shndx']).data()[s['st_value']:s['st_value']+s['st_size']]
  pixels=data('audio_terminal_result_icon_pixels_6ceab8');desc=data('audio_terminal_result_icon_773258')
  stock_pixels=blob[0x6ceab8-0x438000:0x6ceab8-0x438000+256]
  stock_desc=blob[0x773258-0x438000:0x773258-0x438000+28]
  if len(pixels)!=256 or pixels!=stock_pixels or len(desc)!=28 or desc[:16]!=stock_desc[:16] or desc[20:]!=stock_desc[20:]:raise RuntimeError('result icon bytes changed')
  symbol=symbols['audio_terminal_result_icon_773258'];sec=e.get_section(symbol['st_shndx']);rel=e.get_section_by_name('.rel'+sec.name)
  if rel is None or not any(r['r_offset']==symbol['st_value']+16 and symtab.get_symbol(r['r_info_sym']).name=='audio_terminal_result_icon_pixels_6ceab8' for r in rel.iter_relocations()):raise RuntimeError('result icon relocation missing')
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 oracle=OUT/'oracle-receipt.json';d=json.loads(oracle.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_RESULT_AREA_C_ORACLE' or d['cases']!=48 or d['source_sha256']!=sha(SOURCE):raise RuntimeError('result-area oracle changed')
 before=imports(BASE)
 if len(before)!=184 or 'audio_terminal_ui_result_area_prepare_5ebff8' not in before:raise RuntimeError('main frontier changed')
 source_obj=OUT/'terminal-result-area.o';icon_obj=OUT/'terminal-result-icon.o'
 compile(SOURCE,source_obj);compile(ICON,icon_obj);validate_icon(icon_obj,blob)
 linked=OUT/'apollo-main-terminal-result-area-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(source_obj),str(icon_obj),'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_result_area_prepare_5ebff8'}
 if before-after!=resolved or after-before or len(after)!=183:raise RuntimeError(f'result-area binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_RESULT_AREA_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'icon_source':str(ICON.relative_to(ROOT)),'icon_source_sha256':sha(ICON),'icon_exact_bytes':True,'oracle_receipt':str(oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(oracle),'source_object':str(source_obj.relative_to(ROOT)),'source_object_sha256':sha(source_obj),'icon_object':str(icon_obj.relative_to(ROOT)),'icon_object_sha256':sha(icon_obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':184,'unresolved_after':183,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Bounded result-area call/state oracle and exact icon bytes pass; lower LVGL effects, final RAM/layout, whole image and hardware remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
