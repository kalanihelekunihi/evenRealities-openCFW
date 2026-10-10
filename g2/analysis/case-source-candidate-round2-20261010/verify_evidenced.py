#!/usr/bin/env python3
"""Check three narrow CASE bindings against retained original-byte evidence."""
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent
R=D.parents[2]
receipt=json.loads((D/'receipt.json').read_text())
source=R/'g2/components/case/source_candidate_20261010/evidenced_providers.c'
text=source.read_text()
assert 'return case_event_flags_set((void *)(uintptr_t)event, flags);' in text
assert 'return case_event_flags_set(event, flags);' in text
for p,s in [('case-frame-callback-closure-2026-10-08/build_offline.py','case_event_post = 0x0800a889'),('case-binary-forward-closure-2026-10-08/build_offline.py','case_forward_event = 0x0800a889')]:
 assert s in (R/'g2/analysis'/p).read_text()
original=(R/'g2/analysis/case-uart-error-atomic-closure-2026-10-08/original-disassembly.txt').read_text()
assert '08005f42 7047         bx       lr' in original
obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__evidenced_providers.c.o'
out=subprocess.run(['/opt/homebrew/bin/arm-none-eabi-objdump','-d',str(obj)],text=True,capture_output=True,check=True).stdout
body=out.split('<HAL_UART_ErrorCallback>:')[1].split('\n\n')[0]
assert re.search(r'\b4770\s+bx\s+lr',body),body
assert receipt['archive_rebuild_same_sha256'] and len(receipt['sources'])==12
j={'case_event_post':'same original entry 0x0800a888 as independently validated case_event_flags_set; 32-bit event pointer in r0 and flags in r1','case_forward_event':'same original entry 0x0800a888 as independently validated case_event_flags_set; pointer in r0 and flags in r1','HAL_UART_ErrorCallback':'original 0x08005f42 opcode 0x7047 (Thumb bx lr); candidate section opcode 0x4770 little-endian Thumb bx lr','result':'PASS selected entry/ABI and callback opcode comparisons; integrated runtime behavior not tested'}
(D/'evidenced-provider-verification.json').write_text(json.dumps(j,indent=2)+'\n')
print(j['result'])
