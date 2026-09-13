# SPDX-License-Identifier: MIT
"""Whole decoded module switching with modeled or decoded nested helpers."""
import json,random,subprocess
from itertools import product
from oracle_gx8002_clock_module_source import expected
from load_gx8002_clock_context import load,ROOT
from execute_gx8002_clock_module_source import execute
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha

def verify(nested=False):
    table,context=load();modules={x['module']:x for x in context['modules']};codes={};hashes={}
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x16bf4','--stop-address=0x16d84',str(p)],text=True))
    for name in ('clock-module-source','clock-module-source-fixed'):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';e=Elf32(p.read_bytes(),name);report=json.loads((ROOT/f'docs/research/gx8002-{name}-candidate.json').read_text());assert sha(e.contents(next(s for s in e.sections if s['name']=='.text')))==report['compiled_sha256'];hashes[name]=sha(p.read_bytes());codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True))
    helper_options={};helper_evidence={}
    if nested:
        from load_gx8002_clock_decoded_helpers import load_helpers
        helper_options,helper_evidence=load_helpers()
    def run(*args):return execute(*args,**helper_options)
    rng=random.Random(896);cases=0;differences=[]
    for module in range(26):
        for source in range(10):
            initials=[0,0xffffffff,0xaaaaaaaa,0x55555555,rng.getrandbits(32)]
            if module in (16,19):
                bits=sorted(set(context['modules'][module+i]['gate_all_offset'] for i in (1,2))|set(modules[module+i]['gate_all_offset'] for i in (1,2)))
                initials.extend(sum(v<<b for b,v in zip(bits,values)) for values in product((0,1),repeat=len(bits)))
            for initial in initials:
                mmio={b+o:initial for b in (0xa0010000,0xa0300000) for o in (0x18,0x1c,0x20,0x88,0x8c)}
                if module in (16,19):mmio[0xa0300088]=0 if source==1 else 0xffffffff
                stock=run(old,0x16bf4,module,source,table,modules,mmio)
                baseline=run(codes['clock-module-source'],0x10024be0,module,source,table,modules,mmio)
                assert stock==baseline,(module,source,hex(initial),stock,baseline)
                fixed=run(codes['clock-module-source-fixed'],0x10024be0,module,source,table,modules,mmio)
                assert fixed==expected(module,source,modules,mmio),(module,source,hex(initial),fixed,expected(module,source,modules,mmio))
                if fixed!=stock:
                    assert module in (16,19),(module,source)
                    differences.append({'module':module,'source':source,'initial':hex(initial),'stock_trace':stock[2],'fixed_trace':fixed[2]})
                cases+=1
    audio_cases=0
    for module,source,gate_bits,clock_bits in product((7,8),range(10),range(8),range(16)):
        gate=sum(((gate_bits>>i)&1)<<b for i,b in enumerate((5,6,19)))
        selected=sum(((clock_bits>>i)&1)<<b for i,b in enumerate((6,19,20,21)))
        mmio={b+o:0 for b in (0xa0010000,0xa0300000) for o in (0x18,0x1c,0x20,0x88,0x8c)}
        mmio[0xa0010018]=gate;mmio[0xa001008c]=selected
        wanted=expected(module,source,modules,mmio)
        for program,entry in ((old,0x16bf4),(codes['clock-module-source'],0x10024be0),(codes['clock-module-source-fixed'],0x10024be0)):
            assert run(program,entry,module,source,table,modules,mmio)==wanted,(module,source,gate_bits,clock_bits)
        audio_cases+=1;cases+=1
    return {'cases':cases,'nested_helpers':helper_evidence,'targeted_audio_cases':audio_cases,'differences':differences,'elf_sha256':hashes,'context':context,'limits':[('Complete decoded outer routines and nested lookup/register helpers with marshalled private frames.' if nested else 'Complete decoded outer routines; lookup/register helpers modeled against authenticated table.')+' Gate SET/CLR modeled as updating inhibit state. Independent ID-based transition model checked; physical timing remains outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-module-source-paths.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],len(r['differences']))
