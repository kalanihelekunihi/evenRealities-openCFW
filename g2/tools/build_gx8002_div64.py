# SPDX-License-Identifier: MIT
"""Compile pinned Nationalchip division source on macOS without binary extraction."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'; commit='8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5'
    assert subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()==commit
    path=sdk/'base/src/div64.c';source=path.read_bytes()
    assert source==subprocess.check_output(['git','-C',str(sdk),'show',commit+':base/src/div64.c'])
    out=ROOT/'build/gx8002-div64';out.mkdir(exist_ok=True)
    # Keep the output pointer in the ABI input register through the final store.
    # Empty compiler constraint emits no instruction and changes no arithmetic.
    original='\t*n = res;'
    assert source.decode().count(original)==1
    adapted=source.decode().replace(original, '\tregister uint64_t *output __asm__("r0") = n;\n\t__asm__("" : "+r"(output));\n\t*output = res;')
    adapted_path=out/'div64-adapted.c';adapted_path.write_text(adapted)
    # Supply platform integer types only.
    (out/'types.h').write_text('#include <stdint.h>\n');(out/'div64.h').write_text('#include <stdint.h>\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I',str(out),'-c',str(adapted_path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x102098b4 : { *(.text.__div64_32) } }\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,offset,size in (('.text',0x12e40,168),):
        section=next(s for s in elf.sections if s['name']==name);data=elf.contents(section)
        rows.append({'section':name,'compiled_bytes':len(data),'envelope_bytes':size,'fits':len(data)<=size,'byte_exact':data==stock[offset:offset+size],'compiled_sha256':sha(data)})
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    report={'upstream_commit':commit,'upstream_path':'base/src/div64.c','upstream_sha256':sha(source),'adapted_source_sha256':sha(adapted.encode()),'adaptation':'Constrain output pointer to ABI r0 before final store','flags':flags,'sections':rows,'source_admitted':False,'limits':['Pinned source candidate; decoded behavioral and ownership qualification outstanding.']}
    (ROOT/'docs/research/gx8002-div64-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
