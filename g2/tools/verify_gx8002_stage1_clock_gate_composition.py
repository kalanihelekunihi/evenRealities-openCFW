# SPDX-License-Identifier: MIT
"""Feed compiled lookup writes into the stage1 clock gate interpreter."""
import json,struct
from build_gx8002_stage1_clock_tables import build,ROOT,Elf32,sha
from compare_gx8002_stage1_clock_lookup import execute as lookup
from compare_gx8002_stage1_platform_gate import verify as gate
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=build();path=ROOT/'build/gx8002-stage1-clock-tables/tables.elf'
    elf=Elf32(path.read_bytes(),str(path))
    table=elf.contents(next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table'))
    assert sha(table)==evidence['tables'][0]['sha256']
    ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
    code=decode((path.parent/'lookup.disassembly.txt').read_text());calls=0
    def hook(module):
        nonlocal calls
        calls+=1
        return lookup(code,0x10000138,module,0x1000,ids)
    comparison=gate(lookup_hook=hook)
    result={'lookup_build':evidence,'gate_cases':comparison['cases'],'compiled_lookup_calls':calls,
            'lookup_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'hardware_qualified':False,
            'limits':['Compiled upstream lookup result and ordered output writes supply the gate local structure; source-defined table IDs used.',
                      'Separate abstract frames and fixed table contents. Physical clock transitions, concurrency and loader/reference admission remain unqualified.']}
    (ROOT/'docs/research/gx8002-stage1-clock-gate-composition.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    r=verify();print(r['gate_cases'],'gate cases;',r['compiled_lookup_calls'],'compiled lookup calls')
