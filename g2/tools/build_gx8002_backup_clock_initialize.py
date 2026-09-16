# SPDX-License-Identifier: MIT
"""Build the complete reconstructed backup clock initializer and its setup helpers."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT, FLAGS, sha, Elf32
from build_gx8002_backup_clock_module_initialize import build as modules
from build_gx8002_backup_clock_dividers import build as dividers
from build_gx8002_backup_pll_retry import build as retry


def build():
    evidence={'modules':modules(),'dividers':dividers(),'retry':retry()}
    out=ROOT/'build/gx8002-backup-clock-initialize';out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-backup-clock-source-data';sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_clock_initialize.c';obj=out/'clock.o'
    inputs=[source,ROOT/'build/gx8002-backup-clock-module-initialize/modules.c',ROOT/'components/shared/gx8002/runtime_gx8002_backup_clock_dividers.c',ROOT/'components/shared/gx8002/runtime_gx8002_backup_pll_retry.c']
    combined='\n'.join(p.read_text() for p in inputs)
    # These setup helpers have no external callers in this source cluster.
    # Expose their complete bodies to the compiler for ordinary C inlining.
    for name in ('open_cfw_gx8002_backup_clock_module_initialize','open_cfw_gx8002_backup_clock_dividers','open_cfw_gx8002_backup_pll_retry'):
        combined=combined.replace('extern void '+name,'static inline void '+name).replace('\nvoid '+name,'\nstatic inline void '+name)
    unit=out/'combined.c';unit.write_text(combined)
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-I'+str(base),'-isystem',str(sdk/'include'),'-c',str(unit),'-o',str(obj)],check=True)
    bindings={'gx_clock_set_div':0x3c0c8,'gx_clock_set_dto':0x3c228,'gx_clock_set_module_source':0x3bf00,'gx_clock_set_source':0x3bee0,'gx_clock_set_pll':0x3c448,'gx_clock_set_pll_no_block':0x3c334,'gx_clock_set_module_enable':0x3c528,'open_cfw_gx8002_backup_preserve_memory':0x3c93c,'open_cfw_gx8002_backup_trim_state':0x3c95c,'open_cfw_gx8002_backup_ldo_control':0x40a34}
    ld=out/'clock.ld';ld.write_text((base/'data.ld').read_text()+'\nSECTIONS { .text 0x10003294 : { *(.text*) *(.rodata*) } }\nopen_cfw_gx8002_saved_clock_gates = 0x20017394;\n'+''.join(f'{name} = {address-0x3b940+0x10003000:#x};\n' for name,address in bindings.items()))
    objects=[obj,base/'data.o']
    path=out/'clock.elf';subprocess.run([pre+'ld','-T',str(ld),*[str(o) for o in objects],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'clock');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    dataelf=Elf32((base/'data.elf').read_bytes(),'data')
    for section in dataelf.sections:
        if section['flags']&2 and section['size']:
            current=next(s for s in elf.sections if s['name']==section['name'])
            assert current['address']==section['address'] and elf.contents(current)==dataelf.contents(section)
    (out/'clock.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    size=next(s['size'] for s in elf.sections if s['name']=='.text')
    return {'combined_source_sha256':sha(unit.read_bytes()),'source_inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for p in inputs],'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'entry_address':0x10003294,'text_and_constants_bytes':size,'stock_initializer_envelope_bytes':576,'fits_stock_envelope':size<=576,'dependencies':evidence,'absolute_bindings_package_offsets':bindings,'source_admitted':False,'limits':['Complete initializer plus source module/divider/retry helpers and generated clock data. Linked at original clock entry; firmware integration pending. Low-level clock, trim, preservation and analog helpers remain absolute bindings. Full control-flow execution, incoming reference qualification and integration pending.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-clock-initialize.json').write_text(json.dumps(r,indent=2)+'\n');print(r['text_and_constants_bytes'],'clock source bytes; fits:',r['fits_stock_envelope'])
