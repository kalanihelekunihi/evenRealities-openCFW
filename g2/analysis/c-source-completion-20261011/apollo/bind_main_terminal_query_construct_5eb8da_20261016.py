#!/usr/bin/env python3
"""Bind query-panel constructor and two stock-compared forwarding helpers."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-query-hit-count-5eb576/apollo-main-terminal-query-hit-count-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-construct-5eb8da'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_query_construct_5eb8da.c',G2/'components/audio/uart_thread_source_candidate/terminal_query_four_margins_5eb2bc.c',G2/'components/audio/uart_thread_source_candidate/terminal_query_gap_style_441262.c']
ORACLE=OUT/'oracle-receipt.json';CHILD_ORACLE=OUT/'children-oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 d=json.loads(ORACLE.read_text());c=json.loads(CHILD_ORACLE.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_CONSTRUCT_C_ORACLE' or d['source_sha256']!=sha(SOURCES[0]):raise RuntimeError('constructor oracle/source changed')
 if c['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_CONSTRUCTOR_CHILDREN_C_ORACLE' or c['source_sha256']!=[sha(s) for s in SOURCES[1:]]:raise RuntimeError('children oracle/sources changed')
 before=imports(BASE)
 if len(before)!=176 or 'audio_terminal_query_construct_5eb8da' not in before:raise RuntimeError('Apollo frontier changed')
 objects=[]
 for s in SOURCES:
  obj=OUT/(s.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(obj)],check=True);objects.append(obj)
 linked=OUT/'apollo-main-terminal-query-construct-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*[str(o) for o in objects],'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_query_construct_5eb8da'}
 if before-after!=resolved or after-before or len(after)!=175:raise RuntimeError(f'query-constructor binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_CONSTRUCT_C','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'oracle_receipts':[str(o.relative_to(ROOT)) for o in (ORACLE,CHILD_ORACLE)],'oracle_receipt_sha256':[sha(o) for o in (ORACLE,CHILD_ORACLE)],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':176,'unresolved_after':175,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Query constructor and two style helpers pass bounded stock call/state oracles; lower LVGL/TD effects, dynamic mutation, final image and hardware remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
