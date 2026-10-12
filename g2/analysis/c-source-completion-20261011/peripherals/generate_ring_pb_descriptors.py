#!/usr/bin/env python3
"""Decode the authenticated ring protobuf descriptor graph to semantic C.

The generated output uses nanopb FIELD1/FIELD2 initializers and typed
descriptor relocations. It is source data, not a copied stock byte array.
"""
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OTA=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'components/audio/uart_thread_source_candidate/display_ble_ring_pb_descriptor.c'
EXPECTED='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw=OTA.read_bytes()
assert sha256(raw).hexdigest()==EXPECTED
blob=raw[32:]
base=0x438000
def at(addr,n):
    assert base<=addr and addr+n<=base+len(blob),(hex(addr),n)
    return blob[addr-base:addr-base+n]
def u16(addr):return int.from_bytes(at(addr,2),'little')
def u32(addr):return int.from_bytes(at(addr,4),'little')

records={}
queue=[0x7766dc]
while queue:
    address=queue.pop()
    if address in records:continue
    field_info=u32(address)
    submsg_info=u32(address+4)
    default=u32(address+8)
    callback=u32(address+12)
    count=u16(address+16)
    required=u16(address+18)
    largest=u16(address+20)
    assert default==callback==required==0
    assert 0<count<=32
    assert at(address+22,2)==b'\0\0'
    fields=[];offset=0;subcount=0
    for _ in range(count):
        word=u32(field_info+offset)
        width=1<<(word&3)
        assert width in (1,2)
        type_code=(word>>8)&255
        tag=(word>>2)&63
        if width==1:
            entry=(1,tag,type_code,(word>>16)&255,(word>>28)&15,(word>>24)&15,0)
        else:
            tail=u32(field_info+offset+4)
            tag+=((tail>>28)&15)*64
            entry=(2,tag,type_code,tail&65535,(tail>>16)&4095,(word>>28)&15,(word>>16)&4095)
        fields.append(entry)
        subcount+=((type_code&15) in (8,9))
        offset+=width*4
    assert u32(field_info+offset)==0
    children=[u32(submsg_info+i*4) for i in range(subcount)]
    assert all(children)
    assert u32(submsg_info+subcount*4)==0
    records[address]=(field_info,submsg_info,count,largest,fields,children)
    queue.extend(children)
assert len(records)==20
assert sum(r[2] for r in records.values())==71

lines=[
    '/* Authenticated generated nanopb descriptor graph rooted at native 0x7766dc.',
    ' * Source: official s200 v2.2.6.10 OTA SHA-256 '+EXPECTED+'.',
    ' * Nanopb field generator semantics: PB_FIELDINFO_1/2; no stock byte blob.',
    ' * Absolute ROM placement remains a separate image/linker obligation. */',
    '#include <stddef.h>',
    '#include <stdint.h>',
    'struct pb_msgdesc_candidate {',
    '    const uint32_t *field_info;',
    '    const struct pb_msgdesc_candidate *const *submsg_info;',
    '    const uint8_t *default_value;',
    '    uint8_t (*field_callback)(void *,void *,const void *);',
    '    uint16_t field_count,required_field_count,largest_tag;',
    '};',
    '_Static_assert(sizeof(struct pb_msgdesc_candidate)==24u,"ARM nanopb descriptor ABI");',
    '_Static_assert(offsetof(struct pb_msgdesc_candidate,field_count)==16u,"ARM nanopb field count offset");',
    '#define FIELD1(tag,type,offset,size,size_offset) \\',
    '    (((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \\',
    '     ((((uint32_t)(offset))&0xffu)<<16u)|((((uint32_t)(size_offset))&15u)<<24u)| \\',
    '     ((((uint32_t)(size))&15u)<<28u))',
    '#define FIELD2(tag,type,offset,size,size_offset,array_size) \\',
    '    (1u|((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \\',
    '     ((((uint32_t)(array_size))&0xfffu)<<16u)|((((uint32_t)(size_offset))&15u)<<28u)), \\',
    '    (((uint32_t)(offset)&0xffffu)|((((uint32_t)(size))&0xfffu)<<16u)| \\',
    '     ((((uint32_t)(tag))&0x3c0u)<<22u))',
]
for address in sorted(records):
    name=f'audio_ble_ring_pb_desc_{address:06x}'
    prefix='' if address==0x7766dc else 'static '
    if address==0x7766dc:name='audio_ble_ring_connect_pb_descriptor'
    lines.append(f'{prefix}const struct pb_msgdesc_candidate {name};')
for address,(_,_,count,largest,fields,children) in sorted(records.items()):
    suffix=f'{address:06x}'
    lines.append(f'/* Native 0x{suffix}: {count} fields, largest tag {largest}. */')
    lines.append(f'static const uint32_t ring_fields_{suffix}[] = {{')
    for width,tag,type_code,offset,size,size_offset,array_size in fields:
        if width==1:
            lines.append(f'    FIELD1({tag}u,0x{type_code:02x}u,{offset}u,{size}u,{size_offset}u),')
        else:
            lines.append(f'    FIELD2({tag}u,0x{type_code:02x}u,{offset}u,{size}u,{size_offset}u,{array_size}u),')
    lines.append('    0u')
    lines.append('};')
    lines.append(f'static const struct pb_msgdesc_candidate *const ring_submessages_{suffix}[] = {{')
    for child in children:
        childname=('audio_ble_ring_connect_pb_descriptor' if child==0x7766dc else f'audio_ble_ring_pb_desc_{child:06x}')
        lines.append(f'    &{childname},')
    lines.append('    0')
    lines.append('};')
    name=('audio_ble_ring_connect_pb_descriptor' if address==0x7766dc else f'audio_ble_ring_pb_desc_{suffix}')
    prefix='' if address==0x7766dc else 'static '
    lines.append(f'{prefix}const struct pb_msgdesc_candidate {name} = {{')
    lines.append(f'    ring_fields_{suffix},ring_submessages_{suffix},0,0,{count}u,0u,{largest}u')
    lines.append('};')
OUT.write_text('\n'.join(lines)+'\n')
print(f'{OUT.relative_to(ROOT)}: {len(records)} typed descriptors, '+
      f'{sum(r[2] for r in records.values())} semantic fields, '+
      f'{sum(len(r[5]) for r in records.values())} submessage relocations')
