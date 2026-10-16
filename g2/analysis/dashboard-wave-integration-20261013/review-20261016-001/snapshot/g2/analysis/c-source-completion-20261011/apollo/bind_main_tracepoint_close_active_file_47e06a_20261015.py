#!/usr/bin/env python3
"""Bind stock active-file close/clear wrapper and pointer slot into Main."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_close_active_file_47e06a.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_active_file_handle_20074ae0.ld'
ORACLE_SCRIPT=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_close_active_file_47e06a_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-close-active-file-47e06a';ORACLE=OUT/'oracle.json'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-format-file-path-5edba2/apollo-main-tracepoint-format-file-path-5edba2.o'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED={'audio_tracepoint_storage_lock_47e088','audio_tracepoint_close_active_file_47e06a','audio_tracepoint_active_file_handle'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def output(*a):return subprocess.check_output(a,text=True)
def names(p,flag):return {x.split()[-1] for x in output('arm-none-eabi-nm','-g',flag,str(p)).splitlines()}
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PINNED or [0x438000+i for i in range(len(blob)) if blob.startswith((0x20074ae0).to_bytes(4,'little'),i)]!=[0x47e2c0]:raise RuntimeError('stock active-file slot changed')
 if '0x20074ae0 (NOLOAD)' not in LINKER.read_text():raise RuntimeError('active-file placement changed')
 subprocess.run([sys.executable,str(ORACLE_SCRIPT)],check=True,capture_output=True,text=True)
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_ACTIVE_FILE_NATIVE_C' or oracle['native_c_cases']!=8 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('active-file oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_close_active_file_47e06a.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED or names(obj,'-u')!={'audio_file_close'}:raise RuntimeError('source symbols changed')
 sections=output('arm-none-eabi-readelf','-SW',str(obj))
 if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.active_file\s+NOBITS\s+',x) and '000004' in x for x in sections.splitlines()):raise RuntimeError('active-file NOBITS size changed')
 placed=OUT/'tracepoint-active-file-placement.o'
 subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
 addrs={x.split()[-1]:int(x.split()[0],16) for x in output('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
 if addrs.get('audio_tracepoint_active_file_handle')!=0x20074ae0:raise RuntimeError('active-file slot address changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-close-active-file-47e06a.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if len(before)!=192 or len(after)!=191 or before-after!={'audio_tracepoint_storage_lock_47e088'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_ACTIVE_FILE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),'native_c_cases':8,'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),'placement_address':'0x20074ae0','section_type':'NOBITS','section_bytes':4,'payload_sha256':PINNED,'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':sorted(OWNED),'unresolved_before':192,'unresolved_after':191,'imports_resolved':['audio_tracepoint_storage_lock_47e088'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Four-byte active-file handle slot is a bounded NOLOAD reservation; final RAM layout and startup are open.','File-close effects checked at call boundary; physical storage unproved.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
