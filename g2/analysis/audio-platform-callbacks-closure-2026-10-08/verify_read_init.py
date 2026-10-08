from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0])
def run(entry,kind,offset,count,null,cfg,power,initialize=False):
 u=machine();w(u,0x400201bc,cfg);w(u,0x40021008,power);u.mem_write(0x2005665c,b'\xa5'*108);u.mem_write(0x20006000,b'\xa5'*128);boundary=[];writes=[]
 def invalid(u,access,address,size,value,d):
  assert access==UC_MEM_FETCH_UNMAPPED and address==0x48,(access,hex(address),hex(u.reg_read(UC_ARM_REG_PC)))
  boundary.append(dict(address=hex(address),source=hex(u.reg_read(UC_ARM_REG_R0)),word_count=u.reg_read(UC_ARM_REG_R2),destination_delta=u.reg_read(UC_ARM_REG_R1)-0x2005665c if initialize else u.reg_read(UC_ARM_REG_R1)));return False
 def write(u,access,a,n,v,d):writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_MEM_INVALID,invalid);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40020000,end=0x40021fff)
 if not initialize:
  u.reg_write(UC_ARM_REG_R0,kind);u.reg_write(UC_ARM_REG_R1,offset);u.reg_write(UC_ARM_REG_R2,count);u.reg_write(UC_ARM_REG_R3,0 if null else 0x20006000)
 try:u.emu_start(entry|1,0x2007f000,count=100000)
 except UcError as error:assert error.errno==UC_ERR_FETCH_UNMAPPED and len(boundary)==1
 assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000;assert not writes
 assert bytes(u.mem_read(0x2005665c,108))==b'\xa5'*108 and bytes(u.mem_read(0x20006000,128))==b'\xa5'*128
 return dict(return_value=None if boundary else u.reg_read(UC_ARM_REG_R0),boundary=boundary)
rows=[]
for kind,offset,count,null,cfg,power in itertools.product([0,1,2,3,4,5,6,257],[0,0x25c,0x270,0x278,0x600,0xffffffff],[0,1,20],[0,1],[0,8,16,24],[0,1<<27]):
 args=(kind,offset,count,null,cfg,power);o=run(0x4d3dda,*args);n=run(sym['audio_platform_read_words'],*args);assert o==n,(args,o,n)
 k=kind&255;limit=({0:0x40 if cfg&16 else 0x200,1:0x2c0 if cfg&8 else 0x600,2:0x40,3:0x2c0,4:0x200,5:0x600}).get(k)
 if null or limit is None:assert o['return_value']==6
 elif ((offset+count)&0xffffffff)>limit:assert o['return_value']==5
 elif ((k==0 and cfg&16) or (k==1 and cfg&8) or k in [2,3]) and not power:assert o['return_value']==9
 else:
  base=0x42004000 if k==2 or (k==0 and cfg&16) else 0x42006000 if k==3 or (k==1 and cfg&8) else 0x42000000 if k in [0,4] else 0x42002000;off=offset+0x280 if k==1 and not(cfg&8) and offset>=0x200 else offset;assert o['boundary']==[dict(address='0x48',source=hex((base+off*4)&0xffffffff),word_count=count,destination_delta=0x20006000)]
 rows.append(dict(kind=kind,offset=hex(offset),count=count,null_destination=null,config=hex(cfg),power=hex(power),**o))
restricted=[]
for kind,null,cfg,power in itertools.product([0,1,2,3,4,5,6,257],[0,1],[0,8],[0,1<<27]):
 args=(kind,0x25c,20,null,cfg,power);o=run(0x4d3f3c,*args);n=run(sym['audio_platform_read_words_restricted'],*args);assert o==n;(restricted.append(dict(kind=kind,null_destination=null,config=hex(cfg),power=hex(power),**o)))
initialize=[]
for cfg,power in itertools.product([0,8,16,24],[0,1<<27]):
 args=(0,0,0,0,cfg,power);o=run(0x5a4d48,*args,initialize=True);n=run(sym['audio_platform_newer_initialize'],*args,initialize=True);assert o==n,(cfg,power,o,n)
 if cfg&8 and not power:assert o['return_value']==7
 else:assert o['boundary']==[dict(address='0x48',source='0x42006970' if cfg&8 else '0x42003370',word_count=20,destination_delta=4)]
 initialize.append(dict(config=hex(cfg),power=hex(power),**o))
(D/'read-init-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows)+len(restricted)+len(initialize),read_comparisons=rows,restricted_comparisons=restricted,initialize_comparisons=initialize,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Selected first-party argument/error/bounds logic agrees; successful reads stop at uninitialized ITCM0x48 in this negative fixture with unmapped instruction fetch.','No helper return, copied source-memory result, initialized signature or completed initialization fabricated.','Power/config words synthetic; real fuse/OTP contents and ITCM runtime initialization deliberately omitted.','Initialization post-read stores and finish-init child are static reconstruction only.']),indent=2)+'\n');print('PASS',len(rows)+len(restricted)+len(initialize),'read/init return or ITCM-entry-boundary comparisons')
