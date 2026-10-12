#!/usr/bin/env python3
"""Finite evidence inventory for the two remaining Touch reset-copy regions."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
image=blob[32:]
def reset_bytes(ram,size):
 rom=0xb58c+ram-0x200004c0
 return rom,image[rom-0x3300:rom-0x3300+size]
rom,history=reset_bytes(0x2000065e,426)
assert len(history)==426 and not any(history)
rom2,scalar=reset_bytes(0x20000828,4)
assert scalar==bytes((2,0,0,0))
assert image[0xb5f0-0x3300:0xb5f4-0x3300]==struct.pack('<I',0x2000065e)
source=(HERE/'capsense-v6-reference/cy_capsense_structure.h').read_text()
consumer=(HERE/'capsense-v6-reference/cy_capsense_sensing_lp.c').read_text()
assert 'typedef uint16_t cy_stc_capsense_lp_historic_context_t;' in source
assert 'ptrLpHistoricContext' in source and 'ptrHistoricData++' in consumer
report={
 'status':'FINITE_TOUCH_RESET_BOUNDARY_AUDIT',
 'firmware_sha256':hashlib.sha256(blob).hexdigest(),
 'selected_source_archive_receipt':'g2/components/touch/source_candidate_20261010/build/receipt.json',
 'history':{
  'ram_start':'0x2000065e','next_known_object':'0x20000808','gap_bytes':426,
  'stock_sha256':hashlib.sha256(history).hexdigest(),
  'top_level_context_pointer_word':'0x20000524','pointer_value':'0x2000065e',
  'vendor_element_type':'uint16_t','vendor_consumer':'Cy_CapSense_TransferLpRawCounts advances one element for each scanned slot in each frame',
  'configured_four_slot_nominal_words':212,'nominal_bytes':424,
  'allocation_extent_established':False,
  'missing_evidence':'Producer-generated cycfg_capsense history declaration or official symbol size/link map; current pointer and adjacent object prove a start and available gap only.'},
 'scalar':{
  'ram_start':'0x20000828','rom_start':hex(rom2),'bytes':4,
  'stock_value':'0x00000002','stock_sha256':hashlib.sha256(scalar).hexdigest(),
  'direct_absolute_pointer_literal_count':image.count(struct.pack('<I',0x20000828)),
  'semantic_owner_established':True,
  'owner':'Fifth cy_stc_capsense_scan_slot_t active descriptor row {widget=2,sensor=0} contiguous with four selected rows at 0x20000818.',
  'source':'g2/components/touch/reset_layout_candidate_20261010/reset_sensor_descriptors.c'},
 'limits':['The fifth active scan-slot row is now source-owned by adjacency, vendor row type and exact 20-byte compiled table comparison.','Zero reset contents and adjacency do not prove allocation capacity.','This is a data ownership audit, not physical FIFO or final linker placement proof.']}
report['status']='TOUCH_FIFTH_ACTIVE_ROW_CLOSED_HISTORY_REMAINS'
(HERE/'remaining-reset-gates-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'remaining_bytes':426,'history_bytes':426,'fifth_active_row_bytes':4}))
