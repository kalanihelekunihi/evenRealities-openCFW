from pathlib import Path
import itertools,json,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries=dict(hfrc2=0x4c399e,syspll=0x4c3b44,dispatch=0x4c446c)
meaningful={0x4d38ea:('ratio',3),0x539794:('pll_generate',0),0x4c3d9e:('xtal_request',1),0x4c3e9a:('xtal_release',1),0x4c3cd4:('ext_request',1),0x4c3d28:('ext_release',1),0x4d3992:('hf2_apply',0),0x4d39e4:('hf2_disable',0)}
for n,a in [('audio_xtal_request',0x4c3d9e),('audio_xtal_release',0x4c3e9a)]:meaningful[sym[n]&~1]=meaningful[a]
def run(native,family='hfrc2',hz=196608000,current=0,active=0,hs=0,ext=12000000,explicit=0,ref=1,bad=0,mask=0,clock=5,expose=False):
 u=machine();u.mem_write(0x20073324,b'\0'*56);w(u,0x2007334c,active if family=='hfrc2' or clock==5 else 0);w(u,0x20073354,active if family=='syspll' or clock==6 else 0);u.mem_write(0x200001cc,struct.pack('<5I',0,hs,0,32768,ext));w(u,0x20074254,current);w(u,0x20074258,current);u.mem_write(0x20004536,b'\0\0');u.mem_write(0x20074f55,b'\0'*7);w(u,0x20074260,0);w(u,0x20074264,0);w(u,0x20074268,0);w(u,0x20073f3c,ref);w(u,0x2007425c,0);w(u,0x200740f4,0);w(u,0x200740f8,0);w(u,0x40004030,1<<24);w(u,0x40020060,0xf0000);w(u,0x400204d8,0);w(u,0x400204e4,1);w(u,0x4002012c,0);w(u,0x40008858,0x5af00000);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 cfg=struct.pack('<BBHII',ref,2,0,0xc49ba,0) if family=='hfrc2' or (family=='dispatch' and (clock&255)==5) else struct.pack('<6BHI',ref,0,0,64 if bad else 4,2,1,48,0);u.mem_write(0x20006000,cfg);writes=[];calls=[]
 def code(u,a,n,d):
  if a in meaningful:
   name,num=meaningful[a];calls.append(dict(name=name,args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2][:num]]))
 def wr(u,ac,a,n,v,d):writes.append([a,n,v&((1<<(8*n))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x4021ffff)
 cfgptr=0x20006000 if explicit else 0
 args=[clock,hz,cfgptr] if family=='dispatch' else [hz,cfgptr]
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 name={'hfrc2':'audio_hfrc2_config','syspll':'audio_syspll_config','dispatch':'audio_clock_config'}[family];u.emu_start((sym[name] if native else entries[family])|1,0x2007f000,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',family,hz,hex(u.reg_read(UC_ARM_REG_PC)))
 if expose:return u
 return dict(status=u.reg_read(UC_ARM_REG_R0),writes=writes,calls=calls,config=bytes(u.mem_read(0x20073f30,36)).hex(),frequency=[word(u,a) for a in [0x20074250,0x20074254,0x20074258]],valid=[bytes(u.mem_read(a,1)).hex() for a in [0x20004536,0x20004537,0x20074f55]],table=bytes(u.mem_read(0x20073324,56)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
def compare(c):
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for hz,current,active,hs,ext,explicit,ref,mask in itertools.product([0,196608000,250000000,123],[0,196608000,250000000],[0,1],[0,24000000],[0,12000000],[0,1],[0,1],[0,1]):compare(dict(hz=hz,current=current,active=active,hs=hs,ext=ext,explicit=explicit,ref=ref,mask=mask))
for hz,active,hs,ext,explicit,ref,bad in itertools.product([0,48000000,96000000,1,0xffffffff],[0,1],[0,24000000],[0,12000000],[0,1],[0,1],[0,1]):compare(dict(family='syspll',hz=hz,active=active,hs=hs,ext=ext,explicit=explicit,ref=ref,bad=bad))
for family,ref,hs,ext in itertools.product(['hfrc2','syspll'],[2,255],[0,24000000],[0,12000000]):compare(dict(family=family,ref=ref,hs=hs,ext=ext,explicit=1))
for clock,hz,explicit in itertools.product([0,3,4,5,6,7,255,260,261,262],[0,48000000],[0,1]):compare(dict(family='dispatch',clock=clock,hz=hz,explicit=explicit))
(D/'config-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Actual floating ratio/PLL generation providers; native helpers do not substitute calculated generator outputs.','Nonzero HS fixture explicitly synthetic; stock defaults use HS0,LS32768,external12MHz.','Explicit config-cache validity does not imply driver parameter validation, physical reference or lock readiness.','Synchronous/no-IRQ state; source-generation metadata and valid bits are distinct from hardware state.']),separators=(',',':'))+'\n');print('PASS',len(rows),'configuration/dispatch comparisons')
