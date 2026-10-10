from unicorn import *
from unicorn.arm_const import *
from pathlib import Path
import json,hashlib,struct,sys,platform
from oracle import oracle,FIELDS
D=Path(__file__).parent;R=Path('/repo');b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
fixtures=json.loads((D/'fixtures.json').read_text());out=[]
for f in fixtures['fixtures']:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,b[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(0x40004000,0x1000)
 p=0x20070000;sp=0x200ff000;stop=0x400000;payload=struct.pack('<10I',*[f['time'][k] for k in FIELDS]);guard=b'\xa7'*16;u.mem_write(p-16,guard+payload+guard);u.mem_write(sp-128,b'\xd3'*128);u.mem_write(sp,b'\xe5'*16)
 for a,v in [(0x40004800,f['control']),(0x40004820,0xdeadbeef),(0x40004824,0xcafebabe)]:u.mem_write(a,struct.pack('<I',v))
 u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,stop|1);u.reg_write(UC_ARM_REG_R0,p);writes=[];ram=[];helpers={0x4d3a58:0,0x4d3a38:0}
 def code(u,a,n,d):
  if a==stop:u.emu_stop()
  if a in helpers:helpers[a]+=1
 def write(u,access,a,n,v,d):
  pc=u.reg_read(UC_ARM_REG_PC)
  if 0x40004000<=a<0x40005000:
   assert n==4 and a in [0x40004800,0x40004820,0x40004824];writes.append([a,v]);assert pc in [0x4d3af8,0x4d3b40,0x4d3b8c,0x4d3b94];ram.append({'pc':hex(pc),'address':hex(a),'size':n,'value':v})
  else:assert sp-128<=a and a+n<=sp;ram.append({'pc':hex(pc),'address':hex(a),'size':n,'value':v})
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x4d3add,0,count=3000)
 actual={'status':u.reg_read(UC_ARM_REG_R0),'writes':writes};expected=oracle(f['time'],f['control']);assert expected==f['expected'];assert actual==expected,(f['name'],actual,expected);assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==sp
 assert bytes(u.mem_read(p-16,72))==guard+payload+guard;assert bytes(u.mem_read(sp,16))==b'\xe5'*16
 assert helpers[0x4d3a58]==1 and helpers[0x4d3a38]==(7 if actual['status']==0 else 0)
 if not writes:assert [int.from_bytes(u.mem_read(a,4),'little') for a in [0x40004800,0x40004820,0x40004824]]==[f['control'],0xdeadbeef,0xcafebabe]
 out.append(dict(name=f['name'],time=f['time'],control=f['control'],actual=actual,expected=expected,helper_entries={hex(k):v for k,v in helpers.items()},memory_writes=ram,input_and_guards_retained=True,pass_=True))
(D/'results.json').write_text(json.dumps({'count':len(out),'all_pass':True,'fixtures':out},indent=2)+'\n')
libs=list(Path('/tmp/lz4env').rglob('libunicorn.so.2'));(D/'backend.json').write_text(json.dumps({'platform':platform.platform(),'python':sys.version,'unicorn_version':__import__('unicorn').__version__,'libraries':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in libs}},indent=2)+'\n');print('22 original-byte RTC fixtures PASS')
