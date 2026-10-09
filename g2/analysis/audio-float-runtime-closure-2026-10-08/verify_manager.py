from pathlib import Path
import itertools,json,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'hfrc_request':0x4c3f2a,'hfrc_release':0x4c4016,'hfrc2_request':0x4c4086,'hfrc2_release':0x4c420c,'syspll_request':0x4c427e,'syspll_release':0x4c43ec,'hfrc_wait':0x4c3ef4,'hfrc2_wait':0x4c4058}
meaningful={0x4d391e:('hfrc_force',1),0x4d3938:('hfrc_apply',1),0x4d3952:('hfrc2_force',1),0x4d3992:('hfrc2_apply',1),0x4d39e4:('hfrc2_disable',0),0x4c3d9e:('xtal_request',1),0x4c3e9a:('xtal_release',1),0x4c3cd4:('ext_request',1),0x4c3d28:('ext_release',1),0x5398e0:('pll_init',1),0x539a40:('pll_config',2),0x539994:('pll_enable',1),0x539944:('pll_deinit',1),0x539a10:('pll_disable',1),0x539b56:('pll_wait',1),0x480826:('wait5',4)}
for n,a in [('audio_xtal_request',0x4c3d9e),('audio_xtal_release',0x4c3e9a)]:meaningful[sym[n]&~1]=meaningful[a]
for n,a in [('audio_pll_init',0x5398e0),('audio_pll_configure',0x539a40),('audio_pll_enable',0x539994),('audio_pll_deinit',0x539944),('audio_pll_disable',0x539a10),('audio_pll_wait',0x539b56)]:meaningful[sym[n]&~1]=meaningful[a]
for n,a in [('audio_hfrc_force',0x4d391e),('audio_hfrc_apply',0x4d3938),('audio_hfrc2_force',0x4d3952),('audio_hfrc2_apply',0x4d3992),('audio_hfrc2_disable',0x4d39e4),('audio_ext_request',0x4c3cd4),('audio_ext_release',0x4c3d28)]:meaningful[sym[n]&~1]=meaningful[a]
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def norm(v):return 'local_stack' if 0x2007d800<=v<0x2007e000 else v
def run(native,kind='hfrc_request',valid=1,adjusted=0,ref=1,hs_hz=0,ext_hz=12000000,already=0,other=0,flag=0,stabilized=0,pending=0,mask=0,handle=0,ready=1,lock=1,counter=3,clear=1,cfg_bad=0,expose=False):
 u=machine();family=4 if kind.startswith('hfrc_') else 5 if kind.startswith('hfrc2_') else 6
 u.mem_write(0x20073324,b'\0'*56);w(u,0x20073324+family*8,other);w(u,0x20073328+family*8,(1<<20) if already else 0)
 u.mem_write(0x200001cc,struct.pack('<5I',0,hs_hz,0,32768,ext_hz));u.mem_write(0x20004536,bytes([valid,valid]));u.mem_write(0x20074f55,bytes([valid]));u.mem_write(0x20074f56,b'\0')
 u.mem_write(0x20074f57,bytes([flag,flag,stabilized,pending,pending]));w(u,0x20074250,48000000 if adjusted else 0);w(u,0x20074254,196608000 if adjusted else 0);w(u,0x20073f30,0x0025b800);u.mem_write(0x20073f3c,struct.pack('<BBHII',ref,0,0,0x12345678,0));u.mem_write(0x20073f48,struct.pack('<6BHI',ref,0,0,64 if cfg_bad else 4,2,1,48,0))
 w(u,0x20074264,0x20006100);w(u,0x20074268,0x20006104);w(u,0x20006100,counter);w(u,0x20006104,counter);w(u,0x200740f4,0 if handle==0 else 0x01504c30 if handle==1 else 0x03504c30);w(u,0x200740f8,0);w(u,0x2007425c,0 if handle==0 else 0x200740f4)
 w(u,0x40004030,(1<<24) if ready else 0);w(u,0x40020060,0xf0000 if ready else 0);w(u,0x400204e4,lock);w(u,0x400204d8,0);w(u,0x4002012c,0);w(u,0x4001003c,0);w(u,0x40008858,0x5af00000);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 writes=[];calls=[];delays=[];events=[]
 def code(u,a,n,d):
  if a in meaningful:
   name,num=meaningful[a];calls.append(dict(name=name,args=[norm(u.reg_read(r)) for r in REGS[:num]]))
  if a==0x4807a0:
   delays.append(u.reg_read(UC_ARM_REG_R0))
   if clear and len(delays)==clear:
    u.mem_write(0x20074f57,b'\0\0');events.append(['synthetic_stabilization_clear',clear])
 def wr(u,ac,a,n,v,d):writes.append([a,n,norm(v) if a in [0x20074260,0x20074264,0x20074268] else v&((1<<(n*8))-1)])
 def invalid(u,ac,a,n,v,d):raise AssertionError(('unmapped',native,kind,hex(u.reg_read(UC_ARM_REG_PC)),hex(a)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 for a,b in [(0x20073324,0x2007335b),(0x20074f55,0x20074f5b),(0x2007425c,0x2007426b),(0x40000000,0x4021ffff)]:u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=a,end=b)
 u.reg_write(UC_ARM_REG_R0,(0x20006100 if kind=='hfrc_wait' else 0x20006104) if kind.endswith('_wait') else 52)
 u.emu_start((sym['audio_'+kind] if native else entries[kind])|1,0x2007f000,count=12000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',kind,hex(u.reg_read(UC_ARM_REG_PC)))
 if expose:return u
 return dict(status=None if kind.endswith('_wait') else u.reg_read(UC_ARM_REG_R0),writes=writes,calls=calls,delays=delays,events=events,table=bytes(u.mem_read(0x20073324,56)).hex(),flags=bytes(u.mem_read(0x20074f55,7)).hex(),handle=word(u,0x2007425c),driver=bytes(u.mem_read(0x200740f4,8)).hex(),pointers=[norm(word(u,a)) for a in [0x20074260,0x20074264,0x20074268]],counters=[word(u,0x20006100),word(u,0x20006104)],primask=u.reg_read(UC_ARM_REG_PRIMASK),hfrc_force=word(u,0x40004044),hfadj=word(u,0x40004020),pll_control=word(u,0x400204d8))
rows=[]
def compare(c):
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for kind,valid,adjusted,already,other,flag,stabilized,mask in itertools.product(['hfrc_request','hfrc_release'],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]):compare(dict(kind=kind,valid=valid,adjusted=adjusted,already=already,other=other,flag=flag,stabilized=stabilized,mask=mask))
for kind,valid,adjusted,ref,already,other,flag,mask in itertools.product(['hfrc2_request','hfrc2_release'],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]):compare(dict(kind=kind,valid=valid,adjusted=adjusted,ref=ref,already=already,other=other,flag=flag,mask=mask))
for kind,valid,ref,already,other,mask in itertools.product(['syspll_request','syspll_release'],[0,1],[0,1],[0,1],[0,1],[0,1]):compare(dict(kind=kind,valid=valid,ref=ref,already=already,other=other,mask=mask))
for ref,hs_hz,ext_hz,handle,ready,lock,cfg_bad in itertools.product([0,1],[0,24000000],[0,12000000],[0,1,2],[0,1],[0,1],[0,1]):compare(dict(kind='syspll_request',ref=ref,hs_hz=hs_hz,ext_hz=ext_hz,handle=handle,ready=ready,lock=lock,cfg_bad=cfg_bad))
for kind,flag,counter,clear in itertools.product(['hfrc_wait','hfrc2_wait'],[0,1],[0,3,50,1000],[0,1,3]):compare(dict(kind=kind,flag=flag,counter=counter,clear=clear))
(D/'manager-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Stock default board HS=0,LS32768,external12MHz except explicitly synthetic HS24MHz/ref-unavailable fixtures.','Actual clock, GPIO, PLL driver and wait providers execute; no success/error return stubs.','Selected software stabilization clear at delay entry is synthetic; not asynchronous IRQ proof.','Passive/synthetic power,lock,status bits are not hardware readiness.','Local counter pointers normalized; source dependency helpers reused unchanged.']),separators=(',',':'))+'\n');print('PASS',len(rows),'HFRC/HFRC2/SYSPLL comparisons')
