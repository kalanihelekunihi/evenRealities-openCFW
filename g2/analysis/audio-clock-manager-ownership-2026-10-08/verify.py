from pathlib import Path
import itertools,json
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
addresses=dict(audio_clock_any=0x4c377a,audio_clock_user=0x4c37a8,audio_clock_count=0x4c37ca,audio_clock_set=0x4c37fe,audio_xtal_status=0x480c56,audio_xtal_release=0x4c3e9a)
def invoke(u,a,args):
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(a|1,0x2007f000,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;return u.reg_read(UC_ARM_REG_R0)
def run(native,name,c=2,user=52,yes=1,pattern=0,other=0,mask=0):
 u=machine();u.mem_write(0x20073324,b'\0'*2100);base=0x20073324+8*(c&255);w(u,base,pattern);w(u,base+4,pattern);u.reg_write(UC_ARM_REG_PRIMASK,mask);w(u,0x40020128,0x12345678);w(u,0x4002012c,pattern);u.mem_write(0x20074f56,b'\1');w(u,0x20074260,0x20006000)
 if name=='audio_xtal_release':
  w(u,0x20073334,other);w(u,0x20073338,pattern)
 writes=[]
 def wr(u,ac,a,n,v,d):writes.append([a,n,v&((1<<(n*8))-1)])
 u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x20073324,end=0x20073b60);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40020128,end=0x4002012f)
 if name=='audio_xtal_status':args=[0x20006000]
 elif name=='audio_xtal_release':args=[user]
 else:args=[c,user,yes]
 status=invoke(u,sym[name] if native else addresses[name],args)
 return dict(status=status,table=bytes(u.mem_read(0x20073324,2100)).hex(),writes=writes,output=bytes(u.mem_read(0x20006000,1)).hex(),stabilizing=bytes(u.mem_read(0x20074f56,1)).hex(),counter=word(u,0x20074260),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
def compare(name,case):
 o=run(False,name,**case);n=run(True,name,**case);assert o==n,(name,case,o,n);rows.append(dict(function=name,inputs=case,**o))
for name,c,pattern in itertools.product(['audio_clock_any','audio_clock_count'],[0,2,6,7,255,256],[0,1,0xaaaaaaaa,0xffffffff]):compare(name,dict(c=c,pattern=pattern))
for c,user,pattern in itertools.product([0,2,6,7,256],[0,31,32,52,56,57,255,256],[0,0xffffffff]):compare('audio_clock_user',dict(c=c,user=user,pattern=pattern))
for c,user,yes,pattern in itertools.product([0,2,6,7,256],[0,31,32,52,56,57,255,256],[0,1,255,256],[0,0xffffffff]):compare('audio_clock_set',dict(c=c,user=user,yes=yes,pattern=pattern))
for pattern in [0,1,128,256,257,0xffffffff]:compare('audio_xtal_status',dict(pattern=pattern))
for user,pattern,other,mask in itertools.product([0,31,32,52,56],[0,1<<20,0xffffffff],[0,1],[0,1]):compare('audio_xtal_release',dict(user=user,pattern=pattern,other=other,mask=mask))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Query helpers intentionally lack bounds validation and expose stock byte narrowing; synthetic SRAM only.','Release executes original oscillator/delay providers, not success stubs.','No physical crystal quiescence/readiness or concurrent ISR model.']),separators=(',',':'))+'\n');print('PASS',len(rows),'ownership comparisons')
