#!/usr/bin/env python3
"""Symbolic native calendar frames; existing time state/table/fallback owners reused."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-registration';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x8af8c,0x8b01e,0x8b028,'r1_subscriber_register')]
WORDS={0x8b020:'r1_subscriber_roots',0x8b024:'r1_event_sensor+8'}
PROVIDERS={0x5dcb0:'r1_subscriber_lock',0x5dcd4:'r1_subscriber_unlock',0x855a0:'pvPortMalloc'}
def main():
 OUT.mkdir(exist_ok=True);elf=BASE/'i2c5/stock-analysis-exec.elf';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';sources=['/* Native calendar frames; symbolic instructions and typed literals only. */'];contracts=[]
 for start,end,span_end,name in BODIES:
  text=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(elf)],text=True);path=OUT/('disassembly-'+hex(start)[2:]+'.txt');path.write_text(text);lines=[];instructions=[];words=set()
  for line in text.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(.*)',line)
   if not m:continue
   a=int(m[1],16);size=len(m[2].split())*2;ins=m[3].split('@')[0].strip();op=ins.split()[0];args=ins[len(op):].strip();original=ins
   if op.startswith('ldr') and '[pc,' in args:
    t=int(re.search(r'@\s*(?:\()?([0-9a-f]+)',line)[1],16);words.add(t);ins=op+' '+args.split(',')[0]+', NCF_'+hex(t)[2:]
   elif re.match(r'^(b[a-z]*(?:\.[nw])?|cbz|cbnz)$',op) and op not in ['bx','blx']:
    t=int(re.search(r'\b([0-9a-f]{5,})\s*<',args)[1],16);target=PROVIDERS.get(t,'NCF_'+hex(t)[2:]);ins=op+' '+re.sub(r'[0-9a-f]{5,}\s*<.*',target,args)
   if a in [0x8afd0,0x8affe]:ins=ins.replace('str.w','str')
   lines+=['NCF_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==end-start;cursor=end
  for a in sorted(words):
   if a>cursor:assert raw[cursor-0x27000:a-0x27000]==bytes(a-cursor);lines+=['.space '+str(a-cursor)+',0']
   lines+=['NCF_'+hex(a)[2:]+':','.word '+WORDS[a]];cursor=a+4
  if cursor<span_end:assert raw[cursor-0x27000:span_end-0x27000]==bytes(span_end-cursor);lines+=['.space '+str(span_end-cursor)+',0']
  sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=span_end-start,symbol=name,instructions=instructions,disassembly_sha256=sha(path)))
 sources += ['#include <stdint.h>', 'void *r1_subscriber_roots[5] __attribute__((section(".r1.subscriber.roots"),aligned(4)))={0};', 'struct r1_event_context { void (*create)(void), (*stop)(void); void *thread, *queue; };', 'extern struct r1_event_context r1_event_sensor,r1_event_system;', 'struct r1_subscriber_route { void **thread; uint16_t event_id,reserved; };', '_Static_assert(sizeof(struct r1_subscriber_route)==8,"native routing stride");', 'const struct r1_subscriber_route r1_subscriber_routes[2] __attribute__((section(".r1.subscriber.routes"),aligned(4)))={{&r1_event_sensor.thread,2,0},{&r1_event_system.thread,0x1000,0}};']
 src=ROOT/'r1/components/runtime/native_subscriber_registration.c' ;src.write_text('\n'.join(sources)+'\n');c=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,native_code_bytes=146,native_span_bytes=156,config={'r1_subscriber_roots':{'address':'0x20015708','size':20},'r1_subscriber_routes':{'address':'0x99ba8','size':16}},new_ram_state_bytes=20,multicast_unchecked_index_remains=True,whole_image_complete=False)
 (OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');print('Recovered subscriber registration and typed five-root/two-route configuration')
if __name__=='__main__':main()
