#!/usr/bin/env python3
"""Pin stock-compared Conversate display-main-page route in Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261016'
PRIOR=BASE/'main-conversate-prep-button-5b1150/candidate.o';HERE=BASE/'main-conversate-display-main-page-5b2d64'
CANDIDATE=HERE/'candidate.o';SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_display_main_page_5b2d64.c';ORACLE=HERE/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines() if line.strip()}
def main():
 before,after=imports(PRIOR),imports(CANDIDATE)
 removed={'audio_conversate_ui_route_5b2d64'}
 added={'audio_conversate_display_tick_5b22ee','audio_conversate_prep_icon_76a47c','audio_conversate_title_label_5b3334','audio_uart_page_43f6ac'}
 if len(before)!=131 or len(after)!=134 or before-after!=removed or after-before!=added:raise RuntimeError('display-main-page frontier changed')
 row=json.loads(ORACLE.read_text())
 if row['status']!='PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_MAIN_PAGE_5B2D64_C' or row['cases']!=160 or row['native_body']!='0x5b2d64..0x5b30c7' or row['source_sha256']!=sha(SOURCE) or row['source_complete'] or row['flashable'] or row['hardware_proof']:raise RuntimeError('display-main-page oracle changed')
 defined=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(CANDIDATE)],text=True)
 if ' audio_conversate_ui_route_5b2d64\n' not in defined:raise RuntimeError('display-main-page body missing')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_MAIN_PAGE_5B2D64_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CANDIDATE),'source':ref(SOURCE),'oracle_receipt':ref(ORACLE),'native_body':row['native_body'],'oracle_cases':row['cases'],'unresolved_before':131,'unresolved_after':134,'removed_imports':sorted(removed),'new_imports':sorted(added),'source_complete':False,'flashable':False,'hardware_proof':False,'remaining_gate':'Display tick callback, title/icon data ownership, one LVGL provider, six-frame RAM array, other Main imports and full-image gates remain open.'}
 path=HERE/'receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(after),sha(path))
if __name__=='__main__':main()
