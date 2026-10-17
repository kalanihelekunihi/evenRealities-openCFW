#!/usr/bin/env python3
"""Recover symbolic native TSDB iterator and four bounded navigation helpers."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-flashdb-iterator';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x63ad8,0x63c60,'r1_health_sync_provider_00063ad8'),(0x6a158,0x6a176,'r1_fdb_native_last_sector'),(0x6a176,0x6a194,'r1_fdb_native_last_tsl'),(0x6a194,0x6a1b2,'r1_fdb_native_next_sector'),(0x6a1b2,0x6a1cc,'r1_fdb_native_next_tsl')]
PROVIDERS={0x38060:'r1_native_printf',0x3f014:'r1_fdb_native_db_path',0x2775c:'r1_native_memory_move',0x87c24:'r1_fdb_native_read_sector',0x87e14:'r1_fdb_native_read_tsl'}
def main():
 OUT.mkdir(exist_ok=True);elf=BASE/'i2c5/stock-analysis-exec.elf';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';sources=['/* Symbolic native FlashDB iterator; no instruction-byte arrays. */'];contracts=[]
 for start,end,name in BODIES:
  text=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(elf)],text=True);path=OUT/('disassembly-'+hex(start)[2:]+'.txt');path.write_text(text);lines=[];instructions=[]
  for line in text.splitlines():
   m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(.*)',line)
   if not m:continue
   a=int(m[1],16);size=len(m[2].split())*2;ins=m[3].split('@')[0].strip();op=ins.split()[0];args=ins[len(op):].strip();original=ins
   if op.startswith('ldr') and '[pc,' in args:
    target=re.search(r'@\s*(?:\()?([0-9a-f]+)',line);assert target,line;ins=op+' '+args.split(',')[0]+', FDI_'+target[1]
   elif op=='add' and re.match(r'r\d+, pc,',args):
    target=re.search(r'adr r\d+, ([0-9a-f]+)',line);assert target,line;ins='adr '+args.split(',')[0]+', FDI_'+target[1]
   elif re.match(r'^(b[a-z]*(?:\.[nw])?|cbz|cbnz)$',op) and op not in ['bx','blx']:
    target=re.search(r'\b([0-9a-f]{5,})\s*<',args);assert target,line;t=int(target[1],16)
    label=PROVIDERS[t] if op=='bl' else 'FDI_'+hex(t)[2:];ins=op+' '+re.sub(r'[0-9a-f]{5,}\s*<.*',label,args)
   lines+=['FDI_'+hex(a)[2:]+':',ins];instructions.append(dict(address=hex(a),size=size,assembly=original))
  assert sum(x['size'] for x in instructions)==end-start
  if start==0x63ad8:
   for a,textval,nexta in [(0x63c60,'[FlashDB][tsl]',0x63c70),(0x63c70,'[%s][%s] ',0x63c7c),(0x63c7c,"Error: TSL (%s) isn't initialize OK.\n",0x63ca4)]:
    payload=textval.encode()+b'\0';assert raw[a-0x27000:a-0x27000+len(payload)]==payload;pad=nexta-a-len(payload);assert raw[a-0x27000+len(payload):nexta-0x27000]==bytes(pad);lines+=['FDI_'+hex(a)[2:]+':','.asciz '+json.dumps(textval)];lines+=['.space '+str(pad)+',0'] if pad else []
   for a,n in [(0x63ca4,'r1_fdb_native_next_sector'),(0x63ca8,'r1_fdb_native_next_tsl'),(0x63cac,'r1_fdb_native_last_sector'),(0x63cb0,'r1_fdb_native_last_tsl')]:lines+=['FDI_'+hex(a)[2:]+':','.word '+n]
  source='\n'.join(lines)+'\n';sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps(source)+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=(0x63cb4-start if start==0x63ad8 else end-start),symbol=name,instructions=instructions,disassembly_sha256=sha(path)))
 src=ROOT/'r1/components/runtime/native_flashdb_iterator.c';src.write_text('\n'.join(sources)+'\n');report=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,providers={hex(a):n for a,n in PROVIDERS.items()},native_code_bytes=sum(x['code_bytes'] for x in contracts),whole_image_complete=False)
 (OUT/'contracts.json').write_text(json.dumps(report,indent=2)+'\n');print('Recovered symbolic iterator and four navigation helpers')
if __name__=='__main__':main()
