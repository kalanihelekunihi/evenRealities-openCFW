#!/usr/bin/env python3
"""Extract authenticated two-node Case nanopb descriptor graph into C."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/'g2'
STOCK=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD=STOCK.read_bytes()[32:]
STOCK_SHA='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(PAYLOAD).hexdigest()==STOCK_SHA
BASE=0x438000
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_case_descriptor_77793c_20261017.c'
OUT=G2/'build/c-firmware/20261017/main-case-descriptor/descriptor-map.json'
def data(addr,size):
    off=addr-BASE
    assert 0<=off<=len(PAYLOAD)-size
    return PAYLOAD[off:off+size]
def word(addr):return int.from_bytes(data(addr,4),'little')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

records=[]
for addr in (0x77793c,0x77796c):
    raw=data(addr,24)
    fields,submessages,default,callback=[word(addr+4*i) for i in range(4)]
    count=int.from_bytes(raw[16:18],'little')
    required=int.from_bytes(raw[18:20],'little')
    largest=int.from_bytes(raw[20:22],'little')
    assert raw[22:24]==b'\0\0' and default==callback==required==0
    assert (count,largest)==((3,3) if addr==0x77793c else (5,5))
    cursor=fields;words=[];children=0
    for _ in range(count):
        first=word(cursor)
        width=(1,2,4,8)[first&3]
        words.extend(word(cursor+4*i) for i in range(width))
        cursor+=4*width
        if ((first>>8)&0xf) in (8,9):children+=1
    assert word(cursor)==0
    words.append(0)
    subwords=[word(submessages+4*i) for i in range(children+1)]
    assert subwords[-1]==0
    records.append({'address':hex(addr),'field_info_address':hex(fields),
                    'submsg_info_address':hex(submessages),'field_info':words,
                    'submessages':[hex(x) for x in subwords],
                    'field_count':count,'required_field_count':required,
                    'largest_tag':largest,'raw_sha256':hashlib.sha256(raw).hexdigest()})
assert records[0]['field_info_address']=='0x77f6f8'
assert records[0]['submessages']==['0x77796c','0x0']
assert records[1]['field_info_address']=='0x777954'
assert records[1]['submessages']==['0x0']
lines=['/* Authenticated two-node Case nanopb descriptor graph, stock root 0x77793c.',
       ' * Regenerate with extract_main_case_descriptor_77793c_20261017.py. */',
       '#include "pb.h"','']
for i,record in enumerate(records):
    vals=', '.join(f'0x{v:08x}u' for v in record['field_info'])
    lines.append(f'static const uint32_t case_fields_{i}[{len(record["field_info"])}] = {{{vals}}};')
lines.extend(['static const pb_msgdesc_t *const case_no_submessages[1] = {0};',
              'static const pb_msgdesc_t case_nested_descriptor = {',
              '    case_fields_1, case_no_submessages, 0, 0, 5u, 0u, 5u',
              '};',
              'static const pb_msgdesc_t *const case_root_submessages[2] = {',
              '    &case_nested_descriptor, 0',
              '};',
              'const pb_msgdesc_t audio_uart_case_descriptor_77793c = {',
              '    case_fields_0, case_root_submessages, 0, 0, 3u, 0u, 3u',
              '};',''])
SOURCE.write_text('\n'.join(lines))
record={'status':'PASS_AUTHENTICATED_MAIN_CASE_DESCRIPTOR_GRAPH_77793C',
        'stock_payload_sha256':STOCK_SHA,'root':'0x77793c',
        'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':sha(SOURCE)},
        'descriptors':records,
        'remaining_gate':'C descriptor graph preserves authenticated field words and nested pointer structure. Final ROM placement, protobuf runtime behavior and complete Case image are not proven.'}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(record['status'],len(records),sha(OUT))
