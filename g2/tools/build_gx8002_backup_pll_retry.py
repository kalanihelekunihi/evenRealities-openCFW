# SPDX-License-Identifier: MIT
"""Build complete PLL retry C and source-generated PLL state together."""
import json
import subprocess
from build_gx8002_backup_clock_source_data import build as build_data
from build_gx8002_backup_cfft import ROOT, FLAGS, sha, Elf32


def build():
    data=build_data();base=ROOT/'build/gx8002-backup-clock-source-data'
    out=ROOT/'build/gx8002-backup-pll-retry';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    src=ROOT/'components/shared/gx8002/runtime_gx8002_backup_pll_retry.c';obj=out/'retry.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-I'+str(base),'-isystem',str(sdk/'include'),'-c',str(src),'-o',str(obj)],check=True)
    ld=out/'retry.ld';ld.write_text((base/'data.ld').read_text()+'\nSECTIONS { .text 0x10018000 : { *(.text*) *(.rodata*) } }\ngx_clock_set_pll_no_block = 0x100039f4;\n')
    path=out/'retry.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),str(base/'data.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'PLL retry');prior=Elf32((base/'data.elf').read_bytes(),'PLL data')
    assert sha((base/'data.elf').read_bytes())==data['elf_sha256']
    for sec in prior.sections:
        if sec['flags']&2 and sec['size']:
            current=next(s for s in elf.sections if s['name']==sec['name'])
            assert current['address']==sec['address'] and elf.contents(current)==prior.contents(sec)
    setter_address = 0x3c334 - 0x3b940 + 0x10003000
    assert next(s['value'] for s in elf.symbols() if s['name']=='gx_clock_set_pll_no_block') == setter_address
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    section=next(s for s in elf.sections if s['name']=='.text')
    (out/'retry.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'setter_package_offset':0x3c334,'setter_runtime_address':setter_address,'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'text_and_constants_bytes':section['size'],'data_evidence':data,'source_admitted':False,'limits':['Complete five-attempt source helper with stock terminal failure loop and source-generated mutable PLL data. Absolute setter binding does not constitute executed dependency closure. Analysis address only; retry outcomes, descriptor mutations, references and integration remain pending.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-pll-retry.json').write_text(json.dumps(r,indent=2)+'\n');print(r['text_and_constants_bytes'],'PLL retry source text/constants bytes')
