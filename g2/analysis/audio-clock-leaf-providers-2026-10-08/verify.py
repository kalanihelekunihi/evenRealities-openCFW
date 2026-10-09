from pathlib import Path
import itertools,json,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries=dict(ext_request=0x4c3cd4,ext_release=0x4c3d28,pll_power_enable=0x480058,pll_power_disable=0x48009e,pll_power_enabled=0x4800e4,hfrc_force=0x4d391e,hfrc_apply=0x4d3938,hfrc_disable=0x4d3944,hfrc2_force=0x4d3952,hfrc2_apply=0x4d3992,hfrc2_disable=0x4d39e4,hfrc2_ratio=0x4d38ea,hfrc_target=0x4d3914)
def run(native,op='ext_request',user=52,available=1,already=0,other=0,pattern=0,mask=0,major=0x22,value=1,ready=1,ref=1,div=2,ratio=0x20c49b,nonnull=1,reference=12000000,target=196608000,fpscr=0,expose=False):
 u=machine();u.mem_write(0x20073324,b'\0'*56);w(u,0x2007333c,other<<1 if (user&255)==0 else other);w(u,0x20073340,0);
 if already:w(u,0x2007333c+4*((user&255)>>5),word(u,0x2007333c+4*((user&255)>>5))|(1<<(user&31)))
 w(u,0x200001dc,12000000 if available else 0)
 for a in [0x4001003c,0x40010400,0x400201b0,0x400204d8,0x40004020,0x40004044,0x40004048,0x4000404c,0x40004050]:w(u,a,pattern)
 w(u,0x4002000c,major);w(u,0x40004030,(1<<24) if ready else 0);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_FPSCR,fpscr);w(u,0x20006000,0xa5a5a5a5);u.mem_write(0x20006100,struct.pack('<BBHI',ref&255,div&255,0,ratio));writes=[];delays=[];waits=[]
 def wr(u,ac,a,n,v,d):writes.append([a,n,v&((1<<(n*8))-1)])
 def code(u,a,n,d):
  if a==0x4807a0:delays.append(dict(value=u.reg_read(UC_ARM_REG_R0),primask=u.reg_read(UC_ARM_REG_PRIMASK)))
  if a==0x480826:waits.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x4021ffff);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x20073324,end=0x2007335b)
 if op.startswith('ext_'):args=[user]
 elif op=='pll_power_enabled':args=[0x20006000]
 elif op=='hfrc2_apply':args=[0x20006100 if nonnull else 0]
 elif op=='hfrc2_ratio':args=[reference,target,div,0x20006000]
 elif op=='hfrc_target':args=[reference,target,0x20006000]
 else:args=[value]
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.emu_start((sym['audio_'+op] if native else entries[op])|1,0x2007f000,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 if expose:return u
 return dict(status=u.reg_read(UC_ARM_REG_R0),writes=writes,delays=delays,waits=waits,table=bytes(u.mem_read(0x20073324,56)).hex(),out=word(u,0x20006000),registers={hex(a):word(u,a) for a in [0x4001003c,0x40010400,0x400201b0,0x400204d8,0x40004020,0x40004044,0x40004048,0x4000404c,0x40004050]},primask=u.reg_read(UC_ARM_REG_PRIMASK),fpscr=u.reg_read(UC_ARM_REG_FPSCR))
rows=[]
def compare(c):
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for op,user,available,already,other,pattern,mask in itertools.product(['ext_request','ext_release'],[0,52,56,256],[0,1],[0,1],[0,1],[0,0xffffffff],[0,1]):compare(dict(op=op,user=user,available=available,already=already,other=other,pattern=pattern,mask=mask))
for op,major,pattern,mask in itertools.product(['pll_power_enable','pll_power_disable','pll_power_enabled'],[0x21,0x22,0x23,0xff,0x122],[0,0xffffffff],[0,1]):compare(dict(op=op,major=major,pattern=pattern,mask=mask))
for op,value,pattern,ready in itertools.product(['hfrc_force','hfrc_apply','hfrc_disable','hfrc2_force','hfrc2_disable'],[0,1,2,255,256],[0,0xffffffff],[0,1]):compare(dict(op=op,value=value,pattern=pattern,ready=ready))
for ref,div,ratio,pattern in itertools.product([0,1,2,255],[0,1,2,255],[0,0xffffffff,0x12345678],[0,0xffffffff]):compare(dict(op='hfrc2_apply',ref=ref,div=div,ratio=ratio,pattern=pattern))
for pattern in [0,0xffffffff]:compare(dict(op='hfrc2_apply',nonnull=0,pattern=pattern))
for reference,target,div,fpscr in itertools.product([0,1,32768,12000000,24000000,32000000,0xffffffff],[0,1,196608000,250000000,0xffffffff],[0,1,2,3,31,32,255,256],[0,1<<22,1<<24]):compare(dict(op='hfrc2_ratio',reference=reference,target=target,div=div,fpscr=fpscr))
for reference,target in itertools.product([0,1,32768,12000000,0xffffffff],[0,1,48000000,0xffffffff]):compare(dict(op='hfrc_target',reference=reference,target=target))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Actual wait/delay/IRQ bodies, GPIO and bitmap functions reconstructed natively and compared to originals.','Ratio preserves fixed-point VFP conversion and compares FPSCR; malformed division modeled with DIV_0_TRP disabled. Enabled divide trap/exception behavior remains outside this profile.','No physical GPIO/reference, oscillator,power or IRQ readiness proof.']),separators=(',',':'))+'\n');print('PASS',len(rows),'clock leaf comparisons')
