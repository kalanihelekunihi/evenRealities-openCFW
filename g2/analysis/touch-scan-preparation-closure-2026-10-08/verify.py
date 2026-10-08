from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-all-slot-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for typ,csd,csx')[0],ns);g=ns['ns'];rows=[]
def fixture(lock,old,clockbad,request,completion,fifo,candidate):
 u=ns['fixture']();u.mem_map(0x40000000,0x10000);u.mem_map(0x40020000,0x1000);u.mem_map(0x40040000,0x1000);u.mem_map(0x0fff0000,0x10000);u.mem_write(0x0fff0000,bytes(range(256))*256);u.mem_write(0x20003000,struct.pack('<I',1000000));u.mem_write(0x20003000+8,struct.pack('<I',0x20003100));u.mem_write(0x20003000+41,bytes([1,0,0]));u.mem_write(0x20003100,struct.pack('<II',0x40000000,0x20003700));u.mem_write(0x20003100+8,struct.pack('<IB3xIB3x',0x40040000,6,0x40040100,7));u.mem_write(0x20003700,bytes([lock]));u.mem_write(0x20002000+36,struct.pack('<I',0x20007800));u.mem_write(0x20002000+28,struct.pack('<I',0x20003400));u.mem_write(0x20007800,b'\xa5'*256);u.mem_write(0x20007800+68,struct.pack('<I',6));u.mem_write(0x20003500+85,bytes([old]));u.mem_write(0x20003500+115,b'\x01');u.mem_write(0x20003500+36,struct.pack('<I',100));u.mem_write(0x20003500+44,struct.pack('<I',16384));u.mem_write(0x20003500+81,b'\x02');u.mem_write(0x20000870,b'\x01');u.mem_write(0x40000180,struct.pack('<I',1));u.mem_write(0x40003200,struct.pack('<I',fifo))
 for j in range(3):
  u.mem_write(0x20004000+j*144+56,struct.pack('<H',1));u.mem_write(0x20004000+j*144+138,bytes([candidate]));u.mem_write(0x20005000+j*60+35,bytes([6|request]));u.mem_write(0x20005000+j*60+14,struct.pack('<H',7 if clockbad and j==1 else 16))
 bus=[]
 def read(u,access,a,n,v,data):
  if a==0x40000100:u.mem_write(a,struct.pack('<I',0x100 if completion else 0))
  if 0x40000000<=a<0x40041000 or 0x0fff0000<=a<0x10000000:bus.append(['read',a,n,u.reg_read(UC_ARM_REG_PRIMASK)])
 def write(u,access,a,n,v,data):
  if 0x40000000<=a<0x40041000:bus.append(['write',a,n,v,u.reg_read(UC_ARM_REG_PRIMASK)])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);return u,bus
