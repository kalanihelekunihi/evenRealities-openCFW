"""Stock/source RX original instructions, finite FIFO input, no RX or ring answer stubs."""
import argparse,hashlib,json,itertools,struct,importlib.util
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5];s=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(s);s.loader.exec_module(elf)
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-uart-rx.elf'));ap.add_argument('--output',type=Path,default=Path(__file__).with_name('comparison.json'));args=ap.parse_args();_,segments,symbols=elf.elf_info(args.elf)
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
P=0x20024400;D=0x20001000;BUF=0x20002000;RING=0x20003000;OUT=0x20004000;STOP=0x08000000;CB=0x08000100;UART=0x40039000
ENTRIES={'claim':('opencfw_boot_uart_rx_claim',0x422f4c,0x422fa2),'cancel':('opencfw_boot_uart_rx_cancel',0x422fa2,0x422fde),'fifo':('opencfw_boot_uart_rx_fifo',0x4232c8,0x42330e),'collect':('opencfw_boot_uart_rx_collect',0x423350,0x423390),'blocking':('opencfw_boot_uart_rx_blocking',0x42348e,0x4234d8),'start':('opencfw_boot_uart_rx_start',0x4234fa,0x423524),'pump':('opencfw_boot_uart_rx_pump',0x423608,0x4236ce)}
if 'opencfw_boot_uart_transfer' in symbols:ENTRIES['transfer']=('opencfw_boot_uart_transfer',0x4233e8,0x423444)
trace={}
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);mapped=set()
 for start,size in [(0x410000,0x25000),(0x20000000,0x40000),(STOP,0x10000),(UART,0x4000)]:u.mem_map(start,size);mapped.update(range(start,start+size,4096))
 if source:
  for seg in segments:
   address,data=seg['address'],seg['data']
   for page in range(address&~4095,(address+seg['memory_size']+4095)&~4095,4096):
    if page not in mapped:u.mem_map(page,4096);mapped.add(page)
   u.mem_write(address,data)
 else:u.mem_write(0x410000,blob)
 def word(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
 def read(p):return int.from_bytes(u.mem_read(p,4),'little')
 uart_base=UART+(f.get('module',0)<<12)
 words=list(f.get('fifo',[17,34,51,68,85,102]));events=[];consumed=[];delays=0;done=False;reason='return'
 def hook_read(cpu,access,p,size,value,data):
  if p==uart_base+0x18:word(p,0 if words else 0x10)
  elif p==uart_base:
   value=words.pop(0) if words else 0;word(p,value);consumed.append(value)
 def hook_code(cpu,pc,size,data):
  nonlocal delays,done,reason
  if pc==STOP:done=True;u.emu_stop();return
  if not source and 0x410000<=pc<0x435000:trace[pc]=bytes(u.mem_read(pc,size)).hex()
  save=(symbols.get('opencfw_bl_critical_save',0)&~1) if source else 0x41b8ec
  if source and pc==save and save>=STOP:
   irq=u.reg_read(a.UC_ARM_REG_PRIMASK);u.reg_write(a.UC_ARM_REG_PRIMASK,1);u.reg_write(a.UC_ARM_REG_R0,irq);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  delay=(symbols['opencfw_boot_delay_us_math']&~1) if source else 0x41d1c0
  if pc==delay:
   delays+=1;events.append(['delay',u.reg_read(a.UC_ARM_REG_R0)])
   if delays==f.get('refill_after'):words.extend(f.get('refill',[]))
   if delays==f.get('stop_after'):
    done=True;reason='synthetic-poll-boundary';u.emu_stop();return
   u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if pc==CB:
   events.append(['callback',u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1),u.reg_read(a.UC_ARM_REG_PRIMASK),read(OUT),read(P+0x9c),u.mem_read(P+0x11a,1)[0]])
   u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,hook_code);u.hook_add(UC_HOOK_MEM_READ,hook_read,begin=UART,end=UART+0x3fff)
 u.mem_write(P,bytes([0xa5])*0x11c);word(P,0x01ea9e06);word(P+0x28,f.get('module',0));u.mem_write(P+0x119,b'\x07');u.mem_write(P+0x11a,bytes([f.get('busy',0)]));u.mem_write(P+0xdd,bytes([f.get('ring',0)]));u.mem_write(RING,bytes(range(64)));u.mem_write(BUF,bytes([0xcc])*64);word(OUT,0xeeeeeeee)
 word(P+0x4c,0);word(P+0x50,0);word(P+0x54,f.get('used',0));word(P+0x58,f.get('capacity',16));word(P+0x5c,f.get('width',1));word(P+0x60,RING)
 descriptor=[BUF,f.get('length',4),OUT if f.get('count_pointer',True) else 0,f.get('timeout',3),CB|1 if f.get('callback',True) else 0,0xdeadbeef,0x12345678]+[0]*6+[f.get('mode',3)];u.mem_write(D,struct.pack('<14I',*descriptor));u.mem_write(P+0x64,struct.pack('<7I',*descriptor[:7]));word(P+0x9c,f.get('progress',0));u.mem_write(P+0x98,b'\xa5')
 u.reg_write(a.UC_ARM_REG_XPSR,0x01000000);u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0))
 values=[P,D] if name in ['claim','start','blocking','transfer'] else [P,0 if f.get('null_buffer') else BUF,f.get('length',4),OUT if f.get('count_pointer',True) else 0] if name=='fifo' else [P]
 for reg,value in zip([a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3],values):u.reg_write(reg,value)
 symbol,original,_=ENTRIES[name];u.emu_start((symbols[symbol] if source else original)|1,STOP+2,count=300000);assert done,(source,name,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
 return {'return':None if name=='pump' or reason!='return' else u.reg_read(a.UC_ARM_REG_R0),'reason':reason,'context':bytes(u.mem_read(P,0x11c)).hex(),'destination':bytes(u.mem_read(BUF,64)).hex(),'ring':bytes(u.mem_read(RING,64)).hex(),'count':read(OUT),'events':events,'consumed':consumed,'remaining_fifo':words,'irq':u.reg_read(a.UC_ARM_REG_PRIMASK)}
fixtures=[]
for name,ring,length,callback,irq in itertools.product(['claim','cancel','start','blocking','pump','collect'],[0,1],[0,1,4,8,17],[False,True],[0,1]):
 f=dict(ring=ring,length=length,callback=callback,irq=irq)
 if name=='pump':f['busy']=1
 fixtures.append((name,f))
for name in ['claim','cancel','start','blocking','pump']:
 for busy in [0,1,2]:fixtures.append((name,dict(busy=busy,fifo=[])))
for length,null,count,irq in itertools.product([0,1,4,8],[False,True],[False,True],[0,1]):fixtures.append(('fifo',dict(length=length,null_buffer=null,count_pointer=count,irq=irq)))
for error in [0x100,0x200,0x400,0x800,0xf00]:
 for name in ['fifo','collect','start','blocking','pump']:
  fixtures.append((name,dict(busy=1 if name=='pump' else 0,ring=1 if name=='collect' else 0,fifo=[1,2,error|3,4,5])))
for callback,used,width,capacity in itertools.product([False,True],[0,3,8],[1,2],[1,4,16]):fixtures.append(('pump',dict(busy=1,ring=1,fifo=[],callback=callback,used=used,width=width,capacity=capacity,length=4)))
for timeout in [0,1,2,3,0xffffffff]:
 fixtures.append(('blocking',dict(fifo=[],refill_after=2,refill=[1,2,3,4],timeout=timeout)))
 if timeout in [0,0xffffffff]:fixtures.append(('blocking',dict(fifo=[],timeout=timeout,stop_after=4)))
for callback in [False,True]:fixtures.append(('start',dict(ring=1,fifo=[1,2,3,4],width=2,capacity=16,callback=callback)))
fixtures.append(('collect',dict(capacity=1,fifo=list(range(32)))))
fixtures.append(('pump',dict(busy=1,ring=1,used=3,capacity=4,fifo=[1,2,0x100|3,4],length=3)))
for module in [1,2,3]:
 for name in ['fifo','start','blocking','pump','collect']:fixtures.append((name,dict(module=module,busy=1 if name=='pump' else 0,ring=1 if name=='collect' else 0)))
if 'transfer' in ENTRIES:
 for mode,ring,length,callback,irq in itertools.product([1,3],[0,1],[0,4,17],[False,True],[0,1]):fixtures.append(('transfer',dict(mode=mode,ring=ring,length=length,callback=callback,irq=irq)))
rows=[]
for name,f in fixtures:
 stock=run(False,name,f);source=run(True,name,f)
 if stock!=source:
  args.output.with_suffix('.failure.json').write_text(json.dumps({'name':name,'fixture':f,'stock':stock,'source':source},indent=2)+'\n');raise AssertionError((name,f,{k:[stock[k],source[k]] for k in stock if stock[k]!=source[k]}))
 rows.append({'name':name,'fixture':f,'result':stock})
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
for p,b in trace.items():assert bytes.fromhex(b)==blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]
r={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/uart_rx.c').read_bytes()).hexdigest(),'visited_body_bytes':{name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in ENTRIES.items()},'original_trace':{hex(p):b for p,b in sorted(trace.items())},'comparisons':rows,'limits':['Original RX/ring/critical/cancel zero-fill instructions execute; source ELF only. Independent module models source critical-save, integrated ELF uses native critical save.','Finite synthetic FIFO reads and refill at delay boundary, no hardware/UART IRQ/race/timing/overrun/drain certification. Callback records observe irq/count/progress/busy at entry then return.','Delay1000 injected; zero/infinite timeout stall observed only at explicit synthetic four-poll boundary, not claimed to finish. No SRAM write hooks or expected-copy models.']};args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['visited_body_bytes'])
