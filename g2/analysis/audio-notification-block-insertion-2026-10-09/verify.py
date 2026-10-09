from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3};sections=[]
with elf.open('rb') as f:
 for s in ELFFile(f).iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
CUR=0x20006000;PEER=0x20006100;DL=0x20006400;OL=0x20006500;SUSP=0x20073d4c;READY=0x2006a49c+20;OUT=0x20006800
bind={'audio_block_current':0x455fa8,'audio_notify_wait':0x455b84}
def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x2000)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return int.from_bytes(u.mem_read(a,4),'little')
 def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
 def append(L,item,owner,value):
  sentinel=L+8;prev=word(sentinel+8);w(item,value,sentinel,prev,owner,L);w(prev+4,item);w(sentinel+8,item);w(L,word(L)+1)
 for L in [READY,DL,OL,SUSP]:init(L)
 w(CUR+44,1);w(CUR+104,0xc00003);u.mem_write(CUR+108,bytes([f.get('state',0)]));append(READY,CUR+4,CUR,0xcccccccc)
 if f['peer']:w(PEER+44,1);append(READY,PEER+4,PEER,0)
 if f['index']:w(READY+4,CUR+4)
 if f['existing']:
  for i,offset in enumerate([1,3]):
   task=0x20006200+128*i;deadline=(f['tick']+offset)&0xffffffff;append(OL if deadline<f['tick'] else DL,task+4,task,deadline)
  append(SUSP,0x20006380+4,0x20006380,0x77777777)
 w(0x20074a20,CUR);w(0x20074a24,DL);w(0x20074a28,OL);w(0x20074a34,f['tick']);w(0x20074a38,1);w(0x20074a50,word(word(DL+12)) if word(DL) else 0xffffffff);w(OUT,0xeeeeeeee)
 sp=0x200ff000;args=[f['ticks'],f.get('indefinite',1)]
 if name=='audio_notify_wait':args=[0,0x400001,0x800000,OUT];w(sp,f['ticks'])
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_BASEPRI,0x30 if name=='audio_block_current' else 0);stop=[];write_masks=[];pendsv=[]
 def hook(uc,pc,n,user):
  if pc==0x4420bc:stop.append('before-yield');uc.emu_stop();return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  assert pc not in (0x4420f6,0x5fa0c8),'assertion/exception continuation excluded'
  if native:assert 0x100000<=pc<0x110000 or 0x4420d0<=pc<0x442124 or 0x5fa0a4<=pc<0x5fa0aa,hex(pc)
 def writes(uc,access,a,n,v,user):
  if CUR<=a<CUR+0x80 or READY<=a<READY+20 or DL<=a<OL+20 or SUSP<=a<SUSP+20 or a==OUT or a==0x20074a50:write_masks.append(uc.reg_read(UC_ARM_REG_BASEPRI))
  if a==0xe000ed04:pendsv.append(v)
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,writes);u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1)
 for _ in range(15000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop,(name,f,native,hex(u.reg_read(UC_ARM_REG_PC)));assert all(mask==0x30 for mask in write_masks) and not pendsv
 target=word(CUR+20)
 blocked=name=='audio_block_current' or (f['ticks'] and f['state']!=2)
 if blocked:
  expected=SUSP if f['ticks']==0xffffffff and f.get('indefinite',1) else OL if ((f['tick']+f['ticks'])&0xffffffff)<f['tick'] else DL
  assert target==expected and word(READY)==f['peer']
  if expected!=SUSP:assert word(CUR+4)==(f['tick']+f['ticks'])&0xffffffff
 else:assert target==READY and word(READY)==1+f['peer']
 if name=='audio_notify_wait':assert stop==(['before-yield'] if blocked else ['return'])
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if name=='audio_notify_wait' and stop==['return'] else None,'tasks_and_delayed':bytes(u.mem_read(CUR,0x520)).hex(),'ready_list':bytes(u.mem_read(READY,20)).hex(),'suspended_list':bytes(u.mem_read(SUSP,20)).hex(),'next_unblock':word(0x20074a50),'notification_output':word(OUT),'critical_depth':word(0x2000309c),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'pendsv_writes':pendsv,'state_container':hex(target),'state_item_value':hex(word(CUR+4))}
cases=[]
for tick,ticks,indefinite,peer,existing,index in itertools.product([0,100,0xfffffffe,0xffffffff],[0,1,2,5,0xffffffff],[0,1],[0,1],[0,1],[0,1]):cases.append(('audio_block_current',dict(tick=tick,ticks=ticks,indefinite=indefinite,peer=peer,existing=existing,index=index)))
for tick,ticks,state,peer,existing,index in itertools.product([0,100,0xfffffffe,0xffffffff],[0,1,2,0xffffffff],[0,1,2],[0,1],[0,1],[0,1]):cases.append(('audio_notify_wait',dict(tick=tick,ticks=ticks,state=state,peer=peer,existing=existing,index=index)))
rows=[];diff=[]
for name,f in cases:
 a=run(name,f,False);b=run(name,f,True)
 if a!=b:diff.append({'function':name,'fixture':f,'differences':{k:{'stock':a[k],'source':b[k]} for k in a if a[k]!=b[k]}})
 rows.append({'function':name,'fixture':f,'observed':a,'matches':a==b})
(D/'results.json').write_text(json.dumps({'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'differences':diff,'limits':'Coherent ready/current/delayed/suspended state, direct insertion and actual notify-wait prefix. Real critical helpers; positive wait stops before actual yield. No resumed caller, exception, timeout delivery or invalid-list assertions.'},indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