regions=[(0x20003500,128),(0x20005000,180),(0x20007400,140),(0x20007500,176),(0x20007800,256),(0x20003700,16),(0x20003400,32),(0x40000000,0x1000),(0x40003000,0x1000),(0x40020000,0x1000),(0x40040000,0x1000)]
for kind in ['fields','dither','full']:
 for lock,old,bad,request,complete,candidate in itertools.product([0,2,255],[0,3],[False,True],[0,8],[False,True],[0,2]):
  vals=[]
  for native in [False,True]:
   u,bus=fixture(lock,old,bad,request,complete,1127,candidate)
   if kind=='fields' and not native:
    u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(0x71c9,0x7228,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x7228;r=u.reg_read(UC_ARM_REG_R6)
   else:
    name={'fields':'touch_prepare_scan_fields','dither':'touch_dither_scale','full':'touch_prepare_scan'}[kind];pc={'dither':0x7064,'full':0x71c8}.get(kind)
    r=g['call'](u,g['symbols'][name] if native else pc,[0x20002000])
   vals.append((r,bus,*[u.mem_read(a,n).hex() for a,n in regions],u.reg_read(UC_ARM_REG_PRIMASK)))
  assert vals[0]==vals[1],(kind,lock,old,bad,request,complete,candidate,[(x[0],len(x[1])) for x in vals],[(j,x,y) for j,(x,y) in enumerate(zip(vals[0],vals[1])) if x!=y]);rows.append({'kind':kind,'lock':lock,'old_mode':old,'invalid_clock_widget1':bad,'maximum_request':request,'completion':complete,'dither_candidate':candidate,'return':vals[0][0]})
for fifo,complete in itertools.product([0,32,33,55,56,111,112,337,338,563,564,1127,1128,65535],[False,True]):
 vals=[]
 for native in [False,True]:
  u,bus=fixture(2,0,False,0,complete,fifo,2);r=g['call'](u,g['symbols']['touch_dither_scale'] if native else 0x7064,[0x20002000]);vals.append((r,bus,*[u.mem_read(a,n).hex() for a,n in regions]));
 assert vals[0]==vals[1],(fifo,complete,vals);rows.append({'kind':'dither_threshold','fifo':fifo,'completion':complete,'return':vals[0][0],'scales':list(bytes.fromhex(vals[0][3])[j*60+51] for j in range(3))})
for stride,sensors,complete,fifo_seed in itertools.product([7,11],[0,1,2],[False,True],[0,65534]):
 vals=[]
 for native in [False,True]:
  u,bus=fixture(2,0,False,0,complete,fifo_seed,0);u.mem_write(0x20004000+56,struct.pack('<H',sensors));output=0x20009000;u.mem_write(output,struct.pack('<I',0xa5a5a5a5));u.reg_write(UC_ARM_REG_R3,output);u.mem_write(0x20008000,struct.pack('<I',0x20002000));reads=[0]
  def fifo_trace(u,access,a,n,v,data):
   if a==0x40003200:u.mem_write(a,struct.pack('<I',(fifo_seed+reads[0]*73)&65535));reads[0]+=1
  u.hook_add(UC_HOOK_MEM_READ,fifo_trace);r=g['call'](u,g['symbols']['touch_dither_measure'] if native else 0x69c4,[0x20007400 if stride==7 else 0x20007500+20,0x20004000,stride]);vals.append((r,bus,u.mem_read(output,4).hex(),reads[0],*[u.mem_read(a,n).hex() for a,n in regions]))
 assert vals[0]==vals[1],(stride,sensors,complete,fifo_seed,vals);rows.append({'kind':'measurement_loop','stride_words':stride,'sensors':sensors,'completion':complete,'fifo_seed':fifo_seed,'return':vals[0][0],'maximum':int.from_bytes(bytes.fromhex(vals[0][2]),'little'),'fifo_reads':vals[0][3]})
# An actual compiled synthetic callback executes on both sides. No call hook.
for bad,request,complete in itertools.product([False,True],[0,8],[False,True]):
 vals=[]
 for native in [False,True]:
  u,bus=fixture(2,0,bad,request,complete,1127,2);u.mem_write(0x20003500+20,struct.pack('<I',g['symbols']['touch_test_init_callback']));probe={'return_pc':None,'checked':False}
  def callback_trace(u,a,n,data):
   if a==(g['symbols']['touch_test_init_callback']&~1):probe['return_pc']=u.reg_read(UC_ARM_REG_LR)&~1
   elif a==probe['return_pc']:assert u.reg_read(UC_ARM_REG_R0)==0xdeadbeef;probe['checked']=True
  u.hook_add(UC_HOOK_CODE,callback_trace);r=g['call'](u,g['symbols']['touch_prepare_scan'] if native else 0x71c8,[0x20002000]);assert probe['checked'];vals.append((r,bus,*[u.mem_read(a,n).hex() for a,n in regions]))
 assert vals[0]==vals[1],(bad,request,complete,vals);assert vals[0][0]!=0xdeadbeef
 rows.append({'kind':'external_callback_probe','invalid_clock_widget1':bad,'maximum_request':request,'completion':complete,'return':vals[0][0],'callback_return_register_residue_ignored':True})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Full71c8 and7064 original instructions vs actual independent source composition plus public PDL, no function-entry stubs.','Fields tests are explicit original71c8..7228 slice; return compared with liveR6 status.','Null callback plus actual compiled synthetic ABI/order probe; no vendor callback-body or ISR-body claim.','Saturated-scan widgettypes2/6 and mode0; alternate type7 saturated ABI excluded.','Synthetic completion and FIFO values; no analog/timing/hardware safety claim.']},indent=2)+'\n');print('PASS',len(rows))
