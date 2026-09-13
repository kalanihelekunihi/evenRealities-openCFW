# SPDX-License-Identifier: MIT
"""Observe and verify actual libgcc nonoverlapping 20-byte struct copies."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    p=ROOT/'build/gx8002-exp-placed-cluster/exp.elf';data=p.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-exp-placed-cluster.json').read_text());assert sha(data)==report['elf_sha256']
    elf=Elf32(data,'copy');symbols={s['name']:s['value'] for s in elf.symbols()}
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(p)],text=True))
    entry=symbols['memcpy'];calls=[pc for pc,(op,args,w) in code.items() if op=='bsr' and int(args,0)==entry];assert len(calls)==1
    after=calls[0]+code[calls[0]][2];cases=0
    for name in ('__adddf3','__subdf3'):
        for a in (0,1<<63):
            for b in (0,1<<63):
                trace={entry:[],after:[]}
                execute(code,symbols[name],bytes(20),arguments=[0,a>>32,0,b>>32],return_pair=True,trace=trace)
                assert len(trace[entry])==len(trace[after])==1
                before=trace[entry][0];end=trace[after][0];r=before['registers'];dst,src,n=r['r0'],r['r1'],r['r2']
                assert n==20 and (dst+n<=src or src+n<=dst)
                wanted=bytes(before['memory'][src+i] for i in range(n))
                assert bytes(end['memory'][dst+i] for i in range(n))==wanted
                assert end['registers']['r0']==dst
                assert all(end['memory'][a]==v for a,v in before['memory'].items() if not dst<=a<dst+n)
                cases+=1
    result={'source_elf_sha256':sha(data),'actual_copy_calls':cases,'bytes_per_call':20,'source_admitted':False,'limits':['Actual add/subtract struct-copy context, full copied fields and no unrelated writes verified. General-purpose copy/MMIO use not qualified.']}
    (ROOT/'docs/research/gx8002-arithmetic-copy-calls.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
