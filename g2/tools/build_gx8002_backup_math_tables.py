# SPDX-License-Identifier: MIT
"""Build source-generated arithmetic data on macOS and verify original layout."""
import json,subprocess
from generate_gx8002_backup_math_tables import generate
from build_gx8002_backup_platform_config import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build():
    out=ROOT/'build/gx8002-backup-math-tables';out.mkdir(exist_ok=True)
    source,evidence=generate();(out/'tables.c').write_text(source)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(out/'tables.c'),'-o',str(out/'tables.o')],check=True)
    expected={'.complex_coefficients':(0x4cf14,768),'.bit_reverse':(0x4cd34,480),'.q14_pairs':(0x4da18,1024),'.bit_lengths':(0x4df14,256)}
    (out/'tables.ld').write_text('SECTIONS {\n'+''.join(f'{name} {offset-0x3b940+0x10003000:#x} : {{ *({name}) }}\n' for name,(offset,size) in expected.items())+'}\n')
    path=out/'tables.elf';subprocess.run([pre+'ld','-T',str(out/'tables.ld'),str(out/'tables.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'arithmetic data');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,(offset,size) in expected.items():
        s=next(s for s in elf.sections if s['name']==name);body=elf.contents(s)
        assert len(body)==size and body==stock[offset:offset+size] and not elf.relocations(s['index'])
        rows.append({'section':name,'offset':offset,'bytes':size,'sha256':sha(body)})
    report={'generation':evidence,'source_sha256':sha(source.encode()),'sections':rows,'source_admitted':False,
            'limits':['Decimal generation agrees at 80 and 110 digits with rounding margin checked. This is reproducibility evidence, not a formal numerical-error proof. Runtime consumers and source admission remain pending.']}
    (ROOT/'docs/research/gx8002-backup-math-tables-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
