# SPDX-License-Identifier: MIT
"""Place authenticated SDK variadic printf wrapper against recovered callees."""
import json,subprocess
from build_gx8002_backup_printf_candidate import build as candidate,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA

def build():
    evidence=candidate();out=ROOT/'build/gx8002-backup-printf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=evidence['command'].copy();command.insert(1,'-fno-shrink-wrap');command[-1]=str(out/'wrapper-source.o');subprocess.run(command,check=True)
    # Globalize source-object helper names so the explicit recovered bindings
    # can resolve references while the formatter implementation is assessed.
    subprocess.run([pre+'objcopy','--globalize-symbol=_vsnprintf','--globalize-symbol=_out_char',str(out/'wrapper-source.o'),str(out/'wrapper.o')],check=True)
    ld='SECTIONS { .printf_callback 0x10009924 : { *(.text._out_char) } .printf_wrapper 0x10009934 : { *(.text.printf_) } /DISCARD/ : { *(.text*) *(.rodata*) } }\n_vsnprintf = 0x10008e20;\n_putchar = 0x10009990;\n'
    (out/'wrapper.ld').write_text(ld);path=out/'wrapper.elf';subprocess.run([pre+'ld','-T',str(out/'wrapper.ld'),str(out/'wrapper.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrapper');sec=next(s for s in elf.sections if s['name']=='.printf_wrapper');data=elf.contents(sec);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert len(data)<=52;assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'wrapper.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream':evidence,'bytes':len(data),'envelope_bytes':52,'byte_exact_prefix':data==stock[0x42274:0x42274+len(data)],'source_admitted':False,'limits':['Authenticated wrapper plus default-compiled callback. Variadic ABI decoded verification and integration pending; formatter bound externally with full feature scope retained.']}
    (ROOT/'docs/research/gx8002-backup-printf-wrapper.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print({k:v for k,v in build().items() if k!='upstream'})
