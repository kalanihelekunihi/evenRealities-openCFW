# SPDX-License-Identifier: MIT
"""Compile pinned ARM/T-HEAD Q15 fill C with the native macOS compiler."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    relative='utility/libdsp/Source/SupportFunctions/csky_fill_q15.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
    payload=subprocess.check_output(['git','-C',str(sdk),'cat-file','blob',blob])
    out=ROOT/'build/gx8002-beam-fill-q15';out.mkdir(exist_ok=True)
    (out/'csky_fill_q15.c').write_bytes(payload)
    (out/'csky_math.h').write_text('#include <stdint.h>\ntypedef int16_t q15_t;\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-DCSKY_MATH_NO_SIMD','-Dcsky_fill_q15=beam_fill_q15','-I',str(out),'-c',str(out/'csky_fill_q15.c'),'-o',str(out/'fill.o')],check=True)
    (out/'fill.ld').write_text('SECTIONS { .beam_fill_q15 0x1000f1ac : { *(.text*) } }\n')
    target=out/'fill.elf'
    subprocess.run([pre+'ld','-T',str(out/'fill.ld'),str(out/'fill.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),'fill');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['size']<=40
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'fill.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    report={'sdk_commit':SDK_COMMIT,'upstream_path':relative,'upstream_blob':blob,'source_sha256':sha(payload),'license':'Apache-2.0','source_modifications':[],'configuration':['CSKY_MATH_NO_SIMD','csky_fill_q15=beam_fill_q15'],'header_adapter':'stdint.h and int16_t q15_t only','bytes':sections[0]['size'],'envelope_bytes':40,'fits':True,'source_admitted':False,'limits':['Standalone upstream C build; decoded fill equivalence and integration remain pending.','Scalar stores differ from stock packed store widths; overlapping/MMIO use is not qualified.']}
    (ROOT/'docs/research/gx8002-beam-fill-q15.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
