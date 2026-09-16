# SPDX-License-Identifier: MIT
"""Compose linked audio callback and linked cache invalidation instructions."""
import json,subprocess
from itertools import product
from build_gx8002_backup_denoise_record_callback import ROOT,Elf32,sha
from verify_gx8002_backup_denoise_record_callback import execute as callback
from verify_gx8002_backup_dcache_invalid_range import execute as cache,expected
from verify_gx8002_memcpy_source import decode

def verify():
    path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf';elf=Elf32(path.read_bytes(),'cluster')
    leaf=next(s for s in elf.sections if s['name']=='.dcache_invalid')
    standalone=Elf32((ROOT/'build/gx8002-backup-dcache-invalid-range/dcache-invalid-range-candidate.elf').read_bytes(),'cache')
    section=next(s for s in standalone.sections if s['name']=='.text')
    assert leaf['address']==section['address'] and elf.contents(leaf)==standalone.contents(section)
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([prefix,'-d',str(path)],text=True))
    candidate=ROOT/'build/gx8002-backup-denoise-record-callback/callback.elf'
    callback_elf=Elf32(candidate.read_bytes(),'callback')
    before=next(s for s in callback_elf.sections if s['name']=='.callback')
    after=next(s for s in elf.sections if s['name']=='.denoise_record_callback')
    assert before['address']==after['address'] and callback_elf.contents(before)==elf.contents(after)
    outer=code;cases=0
    for mics,frames,rate,length in product((0,1,2,4),(0,1,4),(1000,16000),(0,1,16)):
        writes=[];calls=[]
        def hook(pointer,size):
            trace,complete=cache(code,0x10004dd8,pointer,size,0)
            assert complete and trace==expected(pointer,size)
            writes.extend(trace);calls.append((pointer,size))
        result=callback(outer,0x1000bd54,0,7,mics,frames,rate,length,cache_hook=hook)
        size=(frames*rate*length//1000)*2
        assert result[0]==0 and calls==[(0x20050000+i*0x100,size) for i in range(mics)]
        wanted=[write for i in range(mics) for write in expected(0x20050000+i*0x100,size)]
        assert writes==wanted;cases+=1
    report={'cluster_sha256':sha(path.read_bytes()),'callback_elf_sha256':sha(candidate.read_bytes()),'cases':cases,'source_admitted':False,
            'limits':['Actual compiled callback/cache functions execute at a modeled helper boundary. Context/frame/queue helpers remain modeled.',
                      'Finite valid audio configurations; physical cache coherence and shared nested stack execution are not proven.']}
    (ROOT/'docs/research/gx8002-backup-denoise-callback-cache.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
