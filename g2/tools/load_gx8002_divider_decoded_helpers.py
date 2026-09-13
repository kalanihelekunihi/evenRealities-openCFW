# SPDX-License-Identifier: MIT
"""Read-only authenticated leaf integration for divider programming."""
import json,subprocess
from load_gx8002_clock_decoded_helpers import load_helpers
from load_gx8002_clock_context import ROOT
from verify_gx8002_clock_divider import execute,expected
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import sha

def load():
    helpers,evidence=load_helpers()
    path=ROOT/'build/gx8002-board/clock-divider-candidate.elf';elf=Elf32(path.read_bytes(),'divider')
    report=json.loads((ROOT/'docs/research/gx8002-clock-divider-verification.json').read_text());row=report['functions'][0]
    section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    def divider_runner(base,offset,shift,mask,value):
        args=(True,base,offset,shift,mask,value);result=execute(code,0x10024ae8,*args);assert result==expected(*args);return result[1]
    return {'divider_runner':divider_runner,'register_runner':helpers['register_runner']},{**evidence,'divider_elf_sha256':sha(path.read_bytes()),'divider_limits':['Descriptor fields and MMIO snapshot marshalled to leaf executor private parameter/descriptor addresses.']}
