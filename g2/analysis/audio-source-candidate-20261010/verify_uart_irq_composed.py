#!/usr/bin/env python3
"""Compose three stock-corrected UART lower helpers with the IRQ public entry."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
import probe_uart_irq_original as oracle
A=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='g2-uart-irq-composed-') as t:
 t=Path(t);objs=[];elf=t/'composed.elf'
 common=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O1','-ffreestanding','-fno-builtin']
 for name in ('uart_irq_local_candidate.c','uart_irq_lower_candidate.c','uart_irq_three_lower_cuts.c'):
  obj=t/(name+'.o');subprocess.run(common+['-c',str(A/name),'-o',str(obj)],check=True);objs.append(obj)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,codec_irq_service',*map(str,objs),'-o',str(elf)],check=True)
 oracle.load_native_elf(elf)
 rows=[];status_values=(0,1,0x10,0x20,0x40,0x50,0x800,0x880,0x900,0xa00,0xc00,0x1000,0x1800,0x1841,0x1851,0x1c00)
 for active,status,cb,ptr,count,ies,rsr,dcr in itertools.product((0,1),status_values,(0,1),(0,1),(3,0x12345),(0,0x80,0x1000),(0,0x3f),(0,0xa5)):
  kw=dict(raw_count=count,ies=ies,rsr=rsr,dcr=dcr,execute_lower=True)
  original=oracle.run(active,status,cb,ptr,0,native=False,**kw)
  source=oracle.run(active,status,cb,ptr,0,native=True,**kw)
  assert original==source,(active,status,cb,ptr,count,ies,rsr,dcr,{k:(original[k],source[k]) for k in original if original[k]!=source[k]})
  rows.append(dict(active=active,status=status,callback=cb,count_pointer=ptr,raw_count=count,ies=ies,rsr=rsr,dcr=dcr,calls=original['calls'],ret=original['ret'],count=original['count'],callback_cell=original['callback_cell'],dma_busy=original['dma_busy']))
 out=dict(status='PASS_PUBLIC_PLUS_THREE_LOWER_WITH_THREE_CUTS',cases=len(rows),sources={name:hashlib.sha256((A/name).read_bytes()).hexdigest() for name in ('uart_irq_local_candidate.c','uart_irq_lower_candidate.c','uart_irq_three_lower_cuts.c')},elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),official_payload_sha256=hashlib.sha256(oracle.RAW).hexdigest(),rows=rows,limits=['Public entry and original/source DMA abort, DMA complete and error-status helper bodies execute with synthetic UART registers.','RX abort, RX read state machine and TX write state machine still return at explicit lower boundaries.','Callback target returns immediately; full handle and UART fixture memory, call order/arguments, return and SP compare.','No archive admission, exception delivery, asynchronous timing, or hardware UART claim.'])
 (A/'uart-irq-composed-results.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PASS',len(rows),'public plus three lower source cases')
