# SPDX-License-Identifier: MIT
"""Compose decoded cache initialization with the upstream disable candidate."""
import json,subprocess
from verify_gx8002_dcache_disable_upstream import verify as qualify,execute as disable,ROOT,sha,Elf32,decode
from execute_gx8002_cache_initialize_disable import execute

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-cache-initialize/initialize.elf'
    baseline_path=ROOT/'docs/research/gx8002-cache-initialize-source-verification.json'
    baseline=json.loads(baseline_path.read_text());elf=Elf32(path.read_bytes(),'initialize')
    for row in baseline.get('functions',[baseline]):
        section=next(s for s in elf.sections if s['name']==row['section_name'])
        assert sha(elf.contents(section))==row['compiled_sha256'] and not elf.relocations(section['index'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    caller=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    callee=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/dcache-disable-upstream-candidate.elf')],text=True))
    cases=0
    for cer in (0,1,2,3,0xffffffff,0xfffffffe,0x12345678,0x80000001):
      for status in (0,1,0xffffffff):
       for seed in (0,0x12340000,0xffff0000):
        expected=[('call',0x1002571c),('call',0x100255e4),('sync',),('sync',),('read',0xe000f000,cer),('write',0xe000f000,cer&0xfffffffe),('write',0xe000f004,1),('sync',),('sync',),('write',0xe000f014,0x20000023),('call',0x100255c4)]
        actual=execute(caller,0x10203c40,(status,0,status),seed,lambda:disable(callee,0x100255e4,cer,seed))
        assert actual==expected;cases+=1
    return {'evidence':evidence,'caller_elf_sha256':sha(path.read_bytes()),'caller_report_sha256':sha(baseline_path.read_bytes()),'composed_cases':cases,'source_admitted':False,'limits':['Decoded initialization-to-disable sequence and ABI qualified. Cache enable helpers remain modeled, CER input scripted, and no physical coherence/timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-disable-upstream-initialize.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
