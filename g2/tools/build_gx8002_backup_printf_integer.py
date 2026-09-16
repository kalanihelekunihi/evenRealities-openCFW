# SPDX-License-Identifier: MIT
"""Place authenticated Paland integer conversion helpers for backup assessment."""
import json,subprocess
from build_gx8002_backup_printf_candidate import build as candidate,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA

def build():
    evidence=candidate();out=ROOT/'build/gx8002-backup-printf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    # _out_rev is an independently placed dependency; do not silently overlap it.
    subprocess.run([pre+'objcopy','--globalize-symbol=_out_rev',str(out/'printf.o'),str(out/'integer.o')],check=True)
    entries=[('_ntoa_format',0x413e0,488),('_ntoa_long',0x415c8,192)]
    ld='SECTIONS {\n'+''.join(f'.text.{name} {offset-0x38940+0x10000000:#x} : {{ *(.text.{name}) }}\n' for name,offset,size in entries)+'/DISCARD/ : { *(.text*) *(.rodata*) } }\n_out_rev = 0x10008a04;\n'
    (out/'integer.ld').write_text(ld);path=out/'integer.elf';subprocess.run([pre+'ld','-T',str(out/'integer.ld'),str(out/'integer.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'integer');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for name,offset,size in entries:
        sec=next(s for s in elf.sections if s['name']=='.text.'+name);data=elf.contents(sec);assert len(data)<=size
        rows.append({'name':name,'address':sec['address'],'bytes':len(data),'envelope_bytes':size,'byte_exact_prefix':data==stock[offset:offset+len(data)]})
    assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'integer.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream':evidence,'functions':rows,'source_admitted':False,'limits':['Stock call/signature structure supports helper mapping; exact version identity and decoded behavior pending. Reverse output remains external at 0x10008a04. Wide integers and floating point remain in scope.']}
    (ROOT/'docs/research/gx8002-backup-printf-integer.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['functions'])
