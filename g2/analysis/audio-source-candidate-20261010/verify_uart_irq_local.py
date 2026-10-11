#!/usr/bin/env python3
"""Compare bounded stock/local UART service while declaring lower cuts explicitly."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
import probe_uart_irq_original as oracle
A=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='g2-uart-irq-local-') as t:
 t=Path(t);obj=t/'service.o';stub=t/'stubs.o';elf=t/'service.elf'
 common=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O1','-ffreestanding','-fno-builtin']
 subprocess.run(common+['-c',str(A/'uart_irq_local_candidate.c'),'-o',str(obj)],check=True)
 subprocess.run(common+['-c',str(A/'uart_irq_all_cut_stubs.c'),'-o',str(stub)],check=True)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,codec_irq_service',str(obj),str(stub),'-o',str(elf)],check=True)
 oracle.load_native_elf(elf)
 rows=[]
 statuses=(0,1,0x10,0x20,0x40,0x50,0x800,0x1000,0x1841,0x1851)
 for active,status,cb,ptr,count in itertools.product((0,1),statuses,(0,1),(0,1),(0,3,0xabc,0x12345)):
  kw=dict(valid=1,raw_count=count)
  original=oracle.run(active,status,cb,ptr,0,native=False,**kw)
  source=oracle.run(active,status,cb,ptr,0,native=True,**kw)
  assert original==source,(active,status,cb,ptr,count,{k:(original[k],source[k]) for k in original if original[k]!=source[k]})
  rows.append(dict(active=active,status=status,callback=cb,count_pointer=ptr,raw_count=count,calls=original['calls'],ret=original['ret'],count=original['count'],callback_cell=original['callback_cell'],dma_busy=original['dma_busy']))
 for valid in (0,2):
  for active,status in itertools.product((0,1),statuses):
   original=oracle.run(active,status,1,1,0,native=False,valid=valid)
   source=oracle.run(active,status,1,1,0,native=True,valid=valid)
   assert original==source,(valid,active,status)
   rows.append(dict(valid=valid,active=active,status=status,calls=original['calls'],ret=original['ret']))
 out=dict(status='PASS_LOCAL_BODY_WITH_EXPLICIT_LOWER_CUTS',cases=len(rows),source_sha256=hashlib.sha256((A/'uart_irq_local_candidate.c').read_bytes()).hexdigest(),stub_sha256=hashlib.sha256((A/'uart_irq_all_cut_stubs.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),official_payload_sha256=hashlib.sha256(oracle.RAW).hexdigest(),rows=rows,limits=['Six lower helpers return at their entry with synthetic get_int_err result 0x77; their side effects are not compared.','Callback target returns immediately; callback arguments and order, pointer clear, count write, full handle and UART fixture memory, SP and return are compared.','No full provider or exception-delivery, physical interrupt, UART waveform, or hardware timing claim.'])
 (A/'uart-irq-local-results.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PASS',len(rows),'bounded stock/source local service cases')
