#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile IRQ C candidate and expose missing interrupt-context preservation."""
import json
import subprocess
from analyze_gx8002_upstream_objects import SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_csi_source import HEADERS
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';output=ROOT/'build/gx8002-irq';output.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_irq_dispatch.c';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    deps=[]
    for name in (*HEADERS,'LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        deps.append({'path':name,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/name,blob))})
    flags=['-Os',*FLAGS[1:],'-mistack'];command=[str(prefix)+'gcc',*flags]
    for name in ('arch/soc/grus/include','include/utility','include/utility/libc'):command+=['-isystem',str(sdk/name)]
    obj=output/'dispatch.o';subprocess.run([*command,'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_irq_dispatch')
    disassembly=subprocess.check_output([str(prefix)+'objdump','-dr',str(obj)],text=True)
    (output/'dispatch.disassembly.txt').write_text(disassembly)
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'source_sha256':sha(source.read_bytes()),'flags':flags,
            'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),
            'relocations':len(elf.relocations(section['index'])),'stock_package_offset':0x17588,'stock_envelope_bytes':80,
            'source_admitted':False,'context_preservation_qualified':False,
            'limits':['Plain interrupt attribute omits stock r18-r31 and fr0-fr7 save/restore.',
                      'Must preserve interrupted register state across arbitrary handler calls before admission.',
                      'Stock indexes vectors 32..63 without a bounds check; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-irq-dispatch-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(build(),indent=2))
