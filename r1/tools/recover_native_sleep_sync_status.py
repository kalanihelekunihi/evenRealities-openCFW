#!/usr/bin/env python3
"""Daily test generator native frame; typed text and bounded log prefix literals."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sync-status';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x5b6f4,0x5b7d8,0x5b890,'r1_sleep_sync_status_backend')]
WORDS={0x5b7d8:'__start_log_const_data+224',0x5b7dc:'__start_log_const_data',0x5b7e0:'0x11223344',0x5b7e4:'r1_sleep_sync_context_prefix'}
PROVIDERS={0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c0:'nrf_log_frontend_std_0',0x799c8:'nrf_log_frontend_std_1',0x277aa:'__aeabi_memclr'}
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
 sources+=['#include <stdint.h>', 'uint32_t r1_sleep_sync_context_prefix[3] __attribute__((section(".r1.sleep.sync.context"),aligned(4)))={0};']
 initialized=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(initialized)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and initialized.read_bytes()[0x200067b4-0x200064a8:0x200067c0-0x200064a8]==bytes(12)
 src=ROOT/'r1/components/runtime/native_sleep_sync_status.c' ;src.write_text('\n'.join(sources)+'\n');c=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,providers={hex(a):n for a,n in PROVIDERS.items()},native_code_bytes=228,native_span_bytes=412,new_ram_state_bytes=12,context_prefix_address="0x200067b4",initialized_data_sha256=sha(initialized),full_context_extent_owned=False,io_callbacks_unresolved=True,whole_image_complete=False);(OUT/'contracts.json').write_text(json.dumps(c,indent=2)+'\n');print('Recovered sleep sync-status backend and authenticated12-byte zero context prefix')
if __name__=='__main__':main()
