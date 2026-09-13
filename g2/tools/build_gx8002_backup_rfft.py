# SPDX-License-Identifier: MIT
"""Build recovered RFFT dispatch against authenticated upstream types."""
import json,subprocess
from build_gx8002_backup_fft_descriptors import build as descriptors,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build(extra_flags=('-fno-tree-loop-optimize',)):
    evidence=descriptors();out=ROOT/'build/gx8002-backup-rfft';out.mkdir(exist_ok=True)
    types=(ROOT/'build/gx8002-backup-fft-descriptors/descriptors.c').read_text().split('extern const q15_t')[0]
    (out/'fft_types.h').write_text(types)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_rfft.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*extra_flags,'-I',str(out),'-c',str(source),'-o',str(out/'rfft.o')],check=True)
    bindings={'backup_cfft':0x47b14,'backup_split_forward':0x47914,'backup_split_inverse':0x479a8}
    (out/'rfft.ld').write_text('SECTIONS { .text 0x1000ef64 : { *(.text.open_cfw_gx8002_backup_rfft) } }\n'+''.join(f'{name} = {offset-0x3b940+0x10003000:#x};\n' for name,offset in bindings.items()))
    path=out/'rfft.elf';subprocess.run([pre+'ld','-T',str(out/'rfft.ld'),str(out/'rfft.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'RFFT dispatcher');s=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(s)
    assert not elf.relocations(s['index']) and sha(IMAGE.read_bytes())==IMAGE_SHA
    (out/'rfft.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_types':evidence,'source_sha256':sha(source.read_bytes()),'flags':['-Os',*FLAGS[1:],*extra_flags],'compiled_bytes':len(body),'envelope_bytes':110,'fits':len(body)<=110,'source_admitted':False,
            'limits':['Recovered dispatcher candidate only. Volatile descriptor reads and scaling require decoded comparison; three lower transform helpers remain retained.']}
    (ROOT/'docs/research/gx8002-backup-rfft-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(build()['compiled_bytes'])
