# SPDX-License-Identifier: MIT
"""Build packed-sample permutation leaf; hardware loop boundary semantics pending."""
import json,subprocess
from build_gx8002_backup_platform_config import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build(extra_flags=()):
    out=ROOT/'build/gx8002-backup-bit-reverse';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_bit_reverse.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*extra_flags,'-c',str(source),'-o',str(out/'reverse.o')],check=True)
    (out/'reverse.ld').write_text('SECTIONS { .text 0x1000f824 : { *(.text.open_cfw_gx8002_backup_bit_reverse) } }\n')
    path=out/'reverse.elf';subprocess.run([pre+'ld','-T',str(out/'reverse.ld'),str(out/'reverse.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'permutation');s=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(s)
    assert not elf.relocations(s['index']) and sha(IMAGE.read_bytes())==IMAGE_SHA
    (out/'reverse.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'extra_flags':list(extra_flags),'compiled_bytes':len(body),'envelope_bytes':38,'fits':len(body)<=38,'source_admitted':False,
            'limits':['Candidate for positive descriptor counts; decoded comparison and hardware bloop zero/wrap semantics remain pending. Not admitted or integrated.']}
    (ROOT/'docs/research/gx8002-backup-bit-reverse-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
