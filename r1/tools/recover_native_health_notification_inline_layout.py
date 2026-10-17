#!/usr/bin/env python3
"""Compile symbolic native instructions, typed literals and readable text in native order."""
import hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-notification-stages';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==c['application_sha256'];providers=c['providers'];textrows=json.loads((OUT/'text-spans.json').read_text());by_address={int(x['address'],16):x for x in textrows};ram={0x20006798:'hr',0x2000679b:'spo2',0x200067ab:'hrv',0x200067a8:'activity'};source='#include <stdint.h>\n/* Symbolic native code and typed .word/.asciz data; no instruction-byte arrays. */\n'
 for i,(kind,length) in enumerate([(0,3),(1,3),(2,3),(3,3),(4,24),(5,6)]):source+='const uint8_t r1_health_sync_kind%d[2] __attribute__((section(".r1.health.sync.kind%d")))={%d,%d};\n'%(i,i,kind,length)
 for name in ram.values():source+='volatile uint8_t r1_health_sync_pending_'+name+' __attribute__((section(".r1.health.sync.pending.'+name+'")))=0;\n'
 for body in c['bodies']:
  entry=int(body['address'],16);tokens={};lines=[];aliases={}
  for x in body['instructions']:
   a=int(x['address'],16);m=x['mnemonic'];op=x['operands'];v=m+' '+op.split('@')[0].strip()
   if 'adr ' in op:
    z=re.search(r'adr (\w+), ([0-9a-f]+)',op);target=int(z[2],16);row=by_address[target];v='adr '+z[1]+',HNS_D'+z[2]
    if 'alias_of'in row:aliases[target]=(int(row['alias_of'],16),row['alias_offset'])
    else:tokens[target]=dict(kind='text',address=hex(target),size=row['size'],text=row['text'])
    row['section']='.text.'+body['symbol'];row['offset']=target-entry;row['inline_body']=body['symbol']
   elif '[pc,' in op:
    z=re.search(r'@ \(([0-9a-f]+)',op);target=int(z[1],16);value=struct.unpack_from('<I',raw,target-0x27000)[0];expr=hex(value)
    if value==0x99bf4:expr='r1_health_sync_kind0'
    elif value in ram:expr='r1_health_sync_pending_'+ram[value]+'-2'
    elif hex(value&~1) in providers and value&1:expr=providers[hex(value&~1)]
    tokens[target]=dict(kind='word',address=hex(target),size=4,expression=expr,native_value=value);v='ldr '+op.split(',')[0]+',HNS_D'+z[1]
   elif re.search(r'([0-9a-f]+)\s*<',op):
    z=re.search(r'([0-9a-f]+)\s*<',op);target=int(z[1],16);dest='HNS_'+z[1] if entry<=target<entry+body['size'] else providers[hex(target)];v=m.replace('.n','')+' '+op[:z.start()]+dest
   lines.extend(['HNS_%x:'%a,v])
  cur=entry+body['size'];layout=[]
  for a,t in sorted(tokens.items()):
   assert a>=cur,(body['address'],t)
   if a>cur:
    gap=a-cur;assert raw[cur-0x27000:a-0x27000]==bytes(gap);lines.append('.space %d,0'%gap);layout.append(dict(kind='zero_padding',address=hex(cur),size=gap))
   lines.append('HNS_D%x:'%a)
   if t['kind']=='text':lines+=['.global r1_health_sync_text_%x'%a,'r1_health_sync_text_%x:'%a,'.asciz '+json.dumps(t['text'])]
   else:lines.append('.word '+t['expression'])
   layout.append(t);cur=a+t['size']
  for a,(owner,offset) in aliases.items():lines+=['.set HNS_D%x,HNS_D%x+%d'%(a,owner,offset),'.global r1_health_sync_text_%x'%a,'.set r1_health_sync_text_%x,HNS_D%x+%d'%(a,owner,offset)]
  body['inline_read_only_layout']=layout;body['source_span_end']=hex(cur);body['source_span_bytes']=cur-entry;source+='__attribute__((naked)) void '+body['symbol']+'(uint32_t first __attribute__((unused)),uint32_t second __attribute__((unused))) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }\n'
 c['native_inline_layout_source']=True;c['source_has_instruction_byte_arrays']=False;c['inline_layout_generator_sha256']=sha(Path(__file__));(ROOT/'r1/components/runtime/native_health_notification_stages.c').write_text(source);(OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');(OUT/'text-spans.json').write_text(json.dumps(textrows,indent=2)+'\n');print('Typed inline native layouts generated:',sum(x['source_span_bytes'] for x in c['bodies']),'bytes')
if __name__=='__main__':main()
