#!/usr/bin/env python3
"""Daily test generator native frame; typed text and bounded log prefix literals."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-daily-fixture';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x8b378,0x8b686,0x8b818,'r1_event_service_0008b378'),(0x5be5c,0x5be60,0x5be64,'r1_temperature_daily_cache_accessor')]
WORDS={0x8b688:'__start_log_const_data+224',0x8b68c:'__start_log_const_data',0x5be60:'r1_health_storage_temperature_prefix'}
PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1',0x799f8:'nrf_log_frontend_std_4',0x8ada4:'r1_time_backend_timestamp',0x8ad64:'r1_time_local_day_start',0x276a4:'r1_native_rand',0x5ace0:'r1_hr_daily_cache_accessor',0x5baec:'r1_spo2_daily_cache_accessor',0x5be5c:'r1_temperature_daily_cache_accessor',0x8d40c:'r1_health_fixture_notify_hr',0x8e3f8:'r1_health_fixture_notify_spo2',0x8e560:'r1_health_fixture_notify_temperature'}
def main():
 OUT.mkdir(exist_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';elf=BASE/'i2c5/stock-analysis-exec.elf';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';sources=['/* Local diagnostic daily-cache fixture; symbolic instructions and typed literals only. */'];contracts=[]
 for start,end,span_end,name in BODIES:
  text=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(elf)],text=True);path=OUT/('disassembly-'+hex(start)[2:]+'.txt');path.write_text(text);lines=[];instructions=[];data={}
  for line in text.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(.*)',line)
   if not m:continue
   a=int(m[1],16);size=len(m[2].split())*2;ins=m[3].split('@')[0].strip();op=ins.split()[0];args=ins[len(op):].strip();original=ins
   if op.startswith('ldr') and '[pc,' in args:
    t=int(re.search(r'@\s*(?:\()?([0-9a-f]+)',line)[1],16);data[t]=('word',WORDS[t],4);ins=op+' '+args.split(',')[0]+', NCF_'+hex(t)[2:]
   elif 'adr ' in line:
    reg,t=re.search(r'adr (\w+), ([0-9a-f]+)',line).groups();t=int(t,16);string=raw[t-0x27000:].split(b'\0',1)[0].decode('ascii');data[t]=('text',string,len(string)+1);ins='adr '+reg+', NCF_'+hex(t)[2:]
   elif re.match(r'^(b[a-z]*(?:\.[nw])?|cbz|cbnz)$',op) and op not in ['bx','blx']:
    t=int(re.search(r'\b([0-9a-f]{5,})\s*<',args)[1],16);target=PROVIDERS.get(t,'NCF_'+hex(t)[2:]);ins=op+' '+re.sub(r'[0-9a-f]{5,}\s*<.*',target,args)
   lines+=['NCF_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==end-start;cursor=end;layout=[]
  for a,(kind,value,size) in sorted(data.items()):
   if a>cursor:assert raw[cursor-0x27000:a-0x27000]==bytes(a-cursor);lines+=['.space '+str(a-cursor)+',0']
   assert a>=cursor;lines+=['NCF_'+hex(a)[2:]+':',('.word '+value) if kind=='word' else '.asciz '+json.dumps(value)];cursor=a+size;layout.append(dict(address=hex(a),size=size,kind=kind,value=value))
  if cursor<span_end:assert raw[cursor-0x27000:span_end-0x27000]==bytes(span_end-cursor);lines+=['.space '+str(span_end-cursor)+',0']
  sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=span_end-start,symbol=name,instructions=instructions,data=layout,disassembly_sha256=sha(path)))
 src=ROOT/'r1/components/runtime/native_health_daily_fixture.c';src.write_text('\n'.join(sources)+'\n');c=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,providers={hex(a):n for a,n in PROVIDERS.items()},native_code_bytes=786,native_span_bytes=1192,new_ram_state_bytes=0,full_daily_cache_extent_owned=False,notification_tails_are_explicit_imports=True,whole_image_complete=False);(OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');print('Recovered daily fixture core and temperature accessor; typed inline strings/literals')
if __name__=='__main__':main()
