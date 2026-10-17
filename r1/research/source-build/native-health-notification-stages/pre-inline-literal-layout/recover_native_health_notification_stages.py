#!/usr/bin/env python3
"""Reduce native sync controllers with symbolic dependencies and bounded data ownership."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from audit_source_frontier import VERIFIED
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-notification-stages';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';elf=BASE/'i2c5/stock-analysis-exec.elf';assert sha(elf)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';OUT.mkdir(exist_ok=True)
 parent=BASE/'native-health-notification-throttle/native-health-notification-throttle-runtime.o';defined={v[2] for l in subprocess.check_output(['arm-none-eabi-nm',str(parent)],text=True).splitlines() if len(v:=l.split())==3 and v[1]!='U'}
 def name(a):
  candidate=VERIFIED.get('0x%08x'%a,('',''))[0];return candidate if candidate in defined else 'r1_health_sync_provider_%08x'%a
 providers={};strings={};bodies=[];ram={0x20006798:('hr',0x2000679a),0x2000679b:('spo2',0x2000679d),0x200067ab:('hrv',0x200067ad),0x200067a8:('activity',0x200067aa)}
 source='#include <stdint.h>\n/* Owner-authorized native controller source. All external code pointers are symbolic.\n * Only accessed descriptor prefixes and individual pending bytes are owned. */\n'
 for i,(kind,length) in enumerate([(0,3),(1,3),(2,3),(3,3),(4,24),(5,6)]):source+='const uint8_t r1_health_sync_kind%d[2] __attribute__((section(".r1.health.sync.kind%d")))={%d,%d};\n'%(i,i,kind,length)
 for label,a in ram.values():source+='volatile uint8_t r1_health_sync_pending_'+label+' __attribute__((section(".r1.health.sync.pending.'+label+'")))=0;\n'
 stage_specs=[(0x8c150,842),(0x8cd60,844),(0x8c750,844),(0x8baec,848),(0x8b818,22)]
 for entry,size in stage_specs:
  dis=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(entry),'--stop-address='+hex(entry+size),str(elf)],text=True);(OUT/('disassembly-%x.txt'%entry)).write_text(dis);instructions=[];lines=[]
  for line in dis.splitlines():
   match=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)(\S+)\s*(.*)',line)
   if not match:continue
   a=int(match[1],16);m=match[3];op=match[4];instructions.append(dict(address=hex(a),size=2*len(match[2].split()),mnemonic=m,operands=op));v=m+' '+op.split('@')[0].strip()
   if 'adr ' in op:
    z=re.search(r'adr (\w+), ([0-9a-f]+)',op);target=int(z[2],16);data=raw[target-0x27000:].split(b'\0',1)[0];assert len(data)<256;data.decode('ascii');strings[target]=data;v='ldr '+z[1]+',=r1_health_sync_text_'+z[2]
   elif '[pc,' in op:
    z=re.search(r'@ \(([0-9a-f]+)',op);assert z,op;target=int(z[1],16);value=struct.unpack_from('<I',raw,target-0x27000)[0];load=hex(value)
    if value==0x99bf4:load='r1_health_sync_kind0'
    elif value in ram:load='r1_health_sync_pending_'+ram[value][0]+'-2'
    elif value&1 and 0x27000<=value&~1<0xc4d08:providers[hex(value&~1)]=name(value&~1);load=providers[hex(value&~1)]
    v='ldr '+op.split(',')[0]+',='+load
   elif re.search(r'([0-9a-f]+)\s*<',op):
    z=re.search(r'([0-9a-f]+)\s*<',op);target=int(z[1],16)
    if entry<=target<entry+size:dest='HNS_'+z[1]
    else:providers[hex(target)]=name(target);dest=providers[hex(target)]
    v=m.replace('.n','')+' '+op[:z.start()]+dest
   lines.extend(['HNS_%x:'%a,v])
  assert sum(x['size'] for x in instructions)==size
  bodies.append(dict(address=hex(entry),size=size,symbol='r1_health_notification_stage_%08x'%entry,instructions=instructions,disassembly_sha256=sha(OUT/('disassembly-%x.txt'%entry))))
  source+='__attribute__((naked)) void r1_health_notification_stage_%08x(uint32_t first __attribute__((unused)),uint32_t second __attribute__((unused))) { __asm__ volatile(%s); }\n'%(entry,json.dumps('\n'.join(lines)+'\n'))
 spans=[];owners=[];data_source=''
 for a,data in sorted(strings.items()):
  owner=next((x for x in owners if x[0]<=a and a+len(data)+1<=x[0]+len(x[1])+1),None)
  if owner:
   offset=a-owner[0];assert owner[1][offset:]==data;data_source+='__asm__(".global r1_health_sync_text_%x\\n.set r1_health_sync_text_%x,r1_health_sync_text_%x+%d\\n");\n'%(a,a,owner[0],offset);spans.append(dict(address=hex(a),size=len(data)+1,text=data.decode(),alias_of=hex(owner[0]),alias_offset=offset))
  else:
   owners.append((a,data));data_source+='const char r1_health_sync_text_%x[%d] __attribute__((section(".r1.health.sync.s%x")))=%s;\n'%(a,len(data)+1,a,json.dumps(data.decode()));spans.append(dict(address=hex(a),size=len(data)+1,text=data.decode(),section='.r1.health.sync.s%x'%a))
 (ROOT/'r1/components/runtime/native_health_notification_stages.c').write_text(data_source+source)
 (OUT/'contracts.json').write_text(json.dumps(dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),bodies=bodies,providers=providers,descriptor_prefix_address='0x99bf4',descriptor_stride=16,source_descriptor_bytes=12,pending_bytes={label:hex(a) for label,a in ram.values()},full_descriptor_or_context_extent_proven=False),indent=2)+'\n');(OUT/'text-spans.json').write_text(json.dumps(spans,indent=2)+'\n');print('Stage bodies',len(bodies),'code',sum(x['size'] for x in bodies),'providers',len(providers),'unique texts',sum(x['size'] for x in spans if 'section'in x))
if __name__=='__main__':main()
