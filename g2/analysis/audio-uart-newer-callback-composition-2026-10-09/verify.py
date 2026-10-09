from pathlib import Path
import json,subprocess,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
bind={'uart_peripheral_enable':0x47f5b8,'uart_peripheral_disable':0x47f7ae}
def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40020000,0x3000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 w(0x40021004,f.get('enabled',0));w(0x40021008,f.get('status',0));w(0x40021108,0x30);w(0x20074270,100);u.mem_write(0x20074f63,bytes([f.get('cache',0)]));u.mem_write(0x20074f71,bytes([0,f.get('pending',0),0,f.get('range',1)]));w(0x4002004c,0xabcdef00)
 cb=1
 family=f.get('family','pcm22');stockcb=0x5a490c if family=='pcm22' else 0x5a1738;nativecb=syms['audio_platform_newer_control' if family=='pcm22' else 'pcm21_control']
 w(0x40021108,f.get('buck',0x30));w(0x2005665c,f.get('signature',0x1f01600d))
 u.mem_write(0x20074f75,bytes([2,0,0,2,0]))
 if cb:
  w(0x20073274,(nativecb if native else stockcb)|1)
 u.reg_write(UC_ARM_REG_R0,f['domain']);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_PRIMASK,f.get('primask',0));stop=[];trace=[];delays=[];events=[];pcs=set()
 def mem(uc,access,a,size,value,user):
  if 0x40020000<=a<0x40023000:trace.append(['R' if access==UC_MEM_READ else 'W',hex(a),size,int.from_bytes(uc.mem_read(a,size),'little') if access==UC_MEM_READ else value,uc.reg_read(UC_ARM_REG_PRIMASK)])
 def hook(uc,pc,size,user):
  if pc==0x4807a0:
   delays.append(uc.reg_read(UC_ARM_REG_R0))
   if len(delays)==f.get('change_after',-1):w(0x40021008,f.get('changed_status',0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if pc in ([syms['pcm_postpone'],syms['pcm_pending_handle']] if native else [0x5a07e6,0x5a07f0]):events.append(['pre' if pc==(syms['pcm_postpone'] if native else 0x5a07e6) else 'post',uc.reg_read(UC_ARM_REG_PRIMASK)])
  if pc in (0x5a45d0,0x5a13e8):
   req=uc.reg_read(UC_ARM_REG_R0);events.append(['before-planner',bytes(uc.mem_read(req,19)).hex(),uc.reg_read(UC_ARM_REG_PRIMASK)]);stop.append('before-planner');uc.emu_stop();return
  if pc==(nativecb if native else stockcb):
   r2=uc.reg_read(UC_ARM_REG_R2);events.append(['group',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),int.from_bytes(uc.mem_read(r2,4),'little'),uc.reg_read(UC_ARM_REG_PRIMASK)])
  if native:
   # Actual group callback3/0..1 is a stock no-op in this PCM2.0 body.
   assert 0x100000<=pc<0x105000 or 0x5fa0a4<=pc<0x5fa0aa,hex(pc);pcs.add(pc)
 u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1)
 for _ in range(15000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop,(name,f,native,hex(u.reg_read(UC_ARM_REG_PC)))
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] else None,'mmio_trace':trace,'delays':delays,'callback_events':events,'primask':u.reg_read(UC_ARM_REG_PRIMASK),'pending_state':bytes(u.mem_read(0x20074f71,4)).hex()},pcs
if __name__=='__main__':
 cases=[]
 for name,family,domain,gate,mask,status in itertools.product(bind,['pcm21','pcm22'],[11,14],['inactive','bad-signature','planner'],[0,1],[0,0x1e00]):
  cases.append((name,dict(domain=domain,enabled=0 if name.endswith('enable') else 0x200<<(domain-11),status=status,family=family,buck=0 if gate=='inactive' else 0x30,signature=0 if gate=='bad-signature' else 0x1f01600d,primask=mask)))
 rows=[];pcs=set();diff=[]
 for name,f in cases:
  a,_=run(name,f,False);b,p=run(name,f,True)
  if a!=b:diff.append({'function':name,'fixture':f,'differences':{k:{'stock':a[k],'source':b[k]} for k in a if a[k]!=b[k]}})
  rows.append({'function':name,'fixture':f,'observed':a,'matches':a==b});pcs|=p
 (D/'results.json').write_text(json.dumps({'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bindings':{k:hex(v) for k,v in bind.items()},'comparisons':rows,'differences':diff,'reached_native_addresses':sorted(map(hex,pcs)),'limits':'UART11..14 only. Complete MMIO read/write traces, masks and pre/post native PCM2.0 bodies; stock no-op group3 callback retained executable dependency. Delay status supply synthetic; No physical power or delivered scheduling; planner paths stop before actual planner, callback gate paths complete.'},indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff));assert not diff,diff[:1]
