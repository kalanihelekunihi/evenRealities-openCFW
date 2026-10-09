from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent; R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
bind={'am_hal_uart_power_control':0x58dbb8,'am_hal_uart_configure':0x58e09e,'am_hal_uart_interrupt_clear':0x58e7e4,'config_baudrate':0x58de38}; providers={0x47f5b8:('enable',1),0x47f7ae:('disable',1),0x4c44bc:('request',2),0x4c4530:('release',2)}
STATE=0x20040000;CFG=0x20041000;OUT=0x20042000

def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x4000);u.mem_map(0x40020000,0x1000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 module=f.get('module',1);base=0x40039000+module*0x1000
 u.mem_write(STATE,b'\xa5'*284);w(STATE,0x1ea9e06);w(STATE+40,module);w(STATE+48,f.get('baud',921600));u.mem_write(STATE+4,bytes([f.get('saved',1)]));u.mem_write(STATE+280,bytes([f.get('clockid',4)]))
 for i in range(8):w(STATE+8+4*i,0xabc00000+i)
 u.mem_write(base,bytes((i*13+7)&255 for i in range(0x4c)));w(base+0x30,f.get('clksel',1)<<4|8);w(0x4002000c,f.get('revision',0x22));w(0x400201b0,0xffffffff);w(OUT,0xeeeeeeee)
 u.mem_write(CFG,struct.pack('<I4BH5B',f.get('baud',921600),f.get('data',3),f.get('parity',2),f.get('stop',0),0,f.get('flow',0),f.get('tx',2),f.get('rx',2),f.get('clock',0),0,0)+b'\0')
 handle=STATE if f.get('valid',1) else 0
 args={'am_hal_uart_power_control':[handle,f.get('power',0),f.get('retain',1)],'am_hal_uart_configure':[handle,CFG],'am_hal_uart_interrupt_clear':[handle,0x12345678],'config_baudrate':[module,f.get('baud',921600),OUT]}[name]
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);calls=[];stop=[];pcs=set()
 def hook(uc,pc,size,user):
  if pc in providers:
   label,n=providers[pc];calls.append([label,*[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1][:n]]]);uc.reg_write(UC_ARM_REG_R0,f.get('provider_status',0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x104000,hex(pc);pcs.add(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1)
 for _ in range(30000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop,(name,f,native,hex(u.reg_read(UC_ARM_REG_PC)))
 return {'return':u.reg_read(UC_ARM_REG_R0),'state':bytes(u.mem_read(STATE,284)).hex(),'registers':bytes(u.mem_read(base,0x4c)).hex(),'gate':int.from_bytes(u.mem_read(0x400201b0,4),'little'),'out':int.from_bytes(u.mem_read(OUT,4),'little'),'providers':calls},pcs
if __name__=='__main__':
 cases=[]
 for power,retain,saved,revision,baud,ps in itertools.product([0,1,2,3],[0,1],[0,1],[0x21,0x22],[1500000,1500001],[0,7]):cases.append(('am_hal_uart_power_control',dict(power=power,retain=retain,saved=saved,revision=revision,baud=baud,provider_status=ps)))
 for clock,revision,baud in itertools.product([0,1,2],[0x21,0x22],[921600,1500000,1500001,3000000,4000000]):cases.append(('am_hal_uart_configure',dict(clock=clock,revision=revision,baud=baud)))
 for clksel,baud in itertools.product(range(8),[9600,921600,1500000,3000000,4000000]):cases.append(('config_baudrate',dict(clksel=clksel,baud=baud)))
 for parity,data,stop,flow in itertools.product([0,1,2,3],[0,3],[0,1],[0,0xc000]):cases.append(('am_hal_uart_configure',dict(parity=parity,data=data,stop=stop,flow=flow,tx=7,rx=0)))
 for name in bind:
  if name not in ('config_baudrate','am_hal_uart_interrupt_clear'):cases.append((name,{'valid':0}))
 cases.append(('am_hal_uart_interrupt_clear',{}))
 for module,power,retain,ps in itertools.product([0,3],[0,1,2],[0,1],[0,7]):cases.append(('am_hal_uart_power_control',dict(module=module,power=power,retain=retain,provider_status=ps,baud=1500001)))
 for module,clock,ps in itertools.product([0,3],[0,1],[0,7]):cases.append(('am_hal_uart_configure',dict(module=module,clock=clock,provider_status=ps)))
 rows=[];pcs=set()
 for name,f in cases:
  a,_=run(name,f,False);b,p=run(name,f,True);assert a==b,(name,f,{k:(a[k],b[k]) for k in a if a[k]!=b[k]});rows.append({'function':name,'fixture':f,'observed':a});pcs|=p
 (D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'comparisons':rows,'reached_native_addresses':sorted(map(hex,pcs)),'limits':'Original unchanged instructions versus source; power/clock explicit return stubs; synthetic registers. Nonzero denominator selected division only; no physical power/clock, scheduling or full runtime ABI.'},indent=2)+'\n');print('PASS',len(rows))
