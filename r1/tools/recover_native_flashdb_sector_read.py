#!/usr/bin/env python3
"""Recover symbolic native TSDB log reader, flash adapter and status decoder."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-flashdb-sector-read';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BODIES=[(0x87c24,0x87d8c,'r1_fdb_native_read_sector')]
PROVIDERS={0x3f03e:'r1_fdb_native_flash_read',0x3f076:'r1_fdb_native_get_status',0x38060:'r1_native_printf',0x3f014:'r1_fdb_native_db_path',0x87e14:'r1_fdb_native_read_tsl'}
def main():
 OUT.mkdir(exist_ok=True);elf=BASE/'i2c5/stock-analysis-exec.elf';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';sources=['/* Symbolic native FlashDB sector read; no instruction-byte arrays. */'];contracts=[]
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
  lines+=['FDI_87d8c:', '.word 0x304c5354']
  for a,textval,nexta in [(0x87d90,'[FlashDB][tsl]',0x87da0),(0x87da0,'[%s][%s] ',0x87dac),(0x87db0,'sector',0x87db8),(0x87db8,'(%s) has assert failed at %s.\n',0x87dd8),(0x87dd8,'0',0x87ddc),(0x87ddc,'Error: this TSL (0x%08X) size (%u) is out of bound.\n',0x87e14)]:
   payload=textval.encode()+b'\0';pad=nexta-a-len(payload);assert raw[a-0x27000:a-0x27000+len(payload)]==payload and raw[a-0x27000+len(payload):nexta-0x27000]==bytes(pad)
   if a==0x87db0:lines+=['FDI_87dac:', '.word r1_fdb_sector_function_name']
   lines+=['FDI_'+hex(a)[2:]+':','.asciz '+json.dumps(textval)]
   if pad:lines+=['.space '+str(pad)+',0']
  source='\n'.join(lines)+'\n';sources+=['__attribute__((naked,section(".text.'+name+'"))) void '+name+'(void) { __asm__ volatile('+json.dumps(source)+'); }'];contracts.append(dict(address=hex(start),code_bytes=end-start,source_span_bytes=496,symbol=name,instructions=instructions,disassembly_sha256=sha(path)))
 src=ROOT/'r1/components/runtime/native_flashdb_sector_read.c';sources+=['const char r1_fdb_sector_function_name[] __attribute__((aligned(1),section(".r1.fdb.sector_function_name")))="read_sector_info";'];src.write_text('\n'.join(sources)+'\n');report=dict(application_sha256=sha(app),analysis_elf_sha256=sha(elf),frozen_pseudocode_sha256=sha(ROOT/'r1/research/decompilation/application/decompiler-output.c'),generator_sha256=sha(Path(__file__)),source_sha256=sha(src),bodies=contracts,providers={hex(a):n for a,n in PROVIDERS.items()},native_code_bytes=sum(x['code_bytes'] for x in contracts),whole_image_complete=False)
 (OUT/'contracts.json').write_text(json.dumps(report,indent=2)+'\n');print('Recovered symbolic sector read and source-owned assertion name')
if __name__=='__main__':main()
