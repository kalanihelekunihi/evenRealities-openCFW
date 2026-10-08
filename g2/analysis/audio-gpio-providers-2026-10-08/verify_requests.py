from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'reference_update':0x44b0b6,'requests_update':0x44b0d6,'reset':0x44b158,'active_reset':0x44b158}
def run(native,kind,index=0,sources=0,initial=0,table=0,mask=0,steps=None):
 u=machine();w(u,0x40008858,initial);w(u,0x4000885c,2);u.mem_write(0x200740ec,bytes([table])*256);u.reg_write(UC_ARM_REG_PRIMASK,mask);writes=[];calls=[]
 def code(u,a,n,d):
  if native:a={sym['audio_gpio_pin_get']&~1:0x480eee,sym['audio_gpio_pin_set']&~1:0x480f0c}.get(a,a)
  if a in [0x47f5b8,0x47f7ae,0x480eee,0x480f0c,0x480826,0x4807a0]:calls.append(hex(a))
 def write(u,ac,a,n,v,d):
  writes.append([a,n,v&((1<<(8*n))-1)])
  if a==0x40021004:w(u,0x40021008,v)
  if a==0x4002100c:w(u,0x40021010,(v&~0xc0)|(0xc0 if v&0xc0 else 0))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x4021ffff);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x200740ec,end=0x200741eb)
 for operation,args in steps or [(kind,[index,sources] if kind=='requests_update' else [sources])]:
  u.reg_write(UC_ARM_REG_LR,0x2007f001)
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(r,v)
  if operation=='active_reset':w(u,0x4000885c,0);w(u,0x40004030,0x1000000);u.reg_write(UC_ARM_REG_R5,0)
  address=(sym['clock_reset_recover'] if operation=='active_reset' else sym['clock_reset_gated_path'] if operation=='reset' else sym['audio_clock_'+operation]) if native else entries[operation]
  u.emu_start(address|1,0x2007f000,count=5000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(retained=word(u,0x40008858),table=bytes(u.mem_read(0x200740ec,256)).hex(),writes=writes,calls=calls,primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for index,sources,initial,table,mask in itertools.product([0,1,2,3,4,5,6,255,256,257],[0,1,2,4,8,16,31,32,255,256,257],[0,0xffffffff],[0,1],[0,1]):
 case=dict(index=index,sources=sources,initial=initial,table=table,mask=mask);o=run(False,'requests_update',**case);n=run(True,'requests_update',**case);assert o==n,(case,o,n);rows.append(dict(function='requests_update',inputs=case,output=o))
for value,initial,mask in itertools.product([0,1,2,3,255,256,257],[0,0xffffffff],[0,1]):
 case=dict(sources=value,initial=initial,mask=mask);o=run(False,'reference_update',**case);n=run(True,'reference_update',**case);assert o==n,(case,o,n);rows.append(dict(function='reference_update',inputs=case,output=o))
for mask in [0,1]:
 steps=[('requests_update',[4,8]),('requests_update',[2,2]),('reset',[]),('requests_update',[2,0])]
 case=dict(initial=0x5af00000,mask=mask,steps=steps);o=run(False,'requests_update',**case);n=run(True,'requests_update',**case);assert o==n;assert o['retained']==0x5af00010;rows.append(dict(function='reset_republish_sequence',inputs=case,output=o))
for mask in [0,1]:
 steps=[('requests_update',[4,8]),('requests_update',[2,2]),('active_reset',[0]),('requests_update',[2,0])]
 case=dict(initial=0x5af00000,mask=mask,steps=steps);o=run(False,'requests_update',**case);n=run(True,'requests_update',**case);assert o==n,(case,o,n);assert o['retained']==0x5af00010;assert '0x47f5b8' in o['calls'];rows.append(dict(function='active_reset_republish_sequence',inputs=case,output=o))
(D/'request-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Synthetic per-slot clock arrays/retained state; invalid indices are deliberate malformed tests.','Gated and active reset sequences execute real original providers; active readiness write responses are synthetic, not physical clock recovery.']),separators=(',',':'))+'\n');print('PASS',len(rows),'clock request comparisons')
