#!/usr/bin/env python3
"""Conservative aligned Thumb-address word census in locked CASE payload."""
from pathlib import Path
import hashlib
import json
import re
import struct

H=Path(__file__).resolve().parent
R=H.parents[3]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
payload=fw[32:]
pseudocode=(R/'g2/tools/manifests/g2-box-ghidra-decomp.c').read_text(errors='replace')
fixed={int(s,16) for s in re.findall(r'/\* FUN 0x(0800[0-9a-fA-F]{4})',pseudocode)}
crosswalk=json.loads((H/'case-body-crosswalk.json').read_text())
lead={int(x['entry'],16) for x in crosswalk['rows'] if x['status']=='header_address_lead'}
records=[]
for off in range(0,len(payload)-3,4):
    value=struct.unpack_from('<I',payload,off)[0]
    target=value&~1
    if value&1 and 0x08000000<=target<0x08000000+len(payload):
        records.append({'word_address':hex(0x08000000+off),
                        'target':hex(target),'vector_slot':off//4 if off<184 else None,
                        'fixed_pseudocode_entry':target in fixed,
                        'header_address_lead':target in lead})
distinct=sorted({int(x['target'],16) for x in records})
direct_fixed=sorted({int(x['target'],16) for x in records if x['fixed_pseudocode_entry']})
result={'status':'CONSERVATIVE_ALIGNED_THUMB_WORD_CENSUS',
        'stock_wrapper_sha256':hashlib.sha256(fw).hexdigest(),
        'aligned_candidate_word_count':len(records),
        'distinct_candidate_target_count':len(distinct),
        'distinct_fixed_pseudocode_target_count':len(direct_fixed),
        'vector_candidate_word_count':sum(x['vector_slot'] is not None for x in records),
        'records':records,
        'limits':['Aligned odd in-image words are candidate executable references, not proof of an indirect call or reachable root.',
                  'This scan misses computed, unaligned, copied, external, and runtime-generated function pointers.',
                  'Header-address leads are mechanical source hints, not whole-body or ABI qualification.',
                  'No section may be discarded for final image on this census alone.']}
(H/'case-native-address-root-census.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','aligned_candidate_word_count','distinct_candidate_target_count','distinct_fixed_pseudocode_target_count','vector_candidate_word_count')}))
