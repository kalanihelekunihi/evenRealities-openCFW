#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4]
b=(R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
t=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-objdump'
def decode(start,end):
 s=subprocess.check_output([str(t),'-D','-b','binary','-EL','-m','arc:ARCv2','-Mcpu=em,dsp','--adjust-vma=0x302400',f'--start-address={start}',f'--stop-address={end}',str(R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin')],text=True)
 return {int(v[0].strip()[:-1],16):' '.join(x.strip() for x in v[2:]) for l in s.splitlines() if len(v:=l.split('\t'))>=3 and v[0].strip().endswith(':')}
setter=decode(0x30aec8,0x30aed4);expected={0x30aec8:'mov_s r2,0x805b10',0x30aece:'st_s r1,[r2,0x4]',0x30aed0:'j_s.d [blink]',0x30aed2:'st_s r0,[r2,0]'};assert setter==expected
seed=decode(0x30a7bc,0x30a800);assert seed[0x30a7be]=='mov_s r0,0x32e3e0' and seed[0x30a7c4]=='mov_s r1,0x32e3bc';assert seed[0x30a7ca].startswith('bl ') and '0x30aec8' in seed[0x30a7ca]
s=(R/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();start=s.index('uint32_t opencfw_em9305_ll_callback_pair(');end=s.index('/* Native0x30a800. */',start);body=s[start:end]
for token in ['0x805b14u=(uint32_t)second','0x805b10u=(uint32_t)first','opencfw_em9305_dispatch_32e3e0','opencfw_em9305_dispatch_32e3bc']:assert token in body
r={'status':'PASS_NATIVE_SETTER_AND_SEED_TARGET_BINDING_TO_SELECTED_SOURCE','setter':'30aec8','seed':'30a7bc','writes':[{'cell':'805b10','target':'32e3e0'},{'cell':'805b14','target':'32e3bc'}],'selected_source_slice_sha256':hashlib.sha256(body.encode()).hexdigest(),'limits':['Static setter/seed binding; all callers, initialization ordering and later overwrites remain open. Target provider ABI and hardware execution are separate gates.']};(P/'pair-owner-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
