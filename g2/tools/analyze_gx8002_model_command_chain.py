#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inspect authenticated model command boundaries; never generate firmware data."""
import json,struct
from collections import Counter
from analyze_gxdnn_arithmetic_dispatch import analyze as arithmetic_dispatch
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
START=0x18d90
SIZE=9164
COMMAND_SHA='c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9'
# Sequential sizes corroborated by pinned gxDNN parse_next_cmd. Only observed
# opcodes are admitted to this structural walk; no host pointer sizes assumed.
SIZES={1:44,0x40:48,0x41:60,0x42:48,0x43:24}
def analyze():
    image=IMAGE.read_bytes();data=image[START:START+SIZE]
    if sha(image)!=IMAGE_SHA or sha(data)!=COMMAND_SHA:raise ValueError('model image/command authentication')
    arithmetic={r['selector']:r['operation'] for r in arithmetic_dispatch()['dispatch']}
    rows=[];offset=0;counts=Counter()
    while offset<len(data):
        header=struct.unpack_from('<I',data,offset)[0];opcode=header&255
        if opcode not in SIZES:raise ValueError('unresolved opcode')
        sequential=bool(header&(1<<17));absolute=bool(header&(1<<16))
        if absolute:raise ValueError('absolute pointer representation unresolved')
        size=SIZES[opcode]+(0 if sequential else 4)
        if offset+size>len(data):raise ValueError('command boundary')
        row={'offset':offset,'header':header,'opcode':opcode,'bytes':size,'sequential':sequential}
        if not sequential:
            link=struct.unpack_from('<I',data,offset+4)[0]
            row['relative_link']={'base_slot':link>>28,'offset':link&0xfffffff}
            if offset+size!=len(data) or link!=0x70000000:raise ValueError('unexpected terminal link')
        payload=offset+(4 if sequential else 8)
        if opcode==1:
            subtype=struct.unpack_from('<I',data,payload+16)[0]&15
            names={0:'active',1:'pool',2:'copy',3:'reduce',4:'tensor_vector',5:'tensor_tensor',6:'tensor_scalar',7:'format',8:'bn'}
            if subtype not in names:raise ValueError('unresolved operator subtype')
            row['operator']=names[subtype];row['subtype']=subtype
            if subtype in (4,5):
                word=lambda off:struct.unpack_from('<I',data,payload+off)[0]
                half=lambda off:struct.unpack_from('<H',data,payload+off)[0]
                address=lambda value:{'base_slot':value>>28,'offset':value&0xfffffff}
                shape=word(20)
                row['tensor_operands']={'source_a':address(word(0)),'source_b':address(word(4)),
                    'destination':address(word(12)),
                    'operation_selector':(word(16)>>(9 if subtype==4 else 11))&3,
                    'extents':[shape>>20,(shape>>8)&0xfff,shape&255],
                    'source_stride_fields':[half(26),half(24)],
                    'destination_stride_fields':[half(30),half(28)],
                    'immediate_bits16':half(32)}
                row['tensor_operands']['arithmetic']=arithmetic[row['tensor_operands']['operation_selector']]
                tensor=row['tensor_operands']
                tensor['source_a_strides_elements']=[*tensor['source_stride_fields'],1]
                tensor['source_b_strides_elements']=([0,0,1] if subtype==4 else [*tensor['source_stride_fields'],1])
                tensor['destination_strides_elements']=[*tensor['destination_stride_fields'],1]
            if subtype in (0,7):
                word=lambda off:struct.unpack_from('<I',data,payload+off)[0]
                half=lambda off:struct.unpack_from('<H',data,payload+off)[0]
                address=lambda value:{'base_slot':value>>28,'offset':value&0xfffffff}
                shape=word(20)
                row['unary_geometry']={'source':address(word(0)),'destination':address(word(12)),
                    'extents':[shape>>20,(shape>>8)&0xfff,shape&255],
                    'source_strides_elements':[half(26),half(24),1],
                    'destination_strides_elements':[half(30),half(28),1]}
                if subtype==0:
                    row['unary_geometry']['activation_selector']=(word(16)>>4)&7
                else:row['unary_geometry']['format_selector']=half(18)&1
            if subtype==2:
                word=lambda off:struct.unpack_from('<I',data,payload+off)[0]
                half=lambda off:struct.unpack_from('<H',data,payload+off)[0]
                address=lambda value:{'base_slot':value>>28,'offset':value&0xfffffff}
                shape=word(20)
                row['copy']={'source':address(word(0)),'destination':address(word(12)),
                    'extents':[shape>>20,(shape>>8)&0xfff,shape&255],
                    'source_strides_elements':[half(26),half(24),1],
                    'destination_strides_elements':[half(30),half(28),1],
                    'immediate_bits16':half(32)}
        rows.append(row);counts[opcode]+=1;offset+=size
    return {'firmware_sha256':IMAGE_SHA,'command_sha256':COMMAND_SHA,'package_offset':START,'bytes':SIZE,'commands':rows,'opcode_counts':dict(counts),'operator_counts':dict(Counter(r['operator'] for r in rows if 'operator' in r)),'exact_slot8_zero_words':[o for o in range(0,SIZE,4) if struct.unpack_from('<I',data,o)[0]==0x80000000],'source_admitted':False,'limits':['Structural command boundaries only. Payload tensor fields, numeric operations and weights remain opaque. No firmware payload generated. Absence of exact slot8-zero words does not establish absence of all immediate forms.']}
if __name__=='__main__':
    report=analyze();(ROOT/'docs/research/gx8002-model-command-chain.json').write_text(json.dumps(report,indent=2)+'\n');print(len(report['commands']),report['opcode_counts'])
