#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link four reconstructed NPU interrupt masks after authenticating stock identities."""
import json,subprocess
from identify_gx8002_npu_interrupts import ROOT,IMAGE,identify
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
FUNCTIONS=[('npu_en_interrupt',0xebf8,120),('npu_clr_interrupt',0xecf4,120),('npu_clr_interrupt_without_overflow',0xed6c,88),('npu_clr_overflow_interrupt',0xedc4,40)]
DELTA=0x101f6a74

def build():
    identities=identify();out=ROOT/'build/gx8002-board';source=ROOT/'components/shared/gx8002/runtime_gx8002_npu_interrupt_masks.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]];stock=IMAGE.read_bytes()
    for name,offset,size in FUNCTIONS:
        matches=next(f['matches'] for f in identities['functions'] if f['symbol']==name)
        if len(matches)!=1 or matches[0]['package_offset']!=offset or matches[0]['bytes']>size:raise ValueError('NPU interrupt mask identity mismatch')
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'npu-interrupt-mask-candidate.o')],check=True)
    script=out/'npu-interrupt-mask-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {o+DELTA:#x} : {{ *(.text.open_cfw_gx8002_{n}) }}\n' for n,o,size in FUNCTIONS)+'}\nopen_cfw_gx8002_reg_set_bit = 0x102055cc;\n')
    p=out/'npu-interrupt-mask-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'npu-interrupt-mask-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));rows=[]
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('NPU interrupt mask unresolved')
    for n,o,size in FUNCTIONS:
        sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('NPU interrupt mask relocation')
        rows.append({'symbol':'open_cfw_gx8002_'+n,'section_name':sec['name'],'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size})
    (out/'npu-interrupt-mask-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'identification':identities,'source_sha256':sha(source.read_bytes()),'flags':flags,'regions':rows,'source_admitted':False,'limits':['Linked candidate only. Need full-mask mapping, ordered helper/MMIO accesses, ignored high bits and ABI qualification.']}
    (ROOT/'docs/research/gx8002-npu-interrupt-mask-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
