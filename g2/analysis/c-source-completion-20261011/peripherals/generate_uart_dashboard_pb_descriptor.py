#!/usr/bin/env python3
"""Recover the six source-owned dashboard nanopb descriptors from native ROM."""
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OTA=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'components/audio/uart_thread_source_candidate/display_uart_dashboard_pb_descriptor.c'
EXPECTED='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw=OTA.read_bytes();assert sha256(raw).hexdigest()==EXPECTED
blob=raw[32:];base=0x438000
def at(a,n):
 assert base<=a and a+n<=base+len(blob)
 return blob[a-base:a-base+n]
def u16(a):return int.from_bytes(at(a,2),'little')
def u32(a):return int.from_bytes(at(a,4),'little')
records={};queue=[0x776574]
while queue:
 address=queue.pop()
 if address in records:continue
 field_info=u32(address);submsg_info=u32(address+4)
 assert u32(address+8)==u32(address+12)==u16(address+18)==0
 count=u16(address+16);largest=u16(address+20)
 assert 0<count<=32 and at(address+22,2)==b'\0\0'
 fields=[];offset=0;subcount=0
 for _ in range(count):
  word=u32(field_info+offset);width=1<<(word&3);assert width in (1,2)
  typ=(word>>8)&255;tag=(word>>2)&63
  if width==1:entry=(1,tag,typ,(word>>16)&255,(word>>28)&15,(word>>24)&15,0)
  else:
   tail=u32(field_info+offset+4);tag+=((tail>>28)&15)*64
   entry=(2,tag,typ,tail&65535,(tail>>16)&4095,(word>>28)&15,(word>>16)&4095)
  fields.append(entry);subcount+=((typ&15) in (8,9));offset+=width*4
 assert u32(field_info+offset)==0
 children=[u32(submsg_info+i*4) for i in range(subcount)]
 assert all(children) and u32(submsg_info+subcount*4)==0
 records[address]=(field_info,submsg_info,count,largest,fields,children)
 queue.extend(children)
assert len(records)==6 and sum(r[2] for r in records.values())==24
lines=[
 '/* Authenticated dashboard nanopb descriptor graph rooted at native 0x776574.',
 ' * The call at 0x501ff8 loads its descriptor pointer from literal 0x502664.',
 ' * Source: official s200 v2.2.6.10 OTA SHA-256 '+EXPECTED+'.',
 ' * Typed field initializers and relocations; final ROM placement is separate. */',
 '#include <stdint.h>',
 'struct pb_msgdesc_candidate {',
 ' const uint32_t *field_info;',
 ' const struct pb_msgdesc_candidate *const *submsg_info;',
 ' const uint8_t *default_value;',
 ' void *field_callback;',
 ' uint16_t field_count,required_field_count,largest_tag;',
 '};',
 '_Static_assert(sizeof(struct pb_msgdesc_candidate)==24u,"ARM descriptor ABI");',
 '#define FIELD1(tag,type,offset,size,size_offset) \\',
 ' (((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \\',
 ' ((((uint32_t)(offset))&0xffu)<<16u)|((((uint32_t)(size_offset))&15u)<<24u)| \\',
 ' ((((uint32_t)(size))&15u)<<28u))',
 '#define FIELD2(tag,type,offset,size,size_offset,array_size) \\',
 ' (1u|((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \\',
 ' ((((uint32_t)(array_size))&0xfffu)<<16u)|((((uint32_t)(size_offset))&15u)<<28u)), \\',
 ' (((uint32_t)(offset)&0xffffu)|((((uint32_t)(size))&0xfffu)<<16u)| \\',
 ' ((((uint32_t)(tag))&0x3c0u)<<22u))',
]
for address in sorted(records):
 name='audio_uart_dashboard_pb_descriptor' if address==0x776574 else f'audio_uart_dashboard_pb_desc_{address:06x}'
 lines.append(f'{"" if address==0x776574 else "static "}const struct pb_msgdesc_candidate {name};')
for address,(_,_,count,largest,fields,children) in sorted(records.items()):
 suffix=f'{address:06x}'
 lines.append(f'/* Native 0x{suffix}: {count} fields, largest tag {largest}. */')
 lines.append(f'static const uint32_t dashboard_fields_{suffix}[] = {{')
 for width,tag,typ,offset,size,size_offset,array_size in fields:
  if width==1:lines.append(f' FIELD1({tag}u,0x{typ:02x}u,{offset}u,{size}u,{size_offset}u),')
  else:lines.append(f' FIELD2({tag}u,0x{typ:02x}u,{offset}u,{size}u,{size_offset}u,{array_size}u),')
 lines.append(' 0u');lines.append('};')
 lines.append(f'static const struct pb_msgdesc_candidate *const dashboard_submessages_{suffix}[] = {{')
 for child in children:
  name='audio_uart_dashboard_pb_descriptor' if child==0x776574 else f'audio_uart_dashboard_pb_desc_{child:06x}'
  lines.append(f' &{name},')
 lines.append(' 0');lines.append('};')
 name='audio_uart_dashboard_pb_descriptor' if address==0x776574 else f'audio_uart_dashboard_pb_desc_{suffix}'
 lines.append(f'{"" if address==0x776574 else "static "}const struct pb_msgdesc_candidate {name} = {{')
 lines.append(f' dashboard_fields_{suffix},dashboard_submessages_{suffix},0,0,{count}u,0u,{largest}u')
 lines.append('};')
lines.append('const void *const audio_uart_dashboard_schema=&audio_uart_dashboard_pb_descriptor;')
OUT.write_text('\n'.join(lines)+'\n')
print(f'{OUT.relative_to(ROOT)}: {len(records)} descriptors, {sum(r[2] for r in records.values())} semantic fields, {sum(len(r[5]) for r in records.values())} submessage relocations')
