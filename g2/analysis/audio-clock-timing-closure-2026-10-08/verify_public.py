from pathlib import Path
import json,itertools,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'lfrc_request':0x4c3bfc,'lfrc_release':0x4c3c2e,'xtal_ls_request':0x4c3c60,'xtal_ls_release':0x4c3ca2,'clock_request':0x4c44bc,'clock_release':0x4c4530}
child_entries={'lfrc_request':0x4c3bfc,'lfrc_release':0x4c3c2e,'xtal_ls_request':0x4c3c60,'xtal_ls_release':0x4c3ca2,'xtal_request':0x4c3d9e,'xtal_release':0x4c3e9a,'ext_request':0x4c3cd4,'ext_release':0x4c3d28,'hfrc_request':0x4c3f2a,'hfrc_release':0x4c4016,'hfrc2_request':0x4c4086,'hfrc2_release':0x4c420c,'syspll_request':0x4c427e,'syspll_release':0x4c43ec}
meaningful={a:name for name,a in child_entries.items()}
for n,a in child_entries.items():meaningful[sym['audio_'+n]&~1]=n
meaningful[0x4809c4]='oscillator_control';meaningful[sym['audio_oscillator_control']&~1]='oscillator_control'
def norm(v):return 'inactive_local_stack' if 0x2007d800<=v<0x2007e000 else v
def run(native,c):
 u=machine();
 if native:require_source_code(u)
 u.mem_write(0x20073324,b'\0'*56);op=c['op'];clock=c.get('clock',1 if op.startswith('xtal_ls') else 0)&255;user=c['user']&255
 if clock<7:
  w(u,0x20073324+clock*8,c.get('other',0));w(u,0x20073328+clock*8,0)
  if c.get('already') and user<57:
   a=0x20073324+clock*8+4*(user>>5);w(u,a,word(u,a)|(1<<(user&31)))
 u.mem_write(0x200001cc,struct.pack('<5I',0,c.get('hs',0),c.get('ls_mode',0),c.get('ls',32768),c.get('ext',12000000)))
 u.mem_write(0x20004536,b'\1\1');u.mem_write(0x20074f55,b'\1\0\0\0\0\0\0');w(u,0x20074250,0);w(u,0x20074254,0);w(u,0x20074258,48000000)
 w(u,0x20074260,0);w(u,0x20074264,0);w(u,0x20074268,0);w(u,0x2007425c,0);w(u,0x200740f4,0);w(u,0x200740f8,0)
 u.mem_write(0x20073f48,struct.pack('<6BHI',1,1,1,1,5,1,20,0));w(u,0x40004030,1<<24);w(u,0x40020060,0xf0000);w(u,0x400204e4,1);w(u,0x400204d8,0);w(u,0x4002012c,0);w(u,0x40020128,0xa5a5a5a5);w(u,0x4001003c,0xdeadbeef);u.reg_write(UC_ARM_REG_PRIMASK,c.get('mask',0));writes=[];calls=[];delays=[]
 def wr(u,ac,a,n,v,d):writes.append([a,n,norm(v) if a in [0x20074260,0x20074264,0x20074268] else v&((1<<(8*n))-1)])
 def code(u,a,n,d):
  if a in meaningful:
   name=meaningful[a];calls.append(dict(name=name,arg=u.reg_read(UC_ARM_REG_R0)))
  if a in [0x4807a0,sym['audio_delay_us']&~1]:delays.append(u.reg_read(UC_ARM_REG_R0))
 for a,b in [(0x20073324,0x2007335b),(0x2007425c,0x2007426b),(0x40000000,0x4021ffff)]:u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=a,end=b)
 u.hook_add(UC_HOOK_CODE,code)
 args=[c['clock'],c['user']] if op.startswith('clock_') else [c['user']]
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(r,v)
 u.emu_start((sym['audio_'+op] if native else entries[op])|1,0x2007f000,count=12000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,c
 return dict(status=u.reg_read(UC_ARM_REG_R0),calls=calls,writes=writes,delays=delays,table=bytes(u.mem_read(0x20073324,56)).hex(),flags=bytes(u.mem_read(0x20074f55,7)).hex(),pointers=[norm(word(u,a)) for a in [0x20074260,0x20074264,0x20074268]],handle=word(u,0x2007425c),driver=bytes(u.mem_read(0x200740f4,8)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK),fpscr=u.reg_read(UC_ARM_REG_FPSCR))
rows=[]
def compare(c):
 o=run(False,c);n=run(True,c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for op,user,already,other,ls,mode,mask in itertools.product(['lfrc_request','lfrc_release','xtal_ls_request','xtal_ls_release'],[0,52,56,256],[0,1],[0,2],[0,32768],[0,1,255],[0,1]):compare(dict(op=op,user=user,already=already,other=other,ls=ls,ls_mode=mode,mask=mask))
for op,clock,user,already,mask in itertools.product(['clock_request','clock_release'],[0,1,2,3,4,5,6,7,255,256,262,263],[0,52,56,57,255,256,312,0xffffffff],[0,1],[0,1]):compare(dict(op=op,clock=clock,user=user,already=already,mask=mask))
for op,ls,hs,ext,clock in itertools.product(['clock_request','clock_release'],[0,32768],[0,24000000],[0,12000000],[1,2,3]):compare(dict(op=op,clock=clock,user=52,ls=ls,hs=hs,ext=ext))
(D/'public-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Entire native public dispatcher invokes reconstructed clock children; prior oscillator provider now native, with native delay/math/IRQ providers; source-code guard rejects original/external execution.','Full bitmap and ordered writes/call arguments compare; local counter-pointer addresses normalized and are not proven live-lifetime safe.','Ready,lock,reference availability and software delay execution are offline synthetic inputs, not physical readiness or asynchronous timing.']),separators=(',',':'))+'\n');print('PASS',len(rows),'public/low-speed comparisons')
