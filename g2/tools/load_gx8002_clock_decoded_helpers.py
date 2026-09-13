# SPDX-License-Identifier: MIT
"""Authenticated decoded helper runners with explicit stack-output marshalling."""
import json,subprocess
from load_gx8002_clock_context import load,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode
from compare_gx8002_clock_lookup import execute as lookup
from execute_gx8002_clock_source_select import execute as update
from verify_gx8002_power_initialize import word

def load_helpers():
    table,context=load();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    path=ROOT/'build/gx8002-platform-gate/tables.elf';lookup_code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));ids=[r['module'] for r in context['modules']]
    path=ROOT/'build/gx8002-board/clock-source-select-candidate.elf';elf=Elf32(path.read_bytes(),'register helper');report=json.loads((ROOT/'docs/research/gx8002-clock-source-select-source-verification.json').read_text())
    row=next(r for r in report['functions'] if r['section_name']=='.helper');section=next(s for s in elf.sections if s['name']=='.helper');assert sha(elf.contents(section))==row['compiled_sha256']
    update_code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    def lookup_runner(module):
        status,values,writes=lookup(lookup_code,0x10024a44,module,0x1000,ids)
        assert status==0 and all(0x1000<=a<0x1018 for a,v in writes)
        return values
    def register_runner(address,offset,value,mask,prior):
        memory={};word(memory,address,prior)
        ret,after,events=update(update_code,0x10024a30,[address,offset,value,mask],memory,lambda *args:None)
        assert ret[0]=='return' and set(after)==set(memory)
        return word(after,address)
    return {'lookup_runner':lookup_runner,'register_runner':register_runner},{'lookup_elf_sha256':context['elf_sha256'],'register_elf_sha256':sha(path.read_bytes()),'limits':['Lookup executor uses fixed private output 0x1000, marshalled to the actual caller stack; register helper executes on a snapshot of the modeled MMIO word.']}
