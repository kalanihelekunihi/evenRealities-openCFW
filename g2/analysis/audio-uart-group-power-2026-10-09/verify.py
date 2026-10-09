from pathlib import Path
import json,subprocess,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
bind={'uart_group_can_poll':0x47f6f2,'uart_power_pre':0x48032c,'uart_power_post':0x480342,'uart_group_control':0x480312,'uart_status_wait':0x480826}
def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40021000,0x1000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 w(0x40021004,f.get('enabled',0));w(0x40021008,f.get('status',0));w(0x20073274,0x10ff11 if f.get('callback') else 0);w(0x2007327c,0x10ff11 if f.get('callback') else 0);w(0x20073280,0x10ff11 if f.get('callback') else 0)
 args={'uart_group_can_poll':[f.get('domain',11)],'uart_power_pre':[],'uart_power_post':[],'uart_group_control':[f.get('action',3),f.get('enable',1),0x20041000],'uart_status_wait':[f.get('budget',5),0x40021008,f.get('mask',0x1e00),f.get('expected',0x1e00),f.get('equal',1)]}[name]
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
 for reg,val in zip(regs,args):u.reg_write(reg,val)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);w(0x200ff000,args[4] if len(args)>4 else 0);u.reg_write(UC_ARM_REG_LR,0x10ff01);stop=[];trace=[];delays=[];callback=[];pcs=set()
 def mem(uc,access,a,size,value,user):
  if 0x40021000<=a<0x40022000:trace.append(['R' if access==UC_MEM_READ else 'W',hex(a),size,int.from_bytes(uc.mem_read(a,size),'little') if access==UC_MEM_READ else value])
 def hook(uc,pc,size,user):
  if pc==0x4807a0:
   delays.append(uc.reg_read(UC_ARM_REG_R0))
   if len(delays)==f.get('change_after',-1):w(0x40021008,f.get('changed_status',0x1e00))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10ff10:
   # External callback body is not executed; compare only declared arguments.
   callback.extend([uc.reg_read(x) for x in regs[:3]] if name=='uart_group_control' else []);stop.append('before-callback');uc.emu_stop();return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x104000,hex(pc);pcs.add(pc)
 u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1)
 for _ in range(10000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] else None,'mmio_trace':trace,'delays':delays,'callback_arguments':callback},pcs
if __name__=='__main__':
 cases=[]
 for domain,enabled in itertools.product([11,12,13,14,267,268,269,270],[0,0x200,0x400,0x800,0x1000,0x1e00,1,0xffffffff]):cases.append(('uart_group_can_poll',dict(domain=domain,enabled=enabled)))
 for name in ['uart_power_pre','uart_power_post']:
  for callback in [0,1]:cases.append((name,dict(callback=callback)))
 for action,enable,callback in itertools.product([3,259],[0,1,256,257],[0,1]):cases.append(('uart_group_control',dict(action=action,enable=enable,callback=callback)))
 for budget,status,equal,change in itertools.product([0,1,5],[0,0x200,0x1e00,0xffffffff],[0,1,256,257],[-1,1,3]):cases.append(('uart_status_wait',dict(budget=budget,status=status,equal=equal,change_after=change)))
 for expected,mask in itertools.product([0,0x200,0x1e00,0xffffffff],[0,0x200,0x1e00]):cases.append(('uart_status_wait',dict(expected=expected,mask=mask,status=0x1e00,budget=1)))
 rows=[];pcs=set()
 for name,f in cases:
  a,_=run(name,f,False);b,p=run(name,f,True);assert a==b,(name,f,a,b);rows.append({'function':name,'fixture':f,'observed':a});pcs|=p
 (D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'comparisons':rows,'reached_native_addresses':sorted(map(hex,pcs)),'limits':'UART-domain predicate subset; ordered MMIO traces compared. Delay/status fixtures synthetic, callback cases stop before body. No physical power, callback execution or scheduling proof.'},indent=2)+'\n');print('PASS',len(rows))
