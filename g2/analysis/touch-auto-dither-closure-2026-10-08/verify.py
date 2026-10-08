from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
D=Path(__file__).resolve().parent;s=D.parent/'touch-all-slot-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for typ,csd,csx')[0],ns);g=ns['ns'];rows=[]
for kind in ['direct','mode7','prepared']:
 for lock,freq,busy,invalid,old in itertools.product([0,2,255],[0,3,6,7],[0,1],[False,True],[0,3,7] if kind=='mode7' else [0]):
  vals=[]
  for native in [False,True]:
   u=ns['fixture']();u.mem_map(0x40000000,0x10000);u.mem_map(0x0fff0000,0x10000);u.mem_write(0x0fff0000,bytes(range(256))*256);u.mem_write(0x20003000+8,struct.pack('<I',0x20003100));u.mem_write(0x20003100,struct.pack('<II',0x40000000,0x20003700));u.mem_write(0x20003700,bytes([lock]));u.mem_write(0x20002000+36,struct.pack('<I',0x20007800));u.mem_write(0x20002000+28,struct.pack('<I',0x20003400));u.mem_write(0x20007800,b'\xa5'*256);u.mem_write(0x20007800+68,struct.pack('<I',freq));u.mem_write(0x20003500+85,bytes([old]));u.mem_write(0x20003500+115,b'\x01');u.mem_write(0x20000870,b'\x01');u.mem_write(0x40000180,struct.pack('<I',busy))
   if invalid:u.mem_write(0x20004000+144+122,b'\x02')
   bus=[]
   def read(u,access,a,n,v,data):
    if 0x40000000<=a<0x40010000 or 0x0fff0000<=a<0x10000000:bus.append(['read',a,n])
   def write(u,access,a,n,v,data):
    if 0x40000000<=a<0x40010000:bus.append(['write',a,n,v])
   u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
   if kind=='prepared':
    if native:r=g['call'](u,g['symbols']['touch_prepare_auto_dither'],[0x20002000])
    else:g['call'](u,0x5378,[0x20002000]);r=g['call'](u,0x68ec,[0x20002000])
   elif kind=='mode7':r=g['call'](u,g['symbols']['touch_switch_dither_dependency'] if native else 0x6ac0,[7,0x20002000])
   else:r=g['call'](u,g['symbols']['touch_configure_auto_dither'] if native else 0x68ec,[0x20002000])
   vals.append((r,bus,u.mem_read(0x20003500,128).hex(),u.mem_read(0x20007400,140).hex(),u.mem_read(0x20007500,176).hex(),u.mem_read(0x20007800,256).hex(),u.mem_read(0x40000000,0x1000).hex(),u.mem_read(0x20003700,16).hex()))
  assert vals[0]==vals[1],(kind,lock,freq,busy,invalid,old,vals)
  rows.append({'kind':kind,'lock':lock,'imo_field':freq,'mrss_initial':busy,'invalid_sensor_method':invalid,'old_mode':old,'return':vals[0][0],'final_mode':bytes.fromhex(vals[0][2])[85],'mrss_reads':sum(x[0]=='read' and x[1]==0x40000180 for x in vals[0][1]),'mmio_writes':sum(x[0]=='write' for x in vals[0][1])})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['No function-entry stubs; original complete functions vs independent reconstruction plus pinned public PDL.','Synthetic SFLASH/MMIO and static MRSS status, including exhausted315-iteration wait; no hardware concurrency/timing proof.','Prepared composition calls original5378 then68ec; it does not assert every stock caller uses this sequence.','Public Configure behavior only;24 bytes differ from stock loop layout.']},indent=2)+'\n');print('PASS',len(rows))
