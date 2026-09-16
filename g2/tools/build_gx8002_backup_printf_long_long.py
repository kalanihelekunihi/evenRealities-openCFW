# SPDX-License-Identifier: MIT
"""Place authenticated SDK wide integer converter with explicit arithmetic deps."""
import json,subprocess
from build_gx8002_backup_printf_candidate import build as candidate,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA

def build():
    evidence=candidate();out=ROOT/'build/gx8002-backup-printf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'objcopy','--globalize-symbol=_ntoa_format',str(out/'printf.o'),str(out/'long-long.o')],check=True)
    bindings={'_ntoa_format':0x10008aa0,'__umoddi3':0x4a110-0x38940+0x10000000,'__udivdi3':0x49ddc-0x38940+0x10000000}
    ld='SECTIONS { .printf_long_long 0x10008d48 : { *(.text._ntoa_long_long) } /DISCARD/ : { *(.text*) *(.rodata*) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in bindings.items())
    (out/'long-long.ld').write_text(ld);path=out/'long-long.elf';subprocess.run([pre+'ld','-T',str(out/'long-long.ld'),str(out/'long-long.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'long long');sec=next(s for s in elf.sections if s['name']=='.printf_long_long');data=elf.contents(sec);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;assert len(data)<=216
    assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'long-long.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream':evidence,'bytes':len(data),'envelope_bytes':216,'bindings':bindings,'byte_exact_prefix':data==stock[0x41688:0x41688+len(data)],'source_admitted':False,'limits':['SDK wide integer converter placed; Arithmetic entry mapping follows the existing decoded unsigned-division verifier; converter equivalence pending. Arithmetic helpers remain external; integration pending.']}
    (ROOT/'docs/research/gx8002-backup-printf-long-long.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print({k:v for k,v in build().items() if k!='upstream'})
