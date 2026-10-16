#!/usr/bin/env python3
"""Bind bounded tracepoint response encoder and its mapped TX RAM."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_encode_response_5eded0.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_encoded_buffer_2037b6c0.ld'
ORACLE_SCRIPT=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_encode_response_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-encode-response-5eded0';ORACLE=OUT/'oracle.json'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-send-reply-5edfd8-5ee066/apollo-main-tracepoint-send-reply-5edfd8-5ee066.o'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED={'audio_tracepoint_encode_response_5eded0','audio_tracepoint_encoded_buffer'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def output(*a):return subprocess.check_output(a,text=True)
def names(p,flag):return {x.split()[-1] for x in output('arm-none-eabi-nm','-g',flag,str(p)).splitlines()}
def section(p,name,address=None):
 lines=[x for x in output('arm-none-eabi-readelf','-SW',str(p)).splitlines() if re.search(r'\s'+re.escape(name)+r'\s+NOBITS\s+',x)]
 if len(lines)!=1 or '000300' not in lines[0] or (address is not None and f'{address:08x}' not in lines[0]):raise RuntimeError(('section',name,lines))
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PINNED or [0x438000+i for i in range(len(blob)) if blob.startswith((0x2037b6c0).to_bytes(4,'little'),i)]!=[0x5ee898]:raise RuntimeError('payload/TX address changed')
 if 0x2037b6c0+0x300!=0x2037b9c0 or '0x2037b6c0 (NOLOAD)' not in LINKER.read_text():raise RuntimeError('TX RAM placement changed')
 subprocess.run([sys.executable,str(ORACLE_SCRIPT)],check=True,capture_output=True,text=True)
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_ENCODER_NATIVE_C' or oracle['native_c_cases']!=180 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('encoder oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_encode_response_5eded0.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED:raise RuntimeError('source definitions changed')
 section(obj,'.bss.opencfw.tracepoint.encoded')
 placed=OUT/'tracepoint-encoded-placement.elf'
 subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
 section(placed,'.opencfw.tracepoint.encoded',0x2037b6c0)
 addrs={x.split()[-1]:int(x.split()[0],16) for x in output('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
 if addrs.get('audio_tracepoint_encoded_buffer')!=0x2037b6c0:raise RuntimeError('placed symbol changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-encode-response-5eded0.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if len(before)!=194 or len(after)!=192 or before-after!=OWNED or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_ENCODER_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),'native_c_cases':180,'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),'payload_sha256':PINNED,'object_sha256':sha(obj),'placement_elf':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),'placement_address':'0x2037b6c0','section_type':'NOBITS','section_bytes':0x300,'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':sorted(OWNED),'unresolved_before':194,'unresolved_after':192,'imports_resolved':sorted(OWNED),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['The TX reservation covers the observed 0x300-byte clear span; final whole-image RAM placement and startup remain open.','Nanopb provider behavior is verified at the call boundary; whole-message encoding and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
