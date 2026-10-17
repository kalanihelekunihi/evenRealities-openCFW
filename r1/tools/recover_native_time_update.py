#!/usr/bin/env python3
"""Symbolic native calendar frames; existing time state/table/fallback owners reused."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-time-update';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x8aea4,0x8aeac,0x8aeb0,'r1_event_service_0008aea4'),(0x8aeb0,0x8af38,0x8af40,'r1_event_service_0008aeb0'),(0x5a990,0x5a9b0,0x5a9b4,'r1_clock_backend_snapshot')]
WORDS={0x8aeac:'r1_time_state',0x8af38:'r1_time_state',0x8af3c:'r1_time_registration',0x5a9b0:'r1_time_registration+12'}
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
    t=int(re.search(r'\b([0-9a-f]{5,})\s*<',args)[1],16);target='r1_clock_backend_snapshot' if t==0x5a990 else '__aeabi_memclr' if t==0x277aa else 'NCF_'+hex(t)[2:];ins=op+' '+re.sub(r'[0-9a-f]{5,}\s*<.*',target,args)
   lines+=['NCF_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==end-start;cursor=end
  for a in sorted(words):
   if a>cursor:assert raw[cursor-0x27000:a-0x27000]==bytes(a-cursor);lines+=['.space '+str(a-cursor)+',0']
   lines+=['NCF_'+hex(a)[2:]+':','.word '+WORDS[a]];cursor=a+4
  if cursor<span_end:assert raw[cursor-0x27000:span_end-0x27000]==bytes(span_end-cursor);lines+=['.space '+str(span_end-cursor)+',0']
  sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=span_end-start,symbol=name,instructions=instructions,disassembly_sha256=sha(path)))
 src=ROOT/'r1/components/runtime/native_time_update.c';src.write_text('\n'.join(sources)+'\n');c=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,native_code_bytes=176,native_span_bytes=192,shared_config={'r1_time_state':{'address':'0x20016ac4','size':32},'r1_time_registration':{'address':'0x20006820','size':24}},new_ram_state_bytes=0,whole_image_complete=False)
 (OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');print('Recovered time flag/update and backend snapshot with shared time state')
if __name__=='__main__':main()
