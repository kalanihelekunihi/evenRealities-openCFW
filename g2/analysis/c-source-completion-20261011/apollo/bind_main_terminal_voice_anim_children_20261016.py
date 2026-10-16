#!/usr/bin/env python3
"""Bind source-owned animimage constructor and frame callback."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-voice-anim-factory-597e90/apollo-main-terminal-voice-anim-factory-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-anim-children'
CTOR_OUT=G2/'build/c-firmware/20261016/main-terminal-voice-anim-ctor-597fae'
EXEC_OUT=G2/'build/c-firmware/20261016/main-terminal-voice-anim-exec-598008'
CTOR=G2/'components/audio/uart_thread_source_candidate/terminal_voice_anim_ctor_597fae.c'
EXEC=G2/'components/audio/uart_thread_source_candidate/terminal_voice_anim_exec_598008.c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def compile(source,obj):subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 co=CTOR_OUT/'oracle-receipt.json';eo=EXEC_OUT/'oracle-receipt.json';a=json.loads(co.read_text());b=json.loads(eo.read_text())
 if a['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_CTOR_C_ORACLE' or a['cases']!=12 or a['source_sha256']!=sha(CTOR):raise RuntimeError('ctor oracle changed')
 if b['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_EXEC_C_ORACLE' or b['cases']!=36 or b['source_sha256']!=sha(EXEC):raise RuntimeError('exec oracle changed')
 before=imports(BASE)
 if len(before)!=187 or 'audio_terminal_voice_anim_ctor_597fae' not in before:raise RuntimeError('main frontier changed')
 cobj=OUT/'terminal-voice-anim-ctor.o';eobj=OUT/'terminal-voice-anim-exec.o';linked=OUT/'apollo-main-terminal-voice-anim-children-bound.o'
 compile(CTOR,cobj);compile(EXEC,eobj)
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(cobj),str(eobj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!={'audio_terminal_voice_anim_ctor_597fae'} or after-before or len(after)!=186:raise RuntimeError(f'anim children binding changed {before-after=} {after-before=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_CHILDREN_C','constructor_source':str(CTOR.relative_to(ROOT)),'constructor_source_sha256':sha(CTOR),'callback_source':str(EXEC.relative_to(ROOT)),'callback_source_sha256':sha(EXEC),'constructor_oracle_receipt':str(co.relative_to(ROOT)),'constructor_oracle_receipt_sha256':sha(co),'callback_oracle_receipt':str(eo.relative_to(ROOT)),'callback_oracle_receipt_sha256':sha(eo),'constructor_object':str(cobj.relative_to(ROOT)),'constructor_object_sha256':sha(cobj),'callback_object':str(eobj.relative_to(ROOT)),'callback_object_sha256':sha(eobj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':187,'unresolved_after':186,'imports_resolved':['audio_terminal_voice_anim_ctor_597fae'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Voice style RAM 0x200014e8 remains unresolved; lower LVGL effects, final RAM/object graph and whole image remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
