#!/usr/bin/env python3
"""Bound direct stock startup producer of the stdio callback sink word."""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
FUNCTIONS=ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl'
DECOMP=ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/decomp'
SELECTED=ROOT/'g2/components/bootloader/initializer_callbacks/startup_alternatives.c'
SETTER=ROOT/'g2/components/bootloader/initializer_callbacks/startup_power_config.c'
all_functions=[json.loads(line) for line in FUNCTIONS.read_text().splitlines()]
direct_callers=[row['entry'] for row in all_functions if '0041583c' in row.get('callees',[])]
assert direct_callers==['0041fa98'],direct_callers
native=(DECOMP/'0041fa98.c').read_text()
setter=(DECOMP/'0041583c.c').read_text()
assert 'FUN_0041583c(0)' in native
assert '*DAT_00415fdc = param_1' in setter
assert 'opencfw_boot_startup_external_mode(0)' in SELECTED.read_text()
assert 'W(0x200270ccu)=callback' in SETTER.read_text()
receipt={
 'status':'PASS_BOUNDED_STDIO_SINK_STARTUP_NULL_PRODUCER',
 'sink_word':'0x200270cc','native_setter':'0x0041583c',
 'known_direct_native_callers':direct_callers,
 'known_direct_call_argument':0,
 'source_caller_sha256':hashlib.sha256(SELECTED.read_bytes()).hexdigest(),
 'source_setter_sha256':hashlib.sha256(SETTER.read_bytes()).hexdigest(),
 'native_functions_sha256':hashlib.sha256(FUNCTIONS.read_bytes()).hexdigest(),
 'limits':['Authenticated native function catalogue has one direct caller of this setter, passing zero; selected caller and setter match.',
           'The startup zero-scatter record covers the sink word, but this audit does not prove the conditional startup path always runs.',
           'Indirect/external calls may later install a nonzero sink; the audit does not establish physical output behavior.'],
}
out=HERE/'boot-stdio-sink-startup-roots.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],direct_callers)
