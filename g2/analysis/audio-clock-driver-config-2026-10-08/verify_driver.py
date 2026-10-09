from pathlib import Path
import itertools,json,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
addresses=dict(init=0x5398e0,deinit=0x539944,enable=0x539994,disable=0x539a10,configure=0x539a40,wait=0x539b56)
names=dict(init='audio_pll_init',deinit='audio_pll_deinit',enable='audio_pll_enable',disable='audio_pll_disable',configure='audio_pll_configure',wait='audio_pll_wait')
def run(native,op='configure',header=0x01504c30,module=0,out=1,null=0,pattern=0,ready=0xf0000,lock=1,ref=1,vco=0,mode=0,refdiv=4,post1=2,post2=1,fbdiv=48,fraction=0):
 u=machine();w(u,0x200740f4,header);w(u,0x200740f8,0);w(u,0x20006000,0xa5a5a5a5);w(u,0x400204d8,pattern);w(u,0x400204dc,pattern);w(u,0x400204e0,(pattern&~63)|refdiv if op=='wait' else pattern);w(u,0x400204e4,lock);w(u,0x40020060,ready);w(u,0x40008858,0x5af00000);u.mem_write(0x20006100,struct.pack('<6BHI',ref,vco,mode,refdiv,post1,post2,fbdiv,fraction));u.reg_write(UC_ARM_REG_PRIMASK,1);writes=[];calls=[]
 def wr(u,ac,a,n,v,d):writes.append([a,n,v&((1<<(8*n))-1)])
 def code(u,a,n,d):
  if a in [0x480058,0x48009e,0x4800e4,0x480826]:
   calls.append(dict(name={0x480058:'power_enable',0x48009e:'power_disable',0x4800e4:'power_query',0x480826:'wait5'}[a],args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]] if a==0x480826 else []))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x4021ffff)
 if op=='init':args=[module,0x20006000 if out else 0]
 else:args=[0 if null else 0x200740f4,0x20006100]
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(r,v)
 u.emu_start((sym[names[op]] if native else addresses[op])|1,0x2007f000,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(status=u.reg_read(UC_ARM_REG_R0),writes=writes,calls=calls,state=bytes(u.mem_read(0x200740f4,8)).hex(),out=word(u,0x20006000),control=word(u,0x400204d8),div0=word(u,0x400204dc),div1=word(u,0x400204e0),retained=word(u,0x40008858),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
def compare(case):
 o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
for module,out,header,pattern in itertools.product([0,1,0xffffffff],[0,1],[0,0x80000000,0x01504c30],[0,0xffffffff]):compare(dict(op='init',module=module,out=out,header=header,pattern=pattern))
for op,header,null,ready,pattern in itertools.product(['enable','disable','deinit'],[0,0x00504c30,0x01504c30,0x03504c30,0xffffffff],[0,1],[0,0xf0000,0xe0000],[0,0xffffffff]):compare(dict(op=op,header=header,null=null,ready=ready,pattern=pattern))
for mode,fbdiv,refdiv,(post1,post2),pattern in itertools.product([0,1,2],[0,3,4,9,10,96,97,960,961],[0,1,63,64],[(0,0),(7,7),(7,8),(1,2),(2,1)],[0,0xffffffff]):compare(dict(mode=mode,fbdiv=fbdiv,refdiv=refdiv,post1=post1,post2=post2,pattern=pattern))
for ref,vco,mode,fraction in itertools.product([0,1,255],[0,1,255],[0,1],[0,0xffffffff]):compare(dict(ref=ref,vco=vco,mode=mode,fraction=fraction))
for header,null,vco,refdiv,lock in itertools.product([0,0x01504c30,0x03504c30],[0,1],[0,1],[0,1,63],[0,1]):compare(dict(op='wait',header=header,null=null,pattern=(1<<29)|(vco<<9),refdiv=refdiv,lock=lock))
# The wait reads register divider; add concrete enabled register cases separately.
for pattern in [0,1<<29,(1<<29)|512]:compare(dict(op='wait',pattern=pattern))
(D/'driver-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Actual power/wait providers, no returned-status stubs.','Driver configure assumes nonNULL config after handle validation; null dereference not modeled as a supported API.','Synthetic SIMOBUCK/control/lock state, not physical readiness.','Direct wait fixtures explicitly write divider bits to0/1/63 and cover real polling timeouts.']),separators=(',',':'))+'\n');print('PASS',len(rows),'SYSPLL driver comparisons')
