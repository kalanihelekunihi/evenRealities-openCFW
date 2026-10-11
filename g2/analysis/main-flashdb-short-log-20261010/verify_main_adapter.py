#!/usr/bin/env python3
"""Clang archive-toolchain oracle for Main tail branch into audio-owned logger."""
import hashlib, importlib.util, itertools, json, subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn.arm_const import UC_ARM_REG_R0

H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('short_log_oracle', H/'verify.py')
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
R = oracle.R
adapter = R/'g2/components/main/flashdb_shortlog_adapter_20261010/adapter.c'
audio = R/'g2/components/audio/source_candidate_20261010/simple_log_provider.c'
elf = H/'main-adapter-audio-log.elf'
cc = subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
cmd = [cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz',
       '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
       '-Wl,-e,g2_flashdb_candidate_compress',
       '-Wl,--defsym=audio_log_policy=0x44a9af',
       '-Wl,--defsym=audio_log_lock=0x441751',
       '-Wl,--defsym=audio_log_unlock=0x441711',
       '-Wl,--defsym=audio_log_format=0x43cb85',
       '-Wl,--defsym=audio_log_lock_state=0x20074388',
       str(adapter),str(audio),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f)
 oracle.entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_candidate_compress')
 oracle.segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
oracle.source_mrs=0x10001020
oracle.source_mrs_reg=UC_ARM_REG_R0
assert bytes(oracle.segs[0][1][:4]) == bytes.fromhex('00f000b8')  # Thumb B.W tail branch
cases=0
for policy,ipsr,lock,take,token,category in itertools.product((0,1,255),(0,3),(0,0x20050000),(0,1,2),(0,0xffffffff,0x04800000),(0,0x3fffff,0xabcdef01)):
 case=dict(policy=policy,ipsr=ipsr,lock=lock,take=take,token=token,category=category)
 a,b=oracle.run(False,case),oracle.run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases+=1
receipt={'status':'PASS','cases':cases,'compiler':cc,'compile':cmd,
         'adapter_sha256':hashlib.sha256(adapter.read_bytes()).hexdigest(),
         'audio_provider_sha256':hashlib.sha256(audio.read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'limits':'Bounded public-entry comparison with synthetic policy/IPSR/lock/formatter providers. Tail branch preserves register and stack arguments; production lower providers remain explicit.'}
(H/'adapter-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS adapter',cases)
