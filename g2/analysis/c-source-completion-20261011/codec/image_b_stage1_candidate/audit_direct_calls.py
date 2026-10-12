#!/usr/bin/env python3
"""Finite corrected-PC direct-BSR catalogue, not whole-body equivalence."""
import hashlib,json,re,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent; R=H.parents[4]
S=R/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage1.bin'
O=R/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump'
text=subprocess.check_output([str(O),'-D','-b','binary','-m','csky','--no-show-raw-insn','--adjust-vma=0x0fffffe8','--start-address=0x10000100','--stop-address=0x10001324',str(S)],text=True)
targets=sorted({int(s,16) for s in re.findall(r'\b(?:bsr|jbsr)\s+0x([0-9a-f]+)',text)})
expected={0x10000134,0x10000138,0x100001f8,0x10000300,0x100004f4,0x100007d8,0x10000d24,0x10000d4c,0x10000df0,0x10000e20,0x10000e64,0x10000ea0,0x10000eb8,0x10000ed0,0x10000edc,0x10000f5c,0x10000fdc,0x10001234,0x10001260,0x100012e0,0x100012f0,0x10001310,0x10003100}
assert set(targets)==expected
raw=S.read_bytes()
# The pre-initialized-data aligned span consists of six internal dispatch
# tables. These are native branch targets, not callable entry providers.
table_words=[int.from_bytes(raw[o:o+4],'little') for o in range(0x133c,0x14e0,4)]
assert len(table_words)==105
assert all(0x10000100 <= word < 0x10001324 for word in table_words)
table_lengths=(18,19,19,18,19,12)
assert sum(table_lengths)==len(table_words)
header={0x10000138:'pinned clk_priv.h:__module_get_info',0x10001310:'pinned board trim transition in gx8002_image_b_stage1_clock_init_100007d8'}
entry=0x10003100
r={'result':'PASS_DIRECT_TARGET_CENSUS','stock_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),
   'runtime_address_rule':'file offset + 0x0fffffe8',
   'scan_native_runtime':'0x10000100..0x10001324',
   'direct_targets_total':len(targets),'targets':[hex(x) for x in targets],
   'source_c_entries':len(targets)-len(header)-1,'pinned_source_inlines':{hex(k):v for k,v in header.items()},
   'interstage_absolute_contract':hex(entry),
   'indirect_dispatch_words':len(table_words),
   'indirect_dispatch_table_lengths':list(table_lengths),
   'all_indirect_dispatch_words_internal_to_stage1_code':True,
   'all_direct_target_identifications_accounted_for':True,
   'whole_native_body_equivalence_proven':False,
   'limits':['Direct BSR targets do not enumerate indirect/table/computed edges.',
             'Source attribution and relocatable link do not prove native MMIO effects or physical transfer.']}
(H/'direct-call-census-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print('stage1 corrected direct targets',len(targets),'PASS')
