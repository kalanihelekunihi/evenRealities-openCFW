from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
T=0x20006000;CURRENT=0x20005000;DELAY=0x20007000;PREV=0x20008000;WOKEN=PREV+4;READY=0x2006a49c;PENDING=0x20073d24

def run(f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x2000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 def empty_list(a):u.mem_write(a,struct.pack('<5I',0,a+8,0xffffffff,a+8,a+8))
 for p in range(6):empty_list(READY+20*p)
 empty_list(PENDING);empty_list(DELAY);w(DELAY,1);w(DELAY+4,T+4);w(DELAY+12,T+4);w(DELAY+16,T+4);u.mem_write(T+4,struct.pack('<5I',100,DELAY+8,DELAY+8,T,DELAY));w(T+36,T);w(T+44,f['priority']);w(T+104,f['old']);u.mem_write(T+108,bytes([f['state']]));w(CURRENT+44,1);w(0x20074a20,CURRENT);w(0x20074a58,f['suspended']);w(0x20074a38,0);w(PREV,0xeeeeeeee);w(WOKEN,0x11111111);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,struct.pack('<2I',PREV if f['previous'] else 0,WOKEN if f['woken'] else 0));u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_BASEPRI,f['basepri']);u.reg_write(UC_ARM_REG_R0,T);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,0x4);u.reg_write(UC_ARM_REG_R3,f['action']);stop=[];writes=[];pcs=set();pendsv=[];flagptr=[]
 STREAM=0x20040000;BUF=0x20041000;SRC=0x20048000
 u.mem_write(STREAM,struct.pack('<7I',0,f['head'],2049,1,T,0,BUF)+bytes(8));w(0x200748bc,STREAM);u.mem_write(SRC,bytes((i*17+3)&255 for i in range(f['bytes'])));u.reg_write(UC_ARM_REG_R0,SRC);u.reg_write(UC_ARM_REG_R1,f['bytes'])
 def mem(uc,access,a,size,value,user):
  if a==0xe000ed04:pendsv.append(value)
  if T<=a<T+128 or a in [0x20074a38,0x20074a44] or READY<=a<READY+120 or DELAY<=a<DELAY+20 or PENDING<=a<PENDING+20 or PREV<=a<PREV+8:
   writes.append([hex(a),size,hex(value),uc.reg_read(UC_ARM_REG_BASEPRI)])
 def hook(uc,pc,size,user):
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if pc==0x57e05e:
   flagptr.append(uc.reg_read(UC_ARM_REG_R3))
   if native:uc.reg_write(UC_ARM_REG_PC,syms['xStreamBufferSendFromISR']|1);return
  if native:assert 0x100000<=pc<0x104000 or 0x5415e6<=pc<0x541600,hex(pc);pcs.add(pc)
 u.hook_add(UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,0x5415e7)
 for _ in range(30000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop
 observed={'return':u.reg_read(UC_ARM_REG_R0),'task':bytes(u.mem_read(T,128)).hex(),'delayed_list':bytes(u.mem_read(DELAY,20)).hex(),'pending_list':bytes(u.mem_read(PENDING,20)).hex(),'ready_lists':bytes(u.mem_read(READY,120)).hex(),'top_priority':int.from_bytes(u.mem_read(0x20074a38,4),'little'),'yield_pending':int.from_bytes(u.mem_read(0x20074a44,4),'little'),'outputs':bytes(u.mem_read(PREV,8)).hex(),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'pendsv_writes':pendsv,'ordered_writes':writes,'stream_state':bytes(u.mem_read(STREAM,36)).hex(),'stream_storage':bytes(u.mem_read(BUF,2049)).hex(),'caller_woken_flag':int.from_bytes(u.mem_read(flagptr[0],4),'little') if flagptr else None}
 assert not pendsv;assert observed['basepri']==f['basepri'];assert all(x[3]==0x30 for x in writes)
 return observed,pcs
if __name__=='__main__':
 rows=[];pcs=set()
 for priority,suspended,head,n in itertools.product([0,2],[0,1],[0,2046,2048],[0,3,205]):
  f=dict(priority=priority,state=1,suspended=suspended,action=0,previous=0,woken=0,basepri=0,old=0x100,head=head,bytes=n);a,_=run(f,False);b,p=run(f,True);assert a==b,(f,{k:(a[k],b[k]) for k in a if a[k]!=b[k]});rows.append({'fixture':f,'observed':a});pcs|=p
 (D/'stream-notifier-composition-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'reached_native_addresses':sorted(map(hex,pcs)),'limits':'Actual original logger callback and original/source stream sender plus native reconstructed notifier. Synthetic initialized waiting TCB/lists and stream pressure; no IRQ delivery/preemption. No PendSV write; software pending state not a performed switch.'},indent=2)+'\n');print('PASS',len(rows))
