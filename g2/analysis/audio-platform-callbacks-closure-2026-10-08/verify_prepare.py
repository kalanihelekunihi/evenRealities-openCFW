from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0])
def run(entry,range_,mask0,mask1,peripheral,available,auxvalue,pin_index,pin_id,pin_enabled,pin_mask):
 u=machine();u.mem_map(0x40008000,0x1000);u.mem_write(0x20006000,struct.pack('<4I3B',mask0,mask1,0,0,range_,2,0));w(u,0x400204d8,peripheral);u.mem_write(0x20074f78,bytes([0xa5,0xa5,available,0xa5,0xa5]));w(u,0x40008800,auxvalue);w(u,0x40008010,pin_mask);w(u,0x40008200+32*pin_index,(pin_id<<8)|pin_enabled);u.reg_write(UC_ARM_REG_R0,0x20006000);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 active=range_==3 or mask0&0x3fffffff!=0 or mask1&0x4c4!=0 or peripheral&(1<<29)!=0 or (available and auxvalue&15 in [1,2] and not auxvalue&0xc0000000) or (pin_enabled and pin_mask&(1<<pin_index) and (pin_id<6 or 19<=pin_id<25 or 256<=pin_id<480))
 after=bytes(u.mem_read(0x20074f78,5));assert after==bytes([0xa5,0xa5,available,int(bool(active)),0xa5]);return after.hex()
rows=[]
cases=[]
for range_,masks,peripheral,available,aux in itertools.product([2,3],[(0,0),(1,0),(0xc0000000,0),(0,0x4c4)],[0,1<<29],[0,1],[0,1,2,3,0x40000001,0x80000001]):cases.append((range_,*masks,peripheral,available,aux,0,30,0,0))
for index,id_,enabled,selected in itertools.product([0,7,15],[0,5,6,18,19,24,25,255,256,479,480,511],[0,1],[0,1]):cases.append((2,0,0,0,0,0,index,id_,enabled,(1<<index) if selected else 0))
for case in cases:
 o=run(0x5a410c,*case);n=run(sym['audio_platform_prepare_state'],*case);assert o==n;rows.append(dict(inputs=list(case),flag_region=o))
query=[]
for available,value in itertools.product([0,1,255],[0,1,2,3,15,16,0x40000001,0x80000001,0xc0000001]):
 vals=[]
 for entry in [0x48d620,sym['audio_platform_auxiliary_active']]:
  u=machine();u.mem_map(0x40008000,0x1000);u.mem_write(0x20074f7a,bytes([available]));w(u,0x40008800,value);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;want=int(bool(available and value&15 and not value&0xc0000000));assert u.reg_read(UC_ARM_REG_R0)==want;vals.append(want)
 assert vals[0]==vals[1];query.append(dict(available=available,value=hex(value),result=vals[0]))
(D/'prepare-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows)+len(query),prepare_comparisons=rows,query_comparisons=query,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Complete selected integer providers; register/pin states synthetic and passive.','Flag0x20074F7B is a computed software prerequisite, not proof of physical quiescence.','Pin IDs are numeric selectors; individual pin-function names not recovered.']),indent=2)+'\n');print('PASS',len(rows),len(query),'prepare/query comparisons')
