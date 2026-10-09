from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3};sections=[]
with elf.open('rb') as f:
 for s in ELFFile(f).iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
T=0x20006000;PEER=0x20006100;DL=0x20006400;OL=0x20006500;EV=0x20006600;READY=0x2006a49c;OUT=0x20006800
def run(f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x2000)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return int.from_bytes(u.mem_read(a,4),'little')
 def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
 def append(L,I,owner,value=0):
  s=L+8;p=word(s+8);w(I,value,s,p,owner,L);w(p+4,I);w(s+8,I);w(L,word(L)+1)
 for p in range(4):init(READY+20*p)
 for L in [DL,OL,EV]:init(L)
 w(T+44,f['priority']);w(T+104,f['initial']);u.mem_write(T+108,b'\0');append(READY+20*f['priority'],T+4,T)
 w(PEER+44,1);append(READY+20,PEER+4,PEER)
 w(0x20074a20,T);w(0x20074a24,DL);w(0x20074a28,OL);w(0x20074a30,2);w(0x20074a34,f['tick']);w(0x20074a38,max(1,f['priority']));w(0x20074a3c,1);w(0x20074a40,0);w(0x20074a44,0);w(0x20074a48,0);w(0x20074a50,0xffffffff);w(0x20074a58,0);w(OUT,0xeeeeeeee)
 sp=0x200ff000;w(sp,f['ticks']);args=[0,0,f['clear'],OUT]
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x10ff01);stops=[];pendsv=[];phase=[];resume_yield=[False]
 def hook(uc,pc,n,user):
  if pc==0x4420bc and not resume_yield[0]:stops.append(('yield',uc.reg_read(UC_ARM_REG_LR),uc.reg_read(UC_ARM_REG_SP)));uc.emu_stop();return
  if pc==0x10ff00:stops.append(('return',0,0));uc.emu_stop();return
  assert pc!=0x5fa0c8,'no delivered exception'
  if native:assert 0x100000<=pc<0x110000 or 0x4420bc<=pc<0x442124 or 0x455000<=pc<0x456200 or 0x5fa0a4<=pc<0x5fa0c8,hex(pc)
 def mem(uc,access,a,n,v,user):
  if a==0xe000ed04:pendsv.append([v,uc.reg_read(UC_ARM_REG_BASEPRI)])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_PC,(syms['audio_notify_wait'] if native else 0x455b84)|1)
 for _ in range(30000):
  if stops:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stops and stops[-1][0]=='yield';_,resume_lr,resume_sp=stops.pop();phase.append({'after_block':{'state_container':hex(word(T+20)),'event_container':hex(word(T+40)),'notification_state':u.mem_read(T+108,1)[0],'ready_count':word(READY+20*f['priority']),'delayed_count':word(DL),'next_unblock':hex(word(0x20074a50))}})
 if f['outcome']=='notify':
  tmp=0x200fe000;w(tmp,0,0);u.reg_write(UC_ARM_REG_SP,tmp);u.reg_write(UC_ARM_REG_LR,0x10fe01)
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[T,0,f['value'],f['action']]):u.reg_write(reg,v)
  u.reg_write(UC_ARM_REG_PC,(syms['uart_notify_isr'] if native else 0x455dc0)|1);u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0x10fe00,count=30000)
 else:
  w(0x20074a20,PEER);u.reg_write(UC_ARM_REG_SP,0x200fe000);u.reg_write(UC_ARM_REG_LR,0x10fe01);u.reg_write(UC_ARM_REG_PC,(syms['audio_tick_expiry_selected'] if native else 0x45504c)|1)
  for _ in range(f['ticks']):u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0x10fe00,count=30000);u.reg_write(UC_ARM_REG_PC,(syms['audio_tick_expiry_selected'] if native else 0x45504c)|1)
  w(0x20074a20,T)
 phase.append({'after_wake':{'state_container':hex(word(T+20)),'event_container':hex(word(T+40)),'notification_state':u.mem_read(T+108,1)[0],'notification':hex(word(T+104)),'ready_count':word(READY+20*f['priority']),'delayed_count':word(DL)}})
 resume_yield[0]=True;u.reg_write(UC_ARM_REG_SP,resume_sp);u.reg_write(UC_ARM_REG_LR,resume_lr);u.reg_write(UC_ARM_REG_PC,0x4420bd)
 for _ in range(30000):
  if stops:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stops and stops[-1][0]=='return'
 return {'return':u.reg_read(UC_ARM_REG_R0),'output':word(OUT),'notification':word(T+104),'notification_state':u.mem_read(T+108,1)[0],'state_container':hex(word(T+20)),'event_container':hex(word(T+40)),'ready_lists':bytes(u.mem_read(READY,80)).hex(),'delayed':bytes(u.mem_read(DL,20)).hex(),'tick':hex(word(0x20074a34)),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'critical_depth':word(0x2000309c),'pendsv_writes':pendsv,'phases':phase}
cases=[]
for outcome,tick,ticks,priority,initial,clear in itertools.product(['notify','timeout'],[0,100,0xfffffffe],[1,2],[0,1,2],[0,0x100],[0,0x800000]):
 for action,value in ([(0,0x800000),(1,0x800000),(2,0x800000),(3,0x800000)] if outcome=='notify' else [(0,0)]):cases.append(dict(outcome=outcome,tick=tick,ticks=ticks,priority=priority,initial=initial,clear=clear,action=action,value=value))
rows=[];diff=[]
for f in cases:
 a=run(f,False);b=run(f,True)
 if a!=b:diff.append({'fixture':f,'differences':{k:{'stock':a[k],'source':b[k]} for k in a if a[k]!=b[k]}})
 rows.append({'fixture':f,'observed':a,'matches':a==b})
(D/'results.json').write_text(json.dumps({'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'differences':diff,'limits':'Driver explicitly orders block then ISR notify or tick expiry then saved wait continuation. Yield request executes; no exception/context switch is delivered. Synthetic coherent tasks/lists.'},indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
