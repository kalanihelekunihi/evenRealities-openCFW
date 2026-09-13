# SPDX-License-Identifier: MIT
"""Rebuild backup FFT descriptors from pinned upstream type declarations."""
import json,re,subprocess
from build_gx8002_backup_platform_config import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='include/utility/libdsp/csky_vdsp2_math.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    header=authenticated_blob(sdk/rel,blob).decode()
    out=ROOT/'build/gx8002-backup-fft-descriptors';out.mkdir(exist_ok=True)
    declarations=[]
    for name in ('csky_vdsp2_cfft_instance_q15','csky_vdsp2_rfft_instance_q15'):
        matches=re.findall(r'typedef struct\s*\{[^}]*\}\s*'+name+r';',header);assert len(matches)==1
        declarations.append(matches[0])
    source='#include <stdint.h>\n#include <stddef.h>\ntypedef int16_t q15_t;\n'+'\n'.join(declarations)+'''
extern q15_t backup_real_coefficients[];
extern const q15_t backup_complex_coefficients[];
extern const uint16_t backup_bit_reverse[];
_Static_assert(sizeof(csky_vdsp2_cfft_instance_q15)==16,"complex layout");
__attribute__((section(".complex"),used))
const csky_vdsp2_cfft_instance_q15 backup_complex_fft={256,backup_complex_coefficients,backup_bit_reverse,240};
_Static_assert(sizeof(csky_vdsp2_rfft_instance_q15)==20,"upstream layout");
_Static_assert(offsetof(csky_vdsp2_rfft_instance_q15,pTwiddleAReal)==12,"table field");
__attribute__((section(".inverse"),used))
const csky_vdsp2_rfft_instance_q15 backup_inverse={512,1,1,1,backup_real_coefficients,&backup_complex_fft};
__attribute__((section(".forward"),used))
const csky_vdsp2_rfft_instance_q15 backup_forward={512,0,1,1,backup_real_coefficients,&backup_complex_fft};
'''
    (out/'descriptors.c').write_text(source)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(out/'descriptors.c'),'-o',str(out/'descriptors.o')],check=True)
    expected={'.complex':(0x4cd24,16),'.inverse':(0x4f94c,20),'.forward':(0x4f960,20)}
    (out/'descriptors.ld').write_text('SECTIONS {\n'+''.join(f'{name} {offset-0x3b940+(0x10003000 if name==".complex" else 0x20003000):#x} : {{ *({name}) }}\n' for name,(offset,size) in expected.items())+'}\nbackup_real_coefficients = 0x100150d8;\nbackup_complex_coefficients = 0x100145d4;\nbackup_bit_reverse = 0x100143f4;\n')
    path=out/'descriptors.elf';subprocess.run([pre+'ld','-T',str(out/'descriptors.ld'),str(out/'descriptors.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'FFT descriptors');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,(offset,size) in expected.items():
        s=next(s for s in elf.sections if s['name']==name);body=elf.contents(s)
        assert len(body)==size and body==stock[offset:offset+size] and not elf.relocations(s['index'])
        rows.append({'section':name,'offset':offset,'bytes':size,'sha256':sha(body)})
    report={'sdk_commit':SDK_COMMIT,'header_blob':blob,'header_sha256':sha(header.encode()),'source_sha256':sha(source.encode()),'sections':rows,'source_admitted':False,
            'limits':['Pinned upstream descriptor types and symbolic table bindings match stock. Complex coefficient/reversal tables, transform consumers and loader qualification remain pending.']}
    (ROOT/'docs/research/gx8002-backup-fft-descriptors-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
