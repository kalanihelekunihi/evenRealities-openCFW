#!/usr/bin/env python3
"""Join selected pinned TX source to the UART IRQ public-entry oracle."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
import probe_uart_irq_original as oracle
A=Path(__file__).resolve().parent
TX=A/'../../components/audio/uart_tx_offline/am_hal_uart.c'
QUEUE=A/'../../components/audio/uart_tx_offline/am_hal_queue.c'
with tempfile.TemporaryDirectory(prefix='g2-uart-irq-tx-') as t:
 t=Path(t);objects=[]
 for source in (A/'uart_irq_local_candidate.c',A/'uart_irq_lower_candidate.c',A/'uart_irq_oracle_stubs.c',A/'uart_irq_rx_cuts.c'):
  obj=t/(source.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O1','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True);objects.append(obj)
 for source in (A/'uart_irq_tx_bridge.c',QUEUE):
  obj=t/(source.stem+'-m4.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O0','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(obj)],check=True);objects.append(obj)
 # Keep target compile evidence distinct from the M4 comparison build.
 m55=t/'tx-m55.o';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O1','-ffreestanding','-fno-builtin','-c',str(A/'uart_irq_tx_bridge.c'),'-o',str(m55)],check=True)
 elf=t/'joint.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,codec_irq_service',*map(str,objects),'-o',str(elf)],check=True)
 oracle.load_native_elf(elf);rows=[]
 for writing,length,status,queued,occupied in itertools.product((0,1),(0,1,3,32),(0x20,0x21,0x70),(0,1),(0,3)):
  kw=dict(execute_lower=True,execute_tx=True,writing=writing,tx_len=length,queued=queued,occupancy=occupied)
  original=oracle.run(0,status,0,0,0,native=False,**kw)
  source=oracle.run(0,status,0,0,0,native=True,**kw)
  assert original==source,(writing,length,status,queued,occupied,{k:(original[k],source[k]) for k in original if original[k]!=source[k]})
  rows.append(dict(writing=writing,length=length,status=status,queued=queued,occupied=occupied,tx_writes=original['tx_writes'],output=original['tx_out']))
 out=dict(status='PASS_PUBLIC_PLUS_TX_WITH_RX_CUT',cases=len(rows),sources={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in (A/'uart_irq_local_candidate.c',A/'uart_irq_lower_candidate.c',A/'uart_irq_tx_bridge.c',TX,QUEUE)},m55_tx_bridge_object_sha256=hashlib.sha256(m55.read_bytes()).hexdigest(),m4_comparison_elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),official_payload_sha256=hashlib.sha256(oracle.RAW).hexdigest(),rows=rows,limits=['TX source body and queue source execute in public-entry fixture; RX read remains intercepted for status 0x70.','M4 -O0 comparison build avoids Unicorn mishandling of M55 ITT-conditional loads; M55 target compilation is separately recorded and not executed in this suite.','Synthetic FIFO and queue RAM, no physical UART waveform or exception timing.'])
 (A/'uart-irq-tx-joint-results.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PASS',len(rows),'TX joint public-entry cases')
