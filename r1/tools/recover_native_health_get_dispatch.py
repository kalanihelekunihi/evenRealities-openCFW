#!/usr/bin/env python3
"""Daily test generator native frame; typed text and bounded log prefix literals."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-get-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x8b8e8,0x8ba80,0x8baec,'r1_event_service_0008b8e8')]
WORDS={0x8bab0:'__start_log_const_data+224',0x8bab4:'__start_log_const_data',0x8bae4:'r1_health_notification_last_timestamp-4',0x8bae8:'r1_health_get_templates'}
PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799d6:'nrf_log_frontend_std_2',0x8ada4:'r1_time_backend_timestamp',0x8adb4:'r1_time_utc_offset_get',0x8d6ac:'r1_hr_latest_sample',0x8d858:'r1_hrv_latest_sample',0x8e524:'r1_spo2_latest_sample',0x83930:'r1_health_get_hr_encode',0x83972:'r1_health_get_hrv_encode',0x83c20:'r1_health_get_spo2_encode',0x8c150:'r1_health_notification_stage_0008c150',0x8cd60:'r1_health_notification_stage_0008cd60',0x8c750:'r1_health_notification_stage_0008c750',0x8baec:'r1_health_notification_stage_0008baec',0x8b818:'r1_health_notification_stage_0008b818',0x8d8fc:'r1_event_publish'}
def main():
 OUT.mkdir(exist_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';elf=BASE/'i2c5/stock-analysis-exec.elf';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';sources=['/* Local diagnostic daily-cache fixture; symbolic instructions and typed literals only. */'];contracts=[]
 for start,end,span_end,name in BODIES:
  text=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(elf)],text=True);path=OUT/('disassembly-'+hex(start)[2:]+'.txt');path.write_text(text);lines=[];instructions=[];data={}
  for line in text.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(.*)',line)
   if not m:continue
   a=int(m[1],16)
   if 0x8b944<=a<0x8b94c:
    if a==0x8b944:lines+=['NCF_8b944:', '.byte '+','.join('(NCF_%x-NCF_8b944)/2'%t for t in [0x8b94c,0x8b99c,0x8b998,0x8b998,0x8ba48,0x8b9f6,0x8ba6e])+',0']
    continue
   size=len(m[2].split())*2;ins=m[3].split('@')[0].strip();op=ins.split()[0];args=ins[len(op):].strip();original=ins
   if op.startswith('ldr') and '[pc,' in args:
    t=int(re.search(r'@\s*(?:\()?([0-9a-f]+)',line)[1],16);data[t]=('word',WORDS[t],4);ins=op+' '+args.split(',')[0]+', NCF_'+hex(t)[2:]
   elif 'adr ' in line:
    reg,t=re.search(r'adr (\w+), ([0-9a-f]+)',line).groups();t=int(t,16);string=raw[t-0x27000:].split(b'\0',1)[0].decode('ascii');data[t]=('text',string,len(string)+1);ins='adr '+reg+', NCF_'+hex(t)[2:]
   elif re.match(r'^(b[a-z]*(?:\.[nw])?|cbz|cbnz)$',op) and op not in ['bx','blx']:
    t=int(re.search(r'\b([0-9a-f]{5,})\s*<',args)[1],16);target=PROVIDERS.get(t,'NCF_'+hex(t)[2:]);ins=op+' '+re.sub(r'[0-9a-f]{5,}\s*<.*',target,args)
   lines+=['NCF_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==400;cursor=end;layout=[]
  for a,(kind,value,size) in sorted(data.items()):
   if a>cursor:assert raw[cursor-0x27000:a-0x27000]==bytes(a-cursor);lines+=['.space '+str(a-cursor)+',0']
   assert a>=cursor;lines+=['NCF_'+hex(a)[2:]+':',('.word '+value) if kind=='word' else '.asciz '+json.dumps(value)];cursor=a+size;layout.append(dict(address=hex(a),size=size,kind=kind,value=value))
  if cursor<span_end:assert raw[cursor-0x27000:span_end-0x27000]==bytes(span_end-cursor);lines+=['.space '+str(span_end-cursor)+',0']
  sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps('\n'.join(lines)+'\n')+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=span_end-start,symbol=name,instructions=instructions,data=layout,disassembly_sha256=sha(path)))
 templates=[0,0x10000,0,0x10000,0,0x10000,0];assert raw[0x99bc8-0x27000:0x99be4-0x27000]==__import__('struct').pack('<7I',*templates)
 sources+=['#include <stdint.h>', 'const uint32_t r1_health_get_templates[7] __attribute__((section(".r1.health.get.templates"),aligned(4)))={'+','.join(hex(x) for x in templates)+'};']
 src=ROOT/'r1/components/runtime/native_health_get_dispatch.c' ;src.write_text('\n'.join(sources)+'\n');c=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,providers={hex(a):n for a,n in PROVIDERS.items()},native_code_bytes=400,native_span_bytes=516,templates={"address":"0x99bc8","size":28,"words":templates},new_ram_state_bytes=0,full_context_extent_owned=False,publish_and_storage_execution_gated=True,whole_image_complete=False);(OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');print('Recovered health get dispatcher and typed jump/template data')
if __name__=='__main__':main()
