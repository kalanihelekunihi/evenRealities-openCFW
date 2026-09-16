# SPDX-License-Identifier: MIT
"""Build the C log/exp forwarding wrappers, excluding the power wrapper."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-log-exp-wrappers';out.mkdir(exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_math_wrappers.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-DOPEN_CFW_LOG_EXP_ONLY','-fno-optimize-sibling-calls','-c',str(source),'-o',str(out/'wrapper.o')],check=True)
    (out/'wrapper.ld').write_text('SECTIONS { .log_wrapper 0x100100ac : { *(.text.open_cfw_gx8002_logf) } .exp_wrapper 0x100100b4 : { *(.text.open_cfw_gx8002_expf) } /DISCARD/ : { *(.text.open_cfw_gx8002_powf) } }\n__ieee754_logf = 0x10010768;\n__ieee754_expf = 0x100109c0;\n')
    path=out/'wrapper.elf';subprocess.run([pre+'ld','-T',str(out/'wrapper.ld'),str(out/'wrapper.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrapper');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==2
    body=b''.join(elf.contents(s) for s in sorted(allocated,key=lambda s:s['address']));assert body==stock[0x489ec:0x489fc]
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    report={'source_sha256':sha(source.read_bytes()),'bytes':len(body),'exact_stock':True,'source_admitted':False,'limits':['Complete wrapper byte-identical; log/exp core bindings must resolve to source during integration.']}
    (ROOT/'docs/research/gx8002-backup-log-exp-wrappers.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
