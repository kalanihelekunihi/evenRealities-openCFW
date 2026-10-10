from pathlib import Path
import json,struct,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path('/repo/g2/analysis/flashdb-provider-execution-20261010-implementation');raw=Path('/repo/g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
with (D/'candidate-O1.elf').open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS'];syms={s.name:s['st_value']&~1 for s in e.get_section_by_name('.symtab').iter_symbols()}
DB=0x20010000;KEY=0x20020000;BUF=0x20030000;OUT=0x20040000;HDR=0x20050000;SP=0x200ff000;STOP=0x800000;LOCK=STOP+0x100;UNLOCK=STOP+0x200
regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def run(kind,c,source=False,normalize=True):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x100000);u.mem_map(STOP,0x1000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_write(KEY,b'key\0');u.mem_write(BUF,b'\xcd'*64);u.mem_write(HDR,b'\xae'*24);u.mem_write(OUT,struct.pack('<5I',BUF if c.get('buf',True) else 0,c.get('requested',0),0xaaaa,0xbbbb,0xcccc));u.mem_write(DB+24,bytes([c.get('init',1)]));u.mem_write(DB+28,struct.pack('<II',LOCK|1 if c.get('lock') else 0,UNLOCK|1 if c.get('unlock') else 0))
 if kind=='get':args=[DB,KEY,BUF if c['buf'] else 0,c['requested']];u.mem_write(SP,struct.pack('<I',OUT if c['out'] else 0));entry=syms['test_get'] if source else 0x5444f4
 elif kind=='blob':args=[DB,KEY,OUT,0];entry=syms['fdb_kv_get_blob'] if source else 0x54454a
 else:args=[DB,0x123400,HDR,0];entry=syms['test_write'] if source else 0x5445b2
 for r,v in zip(regs,args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);trace=[];diag=False
 dep={syms['find_kv'] if source else 0x54449a:'find',syms['_fdb_flash_read'] if source else 0x585a12:'read',syms['_fdb_write_status'] if source else 0x5858d8:'status',syms['_fdb_flash_write'] if source else 0x585a52:'write',LOCK:'lock',UNLOCK:'unlock',syms['diagnostic'] if source else 0x4733ee:'diagnostic'}
 def hook(u,a,n,d):
  nonlocal diag
  if a==STOP:u.emu_stop();return
  if a not in dep:
   if source and 0x100000<=a<syms['find_kv']:return
   if not source and 0x5444f4<=a<0x5445f2:return
   raise RuntimeError(('unexpected',hex(a)))
  name=dep[a];v=[u.reg_read(r) for r in regs];sp=u.reg_read(UC_ARM_REG_SP)
  if name=='diagnostic':trace.append({'kind':name});diag=True;u.emu_stop();return
  if name=='find':assert v[:2]==[DB,KEY];trace.append({'kind':'find','db':v[0],'key':v[1]});u.mem_write(v[2],b'\xa7'*88);u.mem_write(v[2]+12,struct.pack('<I',c['recorded']));u.mem_write(v[2]+84,struct.pack('<I',0xabc400));ret=int(c['found'])
  elif name=='read':trace.append({'kind':name,'args':v});ret=c.get('read_error',0)
  elif name in ['status','write']:
   extras=list(struct.unpack('<'+('II' if name=='status' else 'I'),u.mem_read(sp,8 if name=='status' else 4)));trace.append({'kind':name,'args':v+extras});ret=c['status'] if name=='status' else c['write'];ret=ret&255 if source and normalize else ret
  else:assert v[0]==DB;trace.append({'kind':name,'db':v[0]});ret=0
  u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def write(u,acc,a,n,val,d):assert SP-256<=a and a+n<=SP+4 or OUT<=a and a+n<=OUT+20,('unexpected guest write',hex(a),n)
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(entry|1,0,count=1000)
 assert diag or u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
 assert bytes(u.mem_read(BUF,64))==b'\xcd'*64 and bytes(u.mem_read(HDR,24))==b'\xae'*24
 return {'return':None if diag else u.reg_read(UC_ARM_REG_R0),'trace':trace,'out':bytes(u.mem_read(OUT,20)).hex(),'diagnostic_stop':diag}
results=[]
getcases=[dict(found=f,requested=n,recorded=v,buf=b,out=o,read_error=err) for f,n,v,b,o,err in [(True,3,8,True,True,0),(True,8,8,True,True,0),(True,12,8,True,True,6),(True,0,8,True,True,0),(True,8,0,True,True,0),(False,8,8,True,True,0),(False,8,8,False,False,0),(True,8,8,False,True,0),(True,8,8,True,False,6),(True,0xffffffff,0xfffffffe,False,True,6)]]
for kind,cases in [('get',getcases),('blob',[dict(c,lock=l,unlock=ul) for c,l,ul in [(getcases[0],True,True),(getcases[2],True,False),(getcases[5],False,True),(getcases[7],False,False)]]),('write',[{'status':s,'write':w} for s,w in [(0,0),(0,2),(0,6),(1,0),(6,0),(0x100,2),(0x101,0),(0,0x100),(0,0x101)]])]:
 for c in cases:
  a=run(kind,c);b=run(kind,c,True);assert a==b,(kind,c,a,b)
  if kind in ['get','blob']:
   expected=min(c['requested'],c['recorded']) if c['found'] else 0;assert a['return']==expected;assert [t['kind'] for t in a['trace']].count('read')==int(c['found'] and c['buf'])
  else:assert a['return']==((c['status'] if c['status']&255 else c['write'])&255);assert [t['kind'] for t in a['trace']].count('write')==int(not(c['status']&255))
  results.append({'kind':kind,'input':c,'stock':a,'source':b,'equal':True,'boundary':'source short-enum providers normalized to uint8; raw stock ABI probed' if kind=='write' else 'mocked find/read/lock providers'})
diag=run('blob',dict(getcases[0],init=0));assert diag['diagnostic_stop'] and diag['trace']==[{'kind':'diagnostic'}]
rawviolations=[]
for c in [{'status':0x100,'write':2},{'status':0x101,'write':0},{'status':0,'write':0x101}]:rawviolations.append({'input':c,'stock':run('write',c),'source_raw_abi_violation':run('write',c,True,False)})
Path('/tmp/flashdb-audit-results.json').write_text(json.dumps({'comparisons':len(results),'all_equal':True,'cases':results,'uninitialized_stock':diag,'raw_source_provider_abi_violations':rawviolations,'scope':'no actual flash providers or hardware I/O; uninitialized stock stops at first logging call'},indent=2)+'\n');print(f'{len(results)} bounded stock/source comparisons PASS; uninitialized diagnostic stop; raw enum ABI differences retained')
