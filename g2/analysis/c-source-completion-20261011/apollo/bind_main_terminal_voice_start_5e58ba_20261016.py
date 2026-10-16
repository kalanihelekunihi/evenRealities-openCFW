#!/usr/bin/env python3
"""Bind voice-start FSM action, timer child and source-owned icon."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-query-root-5e4f54/apollo-main-terminal-query-root-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-voice-start-5e58ba'
TIMER_OUT=G2/'build/c-firmware/20261016/main-terminal-voice-timeout-start-5e7ed4'
ACTION=G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_voice_start_5e58ba.c'
TIMER=G2/'components/audio/uart_thread_source_candidate/terminal_voice_timeout_start_5e7ed4.c'
IMAGE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_icon_773044.c'
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
  pixels=data('audio_terminal_voice_icon_pixels_6ce8b8');desc=data('audio_terminal_voice_icon_773044')
  stock_pixels=blob[0x6ce8b8-0x438000:0x6ce8b8-0x438000+256]
  stock_desc=blob[0x773044-0x438000:0x773044-0x438000+28]
  if len(pixels)!=256 or pixels!=stock_pixels or len(desc)!=28 or desc[:16]!=stock_desc[:16] or desc[20:]!=stock_desc[20:]:raise RuntimeError('voice icon bytes changed')
  symbol=symbols['audio_terminal_voice_icon_773044'];sec=e.get_section(symbol['st_shndx']);rel=e.get_section_by_name('.rel'+sec.name)
  if rel is None or not any(r['r_offset']==symbol['st_value']+16 and symtab.get_symbol(r['r_info_sym']).name=='audio_terminal_voice_icon_pixels_6ce8b8' for r in rel.iter_relocations()):raise RuntimeError('voice icon relocation missing')
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 action_oracle=OUT/'oracle-receipt.json';timer_oracle=TIMER_OUT/'oracle-receipt.json'
 a=json.loads(action_oracle.read_text());t=json.loads(timer_oracle.read_text())
 if a['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_START_C_ORACLE' or a['cases']!=25 or a['source_sha256']!=sha(ACTION):raise RuntimeError('action oracle changed')
 if t['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_TIMEOUT_START_C_ORACLE' or t['cases']!=24 or t['source_sha256']!=sha(TIMER):raise RuntimeError('timer oracle changed')
 before=imports(BASE)
 if len(before)!=186 or 'audio_terminal_ui_action_5e58ba' not in before:raise RuntimeError('main frontier changed')
 action_obj=OUT/'terminal-voice-start.o';timer_obj=OUT/'terminal-voice-timeout-start.o';image_obj=OUT/'terminal-voice-icon.o'
 for source,obj in ((ACTION,action_obj),(TIMER,timer_obj),(IMAGE,image_obj)):compile(source,obj)
 validate_icon(image_obj,blob)
 linked=OUT/'apollo-main-terminal-voice-start-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(action_obj),str(timer_obj),str(image_obj),'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e58ba'};added={'audio_terminal_ui_voice_prepare_5ebd0e'}
 if before-after!=resolved or after-before!=added or len(after)!=186:raise RuntimeError(f'voice start binding changed {before-after=} {after-before=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_START_C','source':str(ACTION.relative_to(ROOT)),'source_sha256':sha(ACTION),'timer_source':str(TIMER.relative_to(ROOT)),'timer_source_sha256':sha(TIMER),'image_source':str(IMAGE.relative_to(ROOT)),'image_source_sha256':sha(IMAGE),'image_exact_bytes':True,'oracle_receipt':str(action_oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(action_oracle),'timer_oracle_receipt':str(timer_oracle.relative_to(ROOT)),'timer_oracle_receipt_sha256':sha(timer_oracle),'action_object':str(action_obj.relative_to(ROOT)),'action_object_sha256':sha(action_obj),'timer_object':str(timer_obj.relative_to(ROOT)),'timer_object_sha256':sha(timer_obj),'image_object':str(image_obj.relative_to(ROOT)),'image_object_sha256':sha(image_obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':186,'unresolved_after':186,'imports_resolved':sorted(resolved),'imports_added':sorted(added),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Voice-prepare child 0x5ebd0e remains unresolved; lower service, LVGL, encoder and logging effects isolated. Final RAM/object layout and whole image remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
