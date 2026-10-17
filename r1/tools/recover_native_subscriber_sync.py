#!/usr/bin/env python3
"""Symbolic native calendar frames; existing time state/table/fallback owners reused."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-sync';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x5dcb0,0x5dccc,0x5dcd4,'r1_subscriber_lock'),(0x5dcd4,0x5dce2,0x5dce8,'r1_subscriber_unlock'),(0x7d814,0x7d818,0x7d818,'r1_subscriber_current_thread')]
WORDS={0x5dccc:'r1_subscriber_mutex',0x5dcd0:'r1_subscriber_mutex_attr',0x5dce4:'r1_subscriber_mutex'}
PROVIDERS={0x7d4d6:'osMutexNew',0x7d488:'osMutexAcquire',0x7d536:'osMutexRelease',0x9879c:'xTaskGetCurrentTaskHandle'}
def main():
 OUT.mkdir(exist_ok=True);elf=BASE/'i2c5/stock-analysis-exec.elf';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';sources=['/* Local event mutex wrappers; CMSIS and FreeRTOS providers remain upstream-owned. */'];contracts=[]
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
   lines+=['NCF_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==end-start;cursor=end
  for a in sorted(words):
   if a>cursor:assert raw[cursor-0x27000:a-0x27000]==bytes(a-cursor);lines+=['.space '+str(a-cursor)+',0']
   lines+=['NCF_'+hex(a)[2:]+':','.word '+WORDS[a]];cursor=a+4
  if cursor<span_end:assert raw[cursor-0x27000:span_end-0x27000]==bytes(span_end-cursor);lines+=['.space '+str(span_end-cursor)+',0']
  sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=span_end-start,symbol=name,instructions=instructions,disassembly_sha256=sha(path)))
 sources += ['#include <stdint.h>', 'uint32_t r1_subscriber_mutex __attribute__((section(".r1.subscriber.mutex"),aligned(4)))=0;', 'uint32_t r1_subscriber_mutex_control[20] __attribute__((section(".r1.subscriber.control"),aligned(4)))={0};', 'const char r1_subscriber_mutex_name[12] __attribute__((section(".r1.subscriber.name")))="event_mutex";', 'struct r1_mutex_attr { const char *name; uint32_t bits; void *memory; uint32_t size; };', 'const struct r1_mutex_attr r1_subscriber_mutex_attr __attribute__((section(".r1.subscriber.attr"),aligned(4)))={r1_subscriber_mutex_name,0,r1_subscriber_mutex_control,80};']
 initialized=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(initialized)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and initialized.read_bytes()[0x20006794-0x200064a8:0x20006798-0x200064a8]==bytes(4)
 src=ROOT/'r1/components/runtime/native_subscriber_sync.c' ;src.write_text('\n'.join(sources)+'\n');c=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,native_code_bytes=46,native_span_bytes=60,config={'r1_subscriber_mutex':{'address':'0x20006794','size':4},'r1_subscriber_mutex_control':{'address':'0x2001571c','size':80},'r1_subscriber_mutex_attr':{'address':'0x99bb8','size':16},'r1_subscriber_mutex_name':{'address':'0xbf784','size':12}},initialized_data_sha256=sha(initialized),new_ram_state_bytes=84,whole_image_complete=False)
 (OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');print('Recovered subscriber mutex wrappers, current-thread thunk and typed configuration')
if __name__=='__main__':main()
