# SPDX-License-Identifier: MIT
"""Build recovered CFFT dispatch with authenticated upstream types on macOS."""
import json,re,subprocess
from build_gx8002_backup_fft_descriptors import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='include/utility/libdsp/csky_vdsp2_math.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    header=authenticated_blob(sdk/rel,blob).decode()
    matches=re.findall(r'typedef struct\s*\{[^}]*\}\s*csky_vdsp2_cfft_instance_q15;',header);assert len(matches)==1
    out=ROOT/'build/gx8002-backup-cfft';out.mkdir(exist_ok=True)
    (out/'fft_types.h').write_text('#include <stdint.h>\ntypedef int16_t q15_t;\n'+matches[0]+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_cfft.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I',str(out),'-c',str(source),'-o',str(out/'cfft.o')],check=True)
    bindings={'backup_radix4':0x47d3c,'backup_radix4_inverse':0x47f50,'backup_radix4_by2':0x47bf4,'backup_radix4_by2_inverse':0x47c98,'backup_bit_reverse':0x48164}
    (out/'cfft.ld').write_text('SECTIONS { .text 0x1000f1d4 : { *(.text.open_cfw_gx8002_backup_cfft) } }\n'+''.join(f'{name} = {offset-0x3b940+0x10003000:#x};\n' for name,offset in bindings.items()))
    path=out/'cfft.elf';subprocess.run([pre+'ld','-T',str(out/'cfft.ld'),str(out/'cfft.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'CFFT dispatcher');s=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(s)
    assert not elf.relocations(s['index']) and sha(IMAGE.read_bytes())==IMAGE_SHA
    (out/'cfft.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'sdk_commit':SDK_COMMIT,'header_blob':blob,'header_sha256':sha(header.encode()),'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':len(body),'envelope_bytes':224,'fits':len(body)<=224,'source_admitted':False,'limits':['Dispatcher candidate; decoded behavioral comparison and loader/reference qualification pending. Five lower helpers remain retained.']}
    (ROOT/'docs/research/gx8002-backup-cfft-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(build()['compiled_bytes'])
