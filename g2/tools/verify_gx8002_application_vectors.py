# SPDX-License-Identifier: MIT
"""Compile and validate the application SRAM vector routing table."""
import json,struct,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def verify():
    out=ROOT/'build/gx8002-application-vectors';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_application_vectors.c'
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([prefix+'gcc',*FLAGS,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_application_reset':0x10023500,'open_cfw_gx8002_exception_entry':0x10023640,'open_cfw_gx8002_irq_entry':0x10025574}
    script=out/'candidate.ld';script.write_text('SECTIONS { .rodata.vectors 0x10023400 : { *(.rodata.open_cfw_gx8002_application_vectors) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in bindings.items()))
    target=out/'candidate.elf';subprocess.run([prefix+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1;section=sections[0];data=elf.contents(section)
    assert section['address']==0x10023400 and not section['flags']&4 and not elf.relocations(section['index'])
    symbols={s['name']:s['value'] for s in elf.symbols()}
    assert all(symbols[k]==v for k,v in bindings.items())
    words=struct.unpack('<64I',data)
    expected=tuple([bindings['open_cfw_gx8002_application_reset']]+[bindings['open_cfw_gx8002_exception_entry']]*31+[bindings['open_cfw_gx8002_irq_entry']]*32)
    assert words==expected
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA and data==stock[0x15414:0x15514]
    return {'candidate':{'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(data),'compiled_sha256':sha(data),'bindings':bindings},'cases':64,'limits':['Vector routing/data verified; target bodies and hardware dispatch are qualified separately.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-application-vectors-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
