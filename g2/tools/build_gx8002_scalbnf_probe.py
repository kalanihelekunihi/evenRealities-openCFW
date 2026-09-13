# SPDX-License-Identifier: MIT
"""Compile recovered scaling C; analysis layout until fit and execution are qualified."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_analog_source import FLAGS

def build(corrected=False,placed=False):
    assert not placed or corrected
    out=ROOT/('build/gx8002-scalbnf-placed' if placed else 'build/gx8002-scalbnf-corrected' if corrected else 'build/gx8002-scalbnf-probe');out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    sources=[ROOT/'components/shared/gx8002'/n for n in ('runtime_gx8002_scalbnf.c','runtime_gx8002_float_sign.c')];objects=[]
    if corrected:
        original=sources[0].read_text();assert original.count('exponent < -22')==1
        patched=out/'scale-corrected.c';patched.write_text(original.replace('exponent < -22','exponent < -24'))
        sources[0]=patched
    for i,source in enumerate(sources):
        obj=out/f'source{i}.o';objects.append(str(obj));subprocess.run([pre+'gcc',*FLAGS,'-ffp-contract=off','-c',str(source),'-o',str(obj)],check=True)
    ld=out/'scale.ld';ld.write_text('SECTIONS { .scale 0x10019000 : { *(.text.open_cfw_gx8002_scale_float) } .sign 0x10019200 : { *(.text.open_cfw_gx8002_copy_float_sign) } /DISCARD/ : { *(.text.open_cfw_gx8002_float_absolute) } }\n')
    if placed:
        script=ld.read_text().replace('0x10019000',hex(0x49ad4-0x3b940+0x10003000)).replace('0x10019200',hex(0x49be4-0x3b940+0x10003000))
        ld.write_text(script+'ASSERT(SIZEOF(.scale) <= 260, "scale overflow")\nASSERT(SIZEOF(.sign) <= 32, "sign overflow")\n')
    path=out/'scale.elf';subprocess.run([pre+'ld','-T',str(ld),*objects,'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'scale');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    (out/'scale.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'placed':placed,'corrected':corrected,'correction':'Retain exponent -24 and -23 for final subnormal rounding' if corrected else None,'elf_sha256':sha(path.read_bytes()),'sources':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sources},'allocated':[(s['name'],s['size']) for s in e.sections if s['flags']&2 and s['size']],'source_admitted':False,'limits':['Analysis build only. Stock behavior, FP flags and physical placement remain unverified; upstream provenance unconfirmed.']}
    (ROOT/('docs/research/gx8002-scalbnf-placed.json' if placed else 'docs/research/gx8002-scalbnf-corrected.json' if corrected else 'docs/research/gx8002-scalbnf-probe.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
