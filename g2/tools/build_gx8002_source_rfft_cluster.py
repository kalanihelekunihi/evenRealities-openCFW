# SPDX-License-Identifier: MIT
"""Self-contained source RFFT link; experimental layout, not a firmware patch."""
import json,re,subprocess
from pathlib import Path
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha,SDK_COMMIT,authenticated_blob
from generate_gx8002_backup_math_tables import generate
from verify_gx8002_memcpy_source import decode

def build(shared_radix4=False,shared_by2=False,generated_reverse=False):
    out=ROOT/('build/gx8002-source-rfft-generated-reverse-cluster' if generated_reverse else 'build/gx8002-source-rfft-double-shared-cluster' if shared_by2 else 'build/gx8002-source-rfft-shared-cluster' if shared_radix4 else 'build/gx8002-source-rfft-cluster');out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='include/utility/libdsp/csky_vdsp2_math.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    header=authenticated_blob(sdk/rel,blob).decode()
    types=re.findall(r'typedef struct\s*\{[^}]*\}\s*csky_vdsp2_cfft_instance_q15;',header);assert len(types)==1
    real_types=re.findall(r'typedef struct\s*\{[^}]*\}\s*csky_vdsp2_rfft_instance_q15;',header);assert len(real_types)==1
    (out/'fft_types.h').write_text('#include <stdint.h>\ntypedef int16_t q15_t;\n'+types[0]+'\n'+real_types[0]+'\n')
    tables,generation=generate()
    tables=tables.replace('open_cfw_gx8002_backup_bit_reverse[','source_cfft_bit_reverse_table[')
    (out/'tables.c').write_text(tables)
    descriptor='''#include "fft_types.h"
extern const int16_t open_cfw_gx8002_backup_complex_coefficients[];
extern const uint16_t source_cfft_bit_reverse_table[];
__attribute__((section(".descriptor"),used))
const csky_vdsp2_cfft_instance_q15 source_cfft_256={256,open_cfw_gx8002_backup_complex_coefficients,source_cfft_bit_reverse_table,240};
extern const int16_t open_cfw_gx8002_backup_q14_pairs[];
__attribute__((section(".descriptor"),used))
const csky_vdsp2_rfft_instance_q15 source_rfft_forward={512,0,1,1,(int16_t *)open_cfw_gx8002_backup_q14_pairs,&source_cfft_256};
__attribute__((section(".descriptor"),used))
const csky_vdsp2_rfft_instance_q15 source_rfft_inverse={512,1,1,1,(int16_t *)open_cfw_gx8002_backup_q14_pairs,&source_cfft_256};

'''
    if generated_reverse:
        assert shared_radix4 and shared_by2
        descriptor=descriptor.replace(',source_cfft_bit_reverse_table,240}',',0,240}')
    (out/'descriptor.c').write_text(descriptor)
    jobs=[('cfft',ROOT/'components/shared/gx8002/runtime_gx8002_backup_cfft.c',()),('reverse',ROOT/'components/shared/gx8002/runtime_gx8002_backup_bit_reverse.c',()),('tables',out/'tables.c',()),('descriptor',out/'descriptor.c',())]
    if generated_reverse:
        jobs[1]=('reverse',ROOT/'components/shared/gx8002/runtime_gx8002_backup_bit_reverse_256.c',())
    jobs.append(('rfft',ROOT/'components/shared/gx8002/runtime_gx8002_backup_rfft.c',('-fno-tree-loop-optimize',)))
    if shared_radix4:jobs.append(('radix4_shared',ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4_shared.c',('-fno-caller-saves',)))
    if shared_by2:jobs.append(('radix4_by2_shared',ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4_by2_shared.c',('-fno-caller-saves',)))
    for kind in ('radix4','radix4_by2','split'):
        if (kind=='radix4' and shared_radix4) or (kind=='radix4_by2' and shared_by2):continue
        for inverse in (0,1):jobs.append((kind+str(inverse),ROOT/f'components/shared/gx8002/runtime_gx8002_backup_{kind}.c',('-DINVERSE='+str(inverse),'-fno-caller-saves')))
    objects=[];sources=[]
    for name,source,extra in jobs:
        obj=out/(name+'.o');objects.append(obj)
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*extra,'-I',str(out),'-c',str(source),'-o',str(obj)],check=True)
        sources.append({'name':name,'source':str(source.relative_to(ROOT)),'sha256':sha(source.read_bytes()),'extra_flags':list(extra)})
    aliases=('radix4','radix4_inverse','radix4_by2','radix4_by2_inverse','bit_reverse','cfft','split_forward','split_inverse')
    script='''ENTRY(open_cfw_gx8002_backup_rfft)
SECTIONS {
 .text 0x10010000 : { *(.text*) }
 .rodata ALIGN(4) : { KEEP(*(.descriptor)) *(.complex_coefficients) *(.bit_reverse) *(.q14_pairs) *(.rodata*) }
 /DISCARD/ : { *(.bit_lengths) }
}
'''+''.join(f'backup_{name} = open_cfw_gx8002_backup_{name};\n' for name in aliases)
    if generated_reverse:
        script=script.replace(' *(.bit_reverse)', '').replace('*(.bit_lengths)', '*(.bit_lengths) *(.bit_reverse)')
    (out/'cluster.ld').write_text(script)
    path=out/'cluster.elf';subprocess.run([pre+'ld','--gc-sections','-T',str(out/'cluster.ld'),*[str(p) for p in objects],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'source CFFT cluster');allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert not any(s['section']==0 and s['name'] for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert {s['name'] for s in allocated}=={'.text','.rodata'}
    symbols={s['name']:s for s in elf.symbols() if s['name']}
    text=next(s for s in allocated if s['name']=='.text')
    for name in aliases:
        assert symbols['backup_'+name]['value']==symbols['open_cfw_gx8002_backup_'+name]['value']
        assert text['address']<=symbols['backup_'+name]['value']<text['address']+text['size']
    rodata=next(s for s in allocated if s['name']=='.rodata');body=elf.contents(rodata)
    off=symbols['source_cfft_256']['value']-rodata['address'];desc=body[off:off+16]
    assert int.from_bytes(desc[:2],'little')==256 and int.from_bytes(desc[12:14],'little')==240
    assert int.from_bytes(desc[4:8],'little')==symbols['open_cfw_gx8002_backup_complex_coefficients']['value']
    assert int.from_bytes(desc[8:12],'little')==(0 if generated_reverse else symbols['source_cfft_bit_reverse_table']['value'])
    if generated_reverse:assert 'source_cfft_bit_reverse_table' not in symbols
    for name,inverse in (('source_rfft_forward',0),('source_rfft_inverse',1)):
        off=symbols[name]['value']-rodata['address'];desc=body[off:off+20]
        assert int.from_bytes(desc[:4],'little')==512 and desc[4:6]==bytes((inverse,1))
        assert int.from_bytes(desc[8:12],'little')==1
        assert int.from_bytes(desc[12:16],'little')==symbols['open_cfw_gx8002_backup_q14_pairs']['value']
        assert int.from_bytes(desc[16:20],'little')==symbols['source_cfft_256']['value']
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    decoded=decode((out/'cluster.disassembly.txt').read_text());calls=[]
    for pc,(op,args,width) in decoded.items():
        if op=='bsr':
            target=int(args,0);assert target in decoded
            assert text['address']<=target<text['address']+text['size']
            calls.append({'pc':pc,'target':target})
    report={'generated_reverse_256_only':generated_reverse,'sdk_commit':SDK_COMMIT,'upstream_header_blob':blob,'sources':sources,'generation':generation,'elf_sha256':sha(path.read_bytes()),'code_bytes':text['size'],'data_bytes':rodata['size'],'entry':symbols['open_cfw_gx8002_backup_rfft']['value'],'retained_binary_inputs':[],'direct_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Standalone RFFT component artifact only. Chosen analysis address is not validated firmware placement.','All RFFT/CFFT arithmetic helpers and generated tables linked to source; no unresolved symbols or relocations. Full linked execution and loader qualification pending.','All non-FFT firmware functionality remains outside this artifact.']}
    if generated_reverse:
        report['limits'].append('Bit reversal specialized to immutable source_cfft_256 inside the closed RFFT512 component. Null table pointer is never dereferenced. Generic/custom-table CFFT calls are outside this variant contract; external entry closure must be established before placement.')
    (ROOT/('docs/research/gx8002-source-rfft-generated-reverse-cluster.json' if generated_reverse else 'docs/research/gx8002-source-rfft-double-shared-cluster.json' if shared_by2 else 'docs/research/gx8002-source-rfft-shared-cluster.json' if shared_radix4 else 'docs/research/gx8002-source-rfft-cluster.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    r=build();print(r['code_bytes'],r['data_bytes'])
