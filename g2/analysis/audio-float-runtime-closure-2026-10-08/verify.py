from pathlib import Path
import json,struct,itertools,random
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'floorf':0x43a5a0,'roundf':0x577d08,'ceilf':0x577d40,'fmodf':0x577c3c}
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def run(native,c):
 u=machine();w(u,0x20074f14,0xa5a55a5a);u.reg_write(UC_ARM_REG_FPSCR,c.get('fpscr',0));u.reg_write(UC_ARM_REG_S0,c['a']);u.reg_write(UC_ARM_REG_S1,c.get('b',0));writes=[]
 def wr(u,ac,a,n,v,d):writes.append([a,n,v])
 u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x20074f14,end=0x20074f17)
 u.emu_start((sym['audio_'+c['op']] if native else entries[c['op']])|1,0x2007f000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,c
 return dict(result=u.reg_read(UC_ARM_REG_S0),fpscr=u.reg_read(UC_ARM_REG_FPSCR),errno=word(u,0x20074f14),errno_writes=writes,sp=u.reg_read(UC_ARM_REG_SP))
rows=[]
def compare(c):
 o=run(False,c);n=run(True,c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
values=[0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,bits(.25),bits(-.25),bits(.5),bits(-.5),bits(.75),bits(-.75),bits(1),bits(-1),bits(1.5),bits(-1.5),bits(2),bits(-2),bits(12),bits(-12),bits(240),bits(-240),bits(16777216),bits(-16777216),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc01234,0xffc01234,0x7f801234,0xff801234]
profiles=[0,1<<22,2<<22,3<<22,1<<24,1<<25,(1<<24)|(1<<25),0xa000009f]
for op,a,profile in itertools.product(['floorf','roundf','ceilf'],values,profiles):compare(dict(op=op,a=a,fpscr=profile))
for a,b,profile in itertools.product(values,values,[0,1<<24,1<<25,0xa000009f]):compare(dict(op='fmodf',a=a,b=b,fpscr=profile))
# Every exponent, representative mantissas, both signs for integer-rounding cores.
for op,e,m,sign in itertools.product(['floorf','roundf','ceilf'],range(256),[0,1,0x3fffff,0x400000,0x7fffff],[0,1]):compare(dict(op=op,a=(sign<<31)|(e<<23)|m))
rng=random.Random(5733436)
for i in range(800):
 a=rng.getrandbits(32);b=rng.getrandbits(32)
 compare(dict(op='fmodf',a=a,b=b,fpscr=profiles[i%len(profiles)]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Exact binary32 outputs, full FPSCR, errno writes/value and restored SP compare.','Source uses integer bit reconstruction; no host libm, original code calls or return stubs in four native providers.','IEEE scalar binary32/ARM hard-float ABI only; runtime attribution/version and full exception/scheduler behavior remain open.']),separators=(',',':'))+'\n');print('PASS',len(rows),'math runtime comparisons')
