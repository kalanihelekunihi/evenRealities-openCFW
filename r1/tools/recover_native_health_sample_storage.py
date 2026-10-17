#!/usr/bin/env python3
"""Recover five native cache aggregators with symbolic code/text and bounded RAM prefixes."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-sample-storage';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[('hr',0x5ad90,0x5ae6c,0x5af18,0x2001654c,80,'r1_hr_event_storage'),('hrv',0x5af60,0x5b042,0x5b0f8,0x200169c0,153,'r1_hrv_event_storage'),('spo2',0x5bb2c,0x5bc0c,0x5bccc,0x200165a0,80,'r1_spo2_event_storage'),('stress',0x5bcec,0x5bdc8,0x5be5c,0x20016670,80,'r1_stress_event_storage'),('temperature',0x5be7c,0x5bf72,0x5c034,0x200165f4,80,'r1_temperature_event_storage')]
PROVIDERS={0x5aca6:'r1_health_storage_hour_index',0x5aba0:'r1_health_storage_average',0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799d6:'nrf_log_frontend_std_2',0x799f8:'nrf_log_frontend_std_4'}
def main():
 OUT.mkdir(exist_ok=True);elf=BASE/'i2c5/stock-analysis-exec.elf';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';sources=['#include <stdint.h>','/* Symbolic native sample storage; bounded cold-zero prefixes are not full contexts. */'];contracts=[]
 for family,start,end,span_end,cache,prefix,name in BODIES:
  text=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(elf)],text=True);path=OUT/('disassembly-'+hex(start)[2:]+'.txt');path.write_text(text);lines=[];instructions=[];words=set();strings=set()
  for line in text.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(.*)',line)
   if not m:continue
   a=int(m[1],16);size=len(m[2].split())*2;ins=m[3].split('@')[0].strip();op=ins.split()[0];args=ins[len(op):].strip();original=ins
   if op.startswith('ldr') and '[pc,' in args:
    t=int(re.search(r'@\s*(?:\()?([0-9a-f]+)',line)[1],16);words.add(t);ins=op+' '+args.split(',')[0]+', HSS_'+hex(t)[2:]
   elif op=='add' and re.match(r'r\d+, pc,',args):
    t=int(re.search(r'adr r\d+, ([0-9a-f]+)',line)[1],16);strings.add(t);ins='adr '+args.split(',')[0]+', HSS_'+hex(t)[2:]
   elif re.match(r'^(b[a-z]*(?:\.[nw])?|cbz|cbnz)$',op) and op not in ['bx','blx']:
    t=int(re.search(r'\b([0-9a-f]{5,})\s*<',args)[1],16);label=PROVIDERS[t] if t in PROVIDERS else 'HSS_'+hex(t)[2:];ins=op+' '+re.sub(r'[0-9a-f]{5,}\s*<.*',label,args)
   lines+=['HSS_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==end-start
  cursor=end;layout=[]
  for a in sorted(words|strings):
   assert cursor<=a
   if a>cursor:assert raw[cursor-0x27000:a-0x27000]==bytes(a-cursor);lines+=['.space '+str(a-cursor)+',0'];layout.append(dict(address=hex(cursor),size=a-cursor,kind='zero'))
   lines+=['HSS_'+hex(a)[2:]+':']
   if a in words:
    value=int.from_bytes(raw[a-0x27000:a-0x27000+4],'little');expr='r1_health_storage_'+family+'_prefix' if value==cache else 'r1_health_storage_stress_text' if value==0xbf8e8 else hex(value);lines+=['.word '+expr];cursor=a+4;layout.append(dict(address=hex(a),size=4,kind='word',value=value,expression=expr))
   else:
    value=raw[a-0x27000:].split(b'\0')[0].decode();lines+=['.asciz '+json.dumps(value)];cursor=a+len(value.encode())+1;layout.append(dict(address=hex(a),size=cursor-a,kind='text',text=value))
  if span_end>cursor:assert raw[cursor-0x27000:span_end-0x27000]==bytes(span_end-cursor);lines+=['.space '+str(span_end-cursor)+',0'];layout.append(dict(address=hex(cursor),size=span_end-cursor,kind='zero'))
  assert cursor<=span_end
  sources+=['uint8_t r1_health_storage_'+family+'_prefix['+str(prefix)+'] __attribute__((aligned(1),section(".r1.health.storage.'+family+'")))={0};','__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }'];contracts.append(dict(family=family,address=hex(start),code_bytes=end-start,source_span_bytes=span_end-start,symbol=name,cache_address=hex(cache),cache_prefix_bytes=prefix,full_cache_context_extent_proven=False,instructions=instructions,inline_layout=layout,disassembly_sha256=sha(path)))
 value=raw[0xbf8e8-0x27000:].split(b'\0')[0].decode();sources+=['const char r1_health_storage_stress_text[] __attribute__((aligned(1),section(".r1.health.storage.stress_text")))='+json.dumps(value)+';'];src=ROOT/'r1/components/runtime/native_health_sample_storage.c';src.write_text('\n'.join(sources)+'\n');report=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,providers={hex(a):n for a,n in PROVIDERS.items()},native_code_bytes=sum(x['code_bytes'] for x in contracts),source_prefix_bytes=sum(x['cache_prefix_bytes'] for x in contracts),external_stress_text=dict(address='0xbf8e8',text=value,size=len(value)+1),whole_image_complete=False)
 (OUT/'contracts.json').write_text(json.dumps(report,indent=2)+'\n');print('Recovered five sample aggregators, bounded cache prefixes and diagnostics')
if __name__=='__main__':main()
