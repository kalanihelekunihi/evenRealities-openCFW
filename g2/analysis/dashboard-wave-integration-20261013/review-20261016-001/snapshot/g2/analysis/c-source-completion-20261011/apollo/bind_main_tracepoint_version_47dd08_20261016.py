#!/usr/bin/env python3
"""Bind the tracepoint version parser and authenticated ROM version string."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_version_47dd08.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_version_47dd08.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_version_47dd08_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-version-47dd08'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-build-header-48ed00/apollo-main-tracepoint-build-header-48ed00.o'
OWNED={'audio_tracepoint_version_47dd08','audio_tracepoint_version_string_78c740'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*a):return subprocess.check_output(a,text=True)
def names(p,flag):return {s.split()[-1] for s in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_VERSION_NATIVE_C' or oracle['native_c_cases']!=9 or oracle['source_sha256']!=sha(SOURCE) or oracle['stock_version_string']!='2.2.6.10':raise RuntimeError('version oracle changed')
 if '0x0078c740' not in LINKER.read_text():raise RuntimeError('version placement changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_version_47dd08.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED or names(obj,'-u'):raise RuntimeError('version source contract changed')
 sections=out('arm-none-eabi-readelf','-SW',str(obj))
 if not any(re.search(r'\s\.rodata\.opencfw\.tracepoint\.version\s+PROGBITS\s+',line) and '000009' in line for line in sections.splitlines()):raise RuntimeError('version string extent changed')
 placed=OUT/'tracepoint-version-placement.o'
 subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
 addrs={s.split()[-1]:int(s.split()[0],16) for s in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
 if addrs.get('audio_tracepoint_version_string_78c740')!=0x78c740:raise RuntimeError('version string address changed')
 linked=OUT/'apollo-main-tracepoint-version-47dd08.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=196 or len(after)!=195 or before-after!={'audio_tracepoint_version_47dd08'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_VERSION_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':9,
      'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
      'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
      'placement_address':'0x78c740','section_bytes':9,'section_type':'PROGBITS',
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':sorted(OWNED),'unresolved_before':196,'unresolved_after':195,
      'imports_resolved':['audio_tracepoint_version_47dd08'],'imports_added':[],
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['Nine controlled stock/C version strings; final ROM placement and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
