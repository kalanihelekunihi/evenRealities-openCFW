#!/usr/bin/env python3
"""Bind the stock-compared query session-name lookup into Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-counter-b-alias-5973dc/apollo-main-terminal-counter-b-alias-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-session-name-5ec7f0'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_session_name_5ec7f0.c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
    oracle=OUT/'oracle-receipt.json'; data=json.loads(oracle.read_text())
    if data['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SESSION_NAME_C_ORACLE' or data['cases']!=120 or data['source_sha256']!=sha(SOURCE):raise RuntimeError('oracle changed')
    before=imports(BASE)
    if len(before)!=187 or 'audio_terminal_query_visibility_5ec82a' not in before:raise RuntimeError('main frontier changed')
    obj=OUT/'terminal-query-session-name.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    linked=OUT/'apollo-main-terminal-query-session-name-bound.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=imports(linked)
    if after!=before:raise RuntimeError(f'import frontier changed: {before-after=} {after-before=}')
    receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SESSION_NAME_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(oracle),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':187,'unresolved_after':187,'imports_resolved':[],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['The session-name lookup is source-owned, but its caller 0x5ec82a remains unresolved; provider effects and final RAM placement remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
