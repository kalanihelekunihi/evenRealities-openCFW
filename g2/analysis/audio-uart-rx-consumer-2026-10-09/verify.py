from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
bind={'xStreamBufferReceive':0x57e136,'prvReadMessageFromBuffer':0x57e220,'prvReadBytesFromBuffer':0x57e2f6,'prvBytesInBuffer':0x57e38c};STATE=0x20040000;BUF=0x20041000;DST=0x20048000
providers={int(v,16):k for k,v in rec['external_aliases'].items()};regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);length=f.get('length',2049);tail=f.get('tail',0);n=f.get('bytes',205);message=f.get('message',0);payload=bytes((i*17+3)&255 for i in range(n));data=(struct.pack('<I',n) if message else b'')+payload;avail=len(data);head=(tail+avail)%length;buffer=bytearray(b'\xa5'*length)
 for i,b in enumerate(data):buffer[(tail+i)%length]=b
 u.mem_write(BUF,bytes(buffer));u.mem_write(DST,b'\xee'*1028);u.mem_write(STATE,struct.pack('<7I',tail,head,length,1,0,f.get('waiter',0),BUF)+bytes([message,0,0,0])+struct.pack('<I',0));cap=f.get('capacity',1024)
 args={'xStreamBufferReceive':[STATE,DST,cap,f.get('ticks',0)],'prvReadMessageFromBuffer':[STATE,DST,cap,avail],'prvReadBytesFromBuffer':[STATE,DST,f.get('count',n),tail],'prvBytesInBuffer':[STATE]}[name]
 for reg,val in zip(regs,args):u.reg_write(reg,val)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);stop=[];calls=[];pcs=set()
 def hook(uc,pc,size,user):
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if pc in providers:
   label=providers[pc]
   if label=='receiver_notify':
    calls.append([label,*[uc.reg_read(r) for r in regs],int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')]);stop.append('before-notify');uc.emu_stop();return
   if label=='receiver_critical_enter':calls.append([label]);stop.append('before-critical-enter');uc.emu_stop();return
   assert label in ['receiver_suspend','receiver_resume'],label
   calls.append([label]);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if native:assert 0x100000<=pc<0x104000,hex(pc);pcs.add(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1)
 for _ in range(20000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop,(name,f,native)
 dst=bytes(u.mem_read(DST,1028));u.mem_write(BUF,b'Z'*length);assert dst==bytes(u.mem_read(DST,1028))
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] else None,'state':bytes(u.mem_read(STATE,36)).hex(),'destination':dst.hex(),'provider_calls':calls,'destination_unchanged_after_ring_reuse':True},pcs
if __name__=='__main__':
 cases=[]
 for name,message,tail,n,cap in itertools.product(['xStreamBufferReceive','prvReadMessageFromBuffer'],[0,1],[0,2046,2048],[0,1,3,15,205],[0,1,3,204,205,1024]):cases.append((name,dict(message=message,tail=tail,bytes=n,capacity=cap)))
 for tail,n in itertools.product([0,2046,2048],[1,3,205]):cases.append(('prvReadBytesFromBuffer',dict(tail=tail,bytes=n,count=n)))
 for tail,n in itertools.product([0,2046,2048],[0,1,205]):cases.append(('prvBytesInBuffer',dict(tail=tail,bytes=n)))
 for n,cap in itertools.product([0,3,205],[0,3,205]):cases.append(('xStreamBufferReceive',dict(bytes=n,capacity=cap,waiter=0x20050000)))
 for n,ticks in itertools.product([0,205],[1,0xffffffff]):cases.append(('xStreamBufferReceive',dict(bytes=n,ticks=ticks)))
 rows=[];pcs=set()
 for name,f in cases:
  a,_=run(name,f,False);b,p=run(name,f,True);assert a==b,(name,f,{k:(a[k],b[k]) for k in a if a[k]!=b[k]});rows.append({'function':name,'fixture':f,'observed':a});pcs|=p
 (D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'comparisons':rows,'reached_native_addresses':sorted(map(hex,pcs)),'limits':'Nonblocking copy plus before-notify/critical cuts. Suspend/resume explicit zero-return stubs; no actual scheduler/task notification, blocking completion or preemption. Ring overwrite proves independent destination fixture copy.'},indent=2)+'\n');print('PASS',len(rows))
