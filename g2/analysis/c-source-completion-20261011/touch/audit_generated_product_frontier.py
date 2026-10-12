#!/usr/bin/env python3
"""Bound four unresolved Touch product-generated objects to locked bytes."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
firmware=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
image=firmware.read_bytes()
assert hashlib.sha256(image).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
def rom(address,size):
    start=32+address-0x3300
    assert 0<=start and start+size<=len(image)
    return image[start:start+size]
def u32(address):return struct.unpack('<I',rom(address,4))[0]
widgets=rom(0xb0f8,432)
common=rom(0xb2a8,132)
assert u32(0xb0f8)==0x20000548
assert u32(0xb188)==0x20000584
assert u32(0xb218)==0x200005c0
assert u32(0xb2b0)==0x2000082c
assert [u32(0xb2e4+i*8) for i in range(9)]==[0xb34c,0xb354,0xb35c,0xb364,
                                                     0xb34c,0xb354,0xb35c,0xb364,0xb36c]
assert u32(0xb32c)==0xb33c
reference=HERE/'capsense-v6-reference/cy_capsense_structure.h'
ref=reference.read_text()
assert 'typedef uint16_t cy_stc_capsense_lp_historic_context_t;' in ref
assert 'cy_stc_capsense_lp_historic_context_t * ptrLpHistoricContext;' in ref
assert 'cy_stc_capsense_internal_context_t * ptrInternalContext;' in ref
assert 'const cy_stc_capsense_widget_config_t * ptrWdConfig;' in ref
listed=subprocess.run(['rg','--files','-g','cycfg_capsense.c','-g','cycfg_capsense.h',
                       '-g','design.modus',str(ROOT)],capture_output=True,text=True,check=True).stdout.splitlines()
cycfg=[Path(p) for p in listed if Path(p).name.startswith('cycfg_capsense.')]
designs=[Path(p) for p in listed if Path(p).name=='design.modus']
assert not cycfg
assert len(designs)==2
report={
 'status':'PASS_BOUNDED_FOUR_GENERATED_OBJECT_BOUNDARIES',
 'firmware_sha256':hashlib.sha256(image).hexdigest(),
 'pinned_vendor_header_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
 'objects':[
  {'symbol':'touch_generated_widget_config','native_start':'0xb0f8','observed_next_object':'0xb2a8','observed_bytes':432,'three_native_record_starts':['0xb0f8','0xb188','0xb218'],'observed_record_stride':144,'stock_sha256':hashlib.sha256(widgets).hexdigest(),'missing':'Authenticated product option macros and generated field initializer source; observed three-record span alone does not identify conditional vendor layout.'},
  {'symbol':'touch_generated_common_config','native_start':'0xb2a8','observed_next_object':'0xb32c','observed_bytes':132,'lp_channel_pointer_at':'0xb2b0','lp_channel_pointer':'0x2000082c','stock_sha256':hashlib.sha256(common).hexdigest(),'missing':'Authenticated product option macros and generated common-config initializer/source; observed boundary is not a declaration.'},
  {'symbol':'touch_generated_internal_context','native_start':'0x20000c50','next_named_lock':'0x20000cc8','available_gap_bytes':120,'native_write_seen_through_offset':117,'missing':'Product generated type/field-option declaration or authenticated symbol extent and zero-scatter placement.'},
  {'symbol':'touch_generated_lp_history','native_start':'0x2000065e','next_named_object':'0x20000808','available_gap_bytes':426,'vendor_element_type':'uint16_t','nominal_four_slot_words':212,'nominal_four_slot_bytes':424,'missing':'Product generated array dimension or authenticated symbol extent; 426-byte gap cannot be used as allocation count.'}
 ],
 'source_search':{'repository_cycfg_capsense_files':[str(p.relative_to(ROOT)) for p in cycfg],
                  'reference_design_modus_files':[str(p.relative_to(ROOT)) for p in designs]},
 'limits':['The observed ROM spans and pointer values are locked-product byte facts. Adjacency does not prove symbol size or optional field layout.',
           'The vendor v6 source proves LP history element width and a consumer advancing one element per scanned slot per frame, not generated history capacity.',
           'No generated product cycfg_capsense.c/.h, product design.modus, or official Touch linker map was found in the checked repository/workspace sources.']}
(HERE/'generated-product-frontier.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],len(widgets),len(common))
