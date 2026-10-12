#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4];T=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-objdump';B=R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin';assert hashlib.sha256(B.read_bytes()).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
s=R/'g2/components/em9305/qpc_scheduler_candidate/initializer_lowers/init_mode_frame48.c';src=s.read_text()
n=subprocess.check_output([str(T),'-D','-b','binary','-EL','-m','arc:ARCv2','-Mcpu=em,dsp','--adjust-vma=0x302400','--start-address=0x323028','--stop-address=0x3230f4',str(B)],text=True);(P/'wide-callee-native.txt').write_text(n)
assert 'enter_s\t[r13-r21,fp,blink]' in n and 'sub_s\tsp,sp,0x30' in n
frame=11*4+48;assert frame==92
loads={0:('r17',92),4:('r16',96),8:('r14',100),12:('r1',104),16:('r0',108),20:('r1',112)}
for off,(reg,callee) in loads.items():
 assert callee==frame+off
 assert re.search(r'ld(?:_s)?\s+'+reg+r',\[sp,(?:'+str(callee)+'|0x'+format(callee,'x')+r')\]',src)
 assert re.search(r'ld(?:_s)?\t'+reg+r',\[sp,(?:'+str(callee)+'|0x'+format(callee,'x')+r')\]',n)
caller=(P/'source.c').read_text()
for instruction in ['st_s r15,[sp,0]','st_s r12,[sp,0x4]','st 0,[sp,8]','st r11,[sp,12]','st_s r3,[sp,0x10]','st_s r2,[sp,0x14]','bl.d opencfw_em9305_mode_event_323028']:assert instruction in caller
r={'status':'PASS_SELECTED_WIDE_CALL_STACK_LAYOUT','saved_register_bytes':44,'local_bytes':48,'incoming_stack_base':92,'caller_stack_offsets':list(loads),'stack_words':6,'caller_source_sha256':hashlib.sha256((P/'source.c').read_bytes()).hexdigest(),'callee_source_sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'limits':['Confirms six stack stores and native/selected callee load layout.','Live argument values, register preservation through nested calls and hardware remain separate.']};(P/'wide-call-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
