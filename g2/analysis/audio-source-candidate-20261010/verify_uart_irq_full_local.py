#!/usr/bin/env python3
"""Rebuild and compare the source-backed UART IRQ local graph with explicit cuts."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
import probe_uart_irq_original as oracle
A=Path(__file__).resolve().parent
sources=(A/'uart_irq_local_candidate.c',A/'uart_irq_lower_candidate.c',A/'uart_irq_rx_abort_candidate.c',A/'uart_irq_read_abort_candidate.c',A/'uart_irq_read_sm_candidate.c',A/'uart_irq_fifo_drain_bridge.c',A/'uart_irq_tx_bridge.c',A/'../../components/audio/uart_tx_offline/am_hal_queue.c',A/'uart_irq_oracle_stubs.c')
with tempfile.TemporaryDirectory(prefix='g2-uart-irq-full-local-') as td:
 t=Path(td);objects=[];m55={}
 for i,src in enumerate(sources):
  target=t/f'{i}-m55.o'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O1','-ffreestanding','-fno-builtin','-c',str(src),'-o',str(target)],check=True)
  m55[src.name]=hashlib.sha256(target.read_bytes()).hexdigest()
  # M4 O0 only for branches where Unicorn skips M55 IT-conditional loads.
  if src.name in ('uart_irq_read_abort_candidate.c','uart_irq_read_sm_candidate.c','uart_irq_fifo_drain_bridge.c','uart_irq_tx_bridge.c','am_hal_queue.c'):
   obj=t/f'{i}-m4.o'
   subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O0','-ffreestanding','-fno-builtin','-c',str(src),'-o',str(obj)],check=True)
  else:obj=target
  objects.append(obj)
 elf=t/'joint.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,codec_irq_service',*map(str,objects),'-o',str(elf)],check=True)
 oracle.load_native_elf(elf);rows=[]
 def compare(group,active,status,cb,ptr,mask=0,**state):
  kw=dict(execute_lower=True,execute_tx=True,execute_rx_abort=True,execute_read_abort=True,execute_fifo_drain=True,execute_read_sm=True,fr=0x10)
  kw.update(state)
  a=oracle.run(active,status,cb,ptr,mask,native=False,**kw)
  b=oracle.run(active,status,cb,ptr,mask,native=True,**kw)
  assert a==b,(group,active,status,cb,ptr,state,{k:(a[k],b[k]) for k in a if a[k]!=b[k]})
  rows.append(dict(group=group,active=active,status=status,callback=cb,count_pointer=ptr,mask=mask,state=state,calls=a['calls'],tx_writes=a['tx_writes'],rx_reads=a['rx_reads'],return_status=a['ret']))
 for active,status,reading,writing,cb,queue in itertools.product((0,1),(0,1,0x10,0x20,0x40,0x70,0x800,0x1000,0x1851),(0,1),(0,1),(0,1),(0,1)):
  compare('broad',active,status,cb,1,reading=reading,writing=writing,rx_len=3,tx_len=3,rx_queue=queue,rx_callback=cb)
 for writing,length,status,queued,occupied in itertools.product((0,1),(0,1,3,32),(0x20,0x21,0x70),(0,1),(0,3)):
  compare('tx_queue',0,status,0,0,writing=writing,tx_len=length,queued=queued,occupancy=occupied)
 for status,cr,fr,reading,mask in itertools.product((0x40,0x840,0x1840),(0,0x4a00),(0,8),(0,1),(0,1)):
  compare('rx_abort',1,status,1,1,mask,cr=cr,fr=fr,reading=reading,dr_read_limit=1)
 for count,dr,fr,reading in itertools.product((1,3),(0x42,0x142),(0,8),(0,1)):
  compare('rx_fifo',1,0x40,0,1,reading=reading,fr=fr,dr_read_limit=count,dr_value=dr)
 for length,count,cb,queue,occupied in itertools.product((0,1,3),(1,3),(0,1),(0,1),(0,3)):
  compare('rx_read',0,0x10,0,0,reading=1,rx_len=length,rx_queue=queue,rx_occupancy=occupied,rx_callback=cb,fr=0,dr_read_limit=count)
 for status,ies,rsr,reading,queue in itertools.product((0x800,0x1000,0x1800,0x1851),(0,0x80,0x1000),(0,1,0x3f),(0,1),(0,1)):
  compare('error_queue',1,status,1,1,reading=reading,rx_queue=queue,ies=ies,rsr=rsr,fr=0x10)
 for length,count,occupied,queue in itertools.product((0,1,3,7),(1,3),(0,1,3,7),(0,1)):
  compare('rx_queue_edge',0,0x10,0,0,reading=1,rx_len=length,rx_queue=queue,rx_occupancy=occupied,fr=0,dr_read_limit=count)
 out=dict(status='PASS_LOCAL_GRAPH_WITH_MEMSET_DELAY_CUTS',cases=len(rows),groups={g:sum(r['group']==g for r in rows) for g in ('broad','tx_queue','rx_abort','rx_fifo','rx_read','error_queue','rx_queue_edge')},source_sha256={str(src.resolve()):hashlib.sha256(src.read_bytes()).hexdigest() for src in sources},m55_object_sha256=m55,mixed_m4_comparison_elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),official_payload_sha256=hashlib.sha256(oracle.RAW).hexdigest(),rows=rows,limits=['Stock memset at 0x43c0e4 is replaced by an explicit parameterized memory effect because Unicorn loops on its IT block; source read-abort uses a C loop.','Baud delay at 0x4807a0 is an explicit call-argument boundary in this suite; prior timing suite covers its local arithmetic/ITCM spin separately.','FIFO occupancy/readiness and UART registers are synthetic; M55 targets compile, M4 O0 comparison objects avoid a Unicorn conditional-load execution defect.','No archive admission, real exception delivery, physical UART waveform or asynchronous timing claim.'])
 (A/'uart-irq-full-local-results.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PASS',len(rows),'joined local graph cases',out['groups'])
