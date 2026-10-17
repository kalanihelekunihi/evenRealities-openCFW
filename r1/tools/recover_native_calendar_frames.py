#!/usr/bin/env python3
"""Symbolic native calendar frames; existing time state/table/fallback owners reused."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-calendar-frames';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x8adb4,0x8adbc,0x8adc0,'r1_time_utc_offset_get'),(0x8af40,0x8af8a,0x8af8c,'time_calendar_utc_to_calendar'),(0x5a7bc,0x5a8a0,0x5a8ac,'time_calendar_unix_to_broken_down')]
WORDS={0x8adbc:'r1_time_state',0x5a8a0:'unix_to_broken_down_fallback',0x5a8a4:'86400',0x5a8a8:'month_days_forward'}
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
    t=int(re.search(r'\b([0-9a-f]{5,})\s*<',args)[1],16);target='time_calendar_unix_to_broken_down' if t==0x5a7bc else 'NCF_'+hex(t)[2:];ins=op+' '+re.sub(r'[0-9a-f]{5,}\s*<.*',target,args)
   lines+=['NCF_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==end-start;cursor=end
  for a in sorted(words):
   if a>cursor:assert raw[cursor-0x27000:a-0x27000]==bytes(a-cursor);lines+=['.space '+str(a-cursor)+',0']
   lines+=['NCF_'+hex(a)[2:]+':','.word '+WORDS[a]];cursor=a+4
  if cursor<span_end:assert raw[cursor-0x27000:span_end-0x27000]==bytes(span_end-cursor);lines+=['.space '+str(span_end-cursor)+',0']
  sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=span_end-start,symbol=name,instructions=instructions,disassembly_sha256=sha(path)))
 src=ROOT/'r1/components/runtime/native_calendar_frames.c';src.write_text('\n'.join(sources)+'\n');c=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,native_code_bytes=310,native_span_bytes=328,shared_config={'r1_time_state':{'address':'0x20016ac4','size':32},'unix_to_broken_down_fallback':{'address':'0x20016ae4','size':36},'month_days_forward':{'address':'0x99c5c','size':24}},new_ram_state_bytes=0,whole_image_complete=False)
 (OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');print('Recovered three calendar frames with existing shared configuration')
if __name__=='__main__':main()
