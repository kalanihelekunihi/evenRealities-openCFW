#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link the reconstructed NPU interrupt status reader after authenticating stock identities."""
import json,subprocess
from identify_gx8002_npu_interrupts import ROOT,IMAGE,identify
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
FUNCTIONS=[('npu_get_interrupt',0xec7c,120)]
DELTA=0x101f6a74

def build():
    identities=identify();out=ROOT/'build/gx8002-board';source=ROOT/'components/shared/gx8002/runtime_gx8002_npu_interrupt_status.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]];stock=IMAGE.read_bytes()
    for name,offset,size in FUNCTIONS:
        matches=next(f['matches'] for f in identities['functions'] if f['symbol']==name)
        if len(matches)!=1 or matches[0]['package_offset']!=offset or matches[0]['bytes']>size:raise ValueError('NPU interrupt status identity mismatch')
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'npu-interrupt-status-candidate.o')],check=True)
    script=out/'npu-interrupt-status-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {o+DELTA:#x} : {{ *(.text.open_cfw_gx8002_{n}) }}\n' for n,o,size in FUNCTIONS)+'}\nopen_cfw_gx8002_reg_set_bit = 0x102055cc;\nopen_cfw_gx8002_reg_clear_bit = 0x102055dc;\nopen_cfw_gx8002_reg_get_value = 0x102055ec;\nopen_cfw_gx8002_reg_set_value = 0x102055f0;\n')
    p=out/'npu-interrupt-status-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'npu-interrupt-status-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));rows=[]
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('NPU interrupt status unresolved')
    for n,o,size in FUNCTIONS:
        sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('NPU interrupt status relocation')
        rows.append({'symbol':'open_cfw_gx8002_'+n,'section_name':sec['name'],'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size})
    (out/'npu-interrupt-status-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'identification':identities,'source_sha256':sha(source.read_bytes()),'flags':flags,'regions':rows,'source_admitted':False,'limits':['Linked candidate only. Need status-to-event mapping, ordered output stores/reloads, helper clobbers, snapshot return value and ABI qualification.']}
    (ROOT/'docs/research/gx8002-npu-interrupt-status-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
