#!/usr/bin/env python3
"""Bind stock-backed unlink facade and bounded readiness cell into Main."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_storage_unlink_47498c.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/file_ready_200746a8.ld'
ORACLE_SCRIPT=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_storage_unlink_47498c_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-storage-unlink-47498c';ORACLE=OUT/'oracle.json'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-close-active-file-47e06a/apollo-main-tracepoint-close-active-file-47e06a.o'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED={'audio_tracepoint_storage_unlink_47498c','audio_file_ready_200746a8'}
ADDED={'audio_file_errno_location_439cc4','audio_file_lfs_remove_4cfa76'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def output(*a):return subprocess.check_output(a,text=True)
def names(p,flag):return {x.split()[-1] for x in output('arm-none-eabi-nm','-g',flag,str(p)).splitlines()}
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PINNED or int.from_bytes(blob[0x474e84-0x438000:0x474e88-0x438000],'little')!=0x200746a8:raise RuntimeError('stock readiness cell changed')
 if '0x200746a8 (NOLOAD)' not in LINKER.read_text():raise RuntimeError('ready-cell placement changed')
 subprocess.run([sys.executable,str(ORACLE_SCRIPT)],check=True,capture_output=True,text=True)
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_UNLINK_FACADE_NATIVE_C' or oracle['native_c_cases']!=72 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('unlink oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_storage_unlink_47498c.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED:raise RuntimeError('unlink source definitions changed')
 sections=output('arm-none-eabi-readelf','-SW',str(obj))
 if not any(re.search(r'\s\.bss\.opencfw\.file\.ready\s+NOBITS\s+',x) and '000004' in x for x in sections.splitlines()):raise RuntimeError('ready-cell NOBITS size changed')
 placed=OUT/'file-ready-placement.o'
 subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
 addrs={x.split()[-1]:int(x.split()[0],16) for x in output('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
 if addrs.get('audio_file_ready_200746a8')!=0x200746a8:raise RuntimeError('ready-cell address changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-storage-unlink-47498c.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if len(before)!=191 or len(after)!=192 or before-after!={'audio_tracepoint_storage_unlink_47498c'} or after-before!=ADDED:raise RuntimeError((len(before),len(after),before-after,after-before))
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_UNLINK_FACADE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),'native_c_cases':72,'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),'placement_address':'0x200746a8','section_type':'NOBITS','section_bytes':4,'payload_sha256':PINNED,'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':sorted(OWNED),'unresolved_before':191,'unresolved_after':192,'imports_resolved':['audio_tracepoint_storage_unlink_47498c'],'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Errno-location and LittleFS remove children remain imports.','Readiness cell is a bounded NOLOAD reservation; startup value and whole-image placement remain open.','Physical NOR filesystem behavior unproved.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
