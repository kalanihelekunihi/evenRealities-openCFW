#!/usr/bin/env python3
"""Bind stock-compared audio manager app acquisition to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_app_acquire_54f380.c'
BASE=G2/'build/c-firmware/20261016/main-text-stream-tick/apollo-main-text-stream-tick-bound.o'
OUT=G2/'build/c-firmware/20261016/main-even-ai-app-acquire';ORACLE=OUT/'oracle-receipt.json'
PROVIDERS={'audio_even_ai_app_acquire_54f380','audio_even_ai_app_count_54f364','g2_audio_app_acquired'}
CHILDREN={'audio_app_codec_enable_53ca32','audio_app_first_hardware_prepare_57a926','audio_app_stream_enable_53ca10','g2_audio_first_hardware_context_20108948'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_EVEN_AI_APP_ACQUIRE_C_ORACLE' or oracle['cases']!=560 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('app acquire oracle changed')
 obj=OUT/'even_ai_app_acquire_54f380.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=PROVIDERS:raise RuntimeError('app acquire providers changed')
 before=names(BASE,'-u')
 if len(before)!=173 or 'audio_even_ai_app_acquire_54f380' not in before:raise RuntimeError('app acquire base changed')
 linked=OUT/'apollo-main-even-ai-app-acquire-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_even_ai_app_acquire_54f380'} or after-before!=CHILDREN or len(after)!=176:raise RuntimeError(f'app acquire frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_EVEN_AI_APP_ACQUIRE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':173,'unresolved_after':176,'imports_resolved':['audio_even_ai_app_acquire_54f380'],'imports_added':sorted(CHILDREN),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['First hardware context extent and final state placement remain open.','Three setup children, whole-image link, and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],173,176,sha(path))
if __name__=='__main__':main()
