#!/usr/bin/env python3
"""Separate native image-A SRAM code labels from Ghidra's data labels."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[4]
base = root/'g2/research/corpus/codec/ghidra/open-2026-09-29/image_a_sram'
receipt = root/'g2/build/c-firmware/20261011/codec-clock-frequency-round/receipt.json'
seeds = list(map(json.loads, (base/'functions-000.jsonl').open()))
symbols = set(json.load(receipt.open())['images']['codec']['relocatable_link']['defined_symbols'])

# Each >=0x1002657c label is in the initialized product-data tail, as
# established by direct source consumers in resident-source-round.md.
data_early = {0x100246c0, 0x10025cd0, 0x10025ce0,
              0x100264d4, 0x100264e4}
data = {x['entry'] for x in seeds if int(x['entry'],16) >= 0x1002657c or
        int(x['entry'],16) in data_early}
aliases = {
    '10025560': 'g2_codec_critical_save',
    '1002556c': 'g2_codec_critical_restore',
    '10025664': 'g2_codec_header_sync',
    '10025930': 'g2_codec_timestamp',
    '100261b8': 'g2_codec_queue_enqueue',
}
assert len(seeds) == 151 and len(data) == 27
assert all(alias in symbols for alias in aliases.values())
body = [x for x in seeds if x['entry'] not in data]
missing = []
for x in body:
    addr = x['entry']
    if addr in aliases or any(s.endswith('_'+addr[3:]) for s in symbols):
        continue
    missing.append(addr)
assert missing == ['10025574'], missing
result = {
    'scope': 'selected C/ASM symbol binding and independently classified native data; no runtime or linker placement proof',
    'raw_labels': len(seeds), 'data_labels': len(data),
    'native_code_labels': len(body), 'source_bound_code_labels': len(body)-len(missing),
    'unbound_code_labels': missing,
    'alias_code_bindings': aliases,
    'data_labels_sorted': sorted(data),
    'receipt': str(receipt.relative_to(root)),
}
out = Path(__file__).with_suffix('.json')
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k: result[k] for k in ('raw_labels','data_labels',
      'native_code_labels','source_bound_code_labels','unbound_code_labels')}))
