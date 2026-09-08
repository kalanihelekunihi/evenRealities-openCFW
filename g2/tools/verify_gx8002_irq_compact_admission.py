#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit explicitly accounted architecture assembly with original frame and bytes."""
import contextlib,io,json,shutil,hashlib
from verify_gx8002_irq_compact_nesting import verify as compare,ROOT
from analyze_gx8002_irq_stack_contract import analyze
from verify_gx8002_logging import check_paths
from verify_gx8002_irq_architecture_frame import MANUAL_SHA

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    if hashlib.sha256((ROOT/'build/csky-isa-manual.pdf').read_bytes()).hexdigest()!=MANUAL_SHA:raise ValueError('IRQ ISA changed')
    with contextlib.redirect_stdout(io.StringIO()):
        evidence=compare();abi=analyze()
    row=evidence['base']['build']
    if not row['byte_exact'] or row['compiled_bytes']!=80:raise ValueError('IRQ stock frame/bytes')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-irq/compact.elf',output/'compact.elf')
    return {'functions':[{'symbol':'open_cfw_gx8002_irq_compact_entry','section_name':'.text',
              'ownership_kind':'compiled_assembly','compiled_bytes':80,'compiled_sha256':row['compiled_sha256'],
              'stock_occurrences':[{'symbol':'open_cfw_gx8002_irq_compact_entry','package_offset':0x17588,'bytes':80,
                'sha256':row['compiled_sha256'],'region':'image_a_sram_text'}]}],
            'evidence':evidence,'abi':abi,'isa_manual_sha256':MANUAL_SHA,
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Source-authored architecture assembly, not counted as C. Exact stock code and frame; full decoded dispatch and post-NIE nested context checks. ABI-compliant callbacks and valid vectors assumed. No new stack growth; physical callback capacity, exception acceptance timing and instruction faults remain whole-device qualification work.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-irq-compact-admission.json').write_text(json.dumps(verify(),indent=2)+'\n')
