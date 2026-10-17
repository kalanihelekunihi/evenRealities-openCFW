#!/usr/bin/env python3
"""Bind query hit-count, height and style-accessor children."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-query-show-5e641c/apollo-main-terminal-query-show-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-hit-count-5eb576'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_query_hit_count_5eb576.c',G2/'components/audio/uart_thread_source_candidate/terminal_query_height_5eb438.c']
ORACLES=[OUT/'oracle-receipt.json',G2/'build/c-firmware/20261016/main-terminal-query-height-5eb438/oracle-receipt.json']
STATUSES=['PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_HIT_COUNT_C_ORACLE','PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_HEIGHT_C_ORACLE']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 for s,o,status in zip(SOURCES,ORACLES,STATUSES):
  d=json.loads(o.read_text())
  if d['status']!=status or d['source_sha256']!=sha(s):raise RuntimeError('source/oracle changed')
 before=imports(BASE)
 if len(before)!=177 or 'audio_terminal_query_hit_count_5eb576' not in before:raise RuntimeError('Apollo frontier changed')
 objects=[]
 for s in SOURCES:
  obj=OUT/(s.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(obj)],check=True);objects.append(obj)
 linked=OUT/'apollo-main-terminal-query-hit-count-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*[str(o) for o in objects],'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_query_hit_count_5eb576'}
 if before-after!=resolved or after-before or len(after)!=176:raise RuntimeError(f'query-hit-count binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_HIT_COUNT_C','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'oracle_receipts':[str(o.relative_to(ROOT)) for o in ORACLES],'oracle_receipt_sha256':[sha(o) for o in ORACLES],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':177,'unresolved_after':176,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Query hit-count, height and two style accessors pass bounded stock oracles; query constructor, mutable LVGL tree effects and final image remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
