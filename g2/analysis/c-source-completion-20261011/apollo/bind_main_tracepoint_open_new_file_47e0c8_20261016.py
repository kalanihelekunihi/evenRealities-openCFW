#!/usr/bin/env python3
"""Bind stock Main tracepoint new-file creation and its bounded RAM cells."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_open_new_file_47e0c8.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_open_new_file_47e0c8.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_open_new_file_47e0c8_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-open-new-file-47e0c8'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-format-pull-path-47de0a/apollo-main-tracepoint-format-pull-path-47de0a.o'
OWNED={'audio_tracepoint_open_new_file_47e0c8','audio_tracepoint_next_sequence_20004188','audio_tracepoint_session_generation_20074ad4'}
ADDED={'audio_tracepoint_trim_old_files_47e090','audio_tracepoint_write_state_47df28','audio_tracepoint_build_header_48ed00'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*a):return subprocess.check_output(a,text=True)
def names(p,flag):return {s.split()[-1] for s in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_OPEN_NEW_FILE_NATIVE_C' or oracle['native_c_cases']!=144 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('new-file oracle changed')
 script=LINKER.read_text()
 if '0x20004188 (NOLOAD)' not in script or '0x20074ad4 (NOLOAD)' not in script:raise RuntimeError('new-file RAM placement changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_open_new_file_47e0c8.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED or names(obj,'-u')-names(BASE,'--defined-only')!=ADDED|{'audio_tracepoint_file_open_474550','audio_tracepoint_file_write_474682'}:raise RuntimeError('new-file source contract changed')
 sections=out('arm-none-eabi-readelf','-SW',str(obj))
 for section in ('next_sequence','session_generation'):
  if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.'+section+r'\s+NOBITS\s+',line) and '000004' in line for line in sections.splitlines()):raise RuntimeError(section+' NOBITS extent changed')
 placed=OUT/'tracepoint-open-new-file-placement.o'
 subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
 addrs={s.split()[-1]:int(s.split()[0],16) for s in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
 if addrs.get('audio_tracepoint_next_sequence_20004188')!=0x20004188 or addrs.get('audio_tracepoint_session_generation_20074ad4')!=0x20074ad4:raise RuntimeError('new-file RAM address changed')
 linked=OUT/'apollo-main-tracepoint-open-new-file-47e0c8.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=194 or len(after)!=196 or before-after!={'audio_tracepoint_open_new_file_47e0c8'} or after-before!=ADDED:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_OPEN_NEW_FILE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':144,
      'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
      'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
      'placement_addresses':{'next_sequence':'0x20004188','session_generation':'0x20074ad4'},
      'section_bytes':{'next_sequence':4,'session_generation':4},'section_type':'NOBITS',
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':sorted(OWNED),'unresolved_before':194,'unresolved_after':196,
      'imports_resolved':['audio_tracepoint_open_new_file_47e0c8'],'imports_added':sorted(ADDED),
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['144 controlled native/C allocation cases; trim/state/header children, final RAM layout and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
