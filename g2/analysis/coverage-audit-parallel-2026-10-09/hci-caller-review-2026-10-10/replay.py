from pathlib import Path
import struct,hashlib,json,sys,re
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import *
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;D=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/source-discovery-parallel-2026-10-09/hci-completion-caller-20261010');R=next(p for p in D.parents if (p/'g2/blobs').exists());raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
extents=[(0x56b182,0x56b37c,'0b7edb877bcded4d11d41e5aa49b94cd1ccc2b6d2537179d92813f101ed782a2'),(0x56a0d0,0x56a0ea,'a3df8ef860f53b928473fb1d4462eacb9356d224a5995eafb2a4795dd733fd9a'),(0x536234,0x536324,'da8ebedf91cd554eae5a19134ec01fd47b991e76d0e8666365b8e662dca7f89c'),(0x4bf9ec,0x4bfa00,'a0a7fa1b14bb01ca88fa84046451d92d37a5df0e01effffeb5c3cbe4c87a152d'),(0x538c4a,0x538c6e,'b89add9a6f39622dc9277b91669b4978b136cf95d4c09bff5a8f65d02c3a7080'),(0x439be4,0x439c8a,'8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd')]
for a,b,h in extents:assert sha(raw[a-0x437fe0:b-0x437fe0])==h
word=lambda a:struct.unpack_from('<I',raw,a-0x437fe0)[0]
H=word(0x56b7c8);L=word(0x56b7cc);T=word(0x56b7d0);SE=word(0x5363e8);Q=word(0x5363ec)
assert [H,SE,Q]==[0x20073870,0x20072cb8,0x20072cd8];assert raw[L+27-0x437fe0]==22 and word(T+27*4)==0x56a0d1
P=0x20080000;M=0x20081000;N=0x20082000;SP=0x200ff000;results=[]
source=(D.parent/'sec-encrypt-nullguard-20261010/sdk-hci_evt.c').read_text()
def body(name):
 match=re.search(r'(?:static\s+)?void\s+'+name+r'\([^;{}]*\)\s*\{',source);assert match;a=match.start();i=match.end()-1;depth=0
 while i<len(source):
  depth+=(source[i]=='{')-(source[i]=='}');i+=1
  if not depth:return source[a:i]
sourcehash={n:sha(body(n).encode()) for n in ['hciEvtProcessCmdCmpl','hciEvtParseLeEncryptCmdCmpl']}
# Independent selected-source projection, not a full native C/module comparator.
def projection(packet,alloc_ok):
 assert len(packet)==20 and packet[1:3]==b'\x17\x20'
 ev=[{'kind':'alloc','size':22}];msg=None
 if alloc_ok:
  msg=bytes([0,0,27,packet[3],packet[3]])+packet[4:20]+b'\xa5'
  ev.extend([{'kind':'parse','input_offset':3,'length':20},{'kind':'security-callback'},{'kind':'dequeue'},{'kind':'type-callback','type':0,'handler':36},{'kind':'free'}])
 ev.append({'kind':'command-credit','numPkts':packet[0]});return ev,msg
for alloc_ok in [True,False]:
 packet=bytes([1,0x17,0x20,0])+bytes(range(16));expected,expected_msg=projection(packet,alloc_ok)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000)
 u.mem_write(P,packet+b'\xcc'*12);u.mem_write(M,b'\xa5'*22+b'\xdd'*10);u.mem_write(N,struct.pack('<IB3x',0,36)+struct.pack('<HBB',1,11,7)+bytes(48)+b'\0'+bytes(3));u.mem_write(Q,struct.pack('<II',N,N));u.mem_write(H+8,struct.pack('<I',0x100201));u.mem_write(H+12,struct.pack('<I',0x536235));u.mem_write(SE+60,struct.pack('<I',0x100101))
 before_node=bytes(u.mem_read(N,64));before_packet=bytes(u.mem_read(P,32));events=[];trace=[];reads=[];writes=[];locks=[];saved={r:0x45670000+i for i,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9])}
 for r,v in saved.items():u.reg_write(r,v)
 for r,v in [(UC_ARM_REG_R0,P),(UC_ARM_REG_R1,20),(UC_ARM_REG_SP,SP),(UC_ARM_REG_LR,0x100001)]:u.reg_write(r,v)
 def code(uc,a,size,user):
  if a==0x100000:uc.emu_stop();return
  args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
  if a==0x56a0d0:assert args==[M,P+3,20];events.append({'kind':'parse','input_offset':3,'length':20})
  elif a==0x536234:assert args[0]==M;events.append({'kind':'security-callback'})
  elif a==0x4bf9ec:assert args[0]==Q;events.append({'kind':'dequeue'})
  if any(lo<=a<hi for lo,hi,h in extents):return
  if a==0x530446:assert args[0]==22;events.append({'kind':'alloc','size':22});uc.reg_write(UC_ARM_REG_R0,M if alloc_ok else 0)
  elif a==0x52b8a4:locks.append('enter');uc.reg_write(UC_ARM_REG_R0,0)
  elif a==0x52b8b6:locks.append('exit')
  elif a==0x100100:
   assert args==[N+8,M,36];events.append({'kind':'type-callback','type':0,'handler':36});trace.append({'callback_event':bytes(uc.mem_read(M,22)).hex(),'request_header':bytes(uc.mem_read(N+8,4)).hex()})
  elif a==0x5304d4:assert args[0]==M;events.append({'kind':'free'});trace.append({'freed_event':bytes(uc.mem_read(M,22)).hex()})
  elif a==0x52aef8:assert args[0]==1;events.append({'kind':'command-credit','numPkts':1})
  else:raise RuntimeError('unmodeled provider '+hex(a))
  uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def read(uc,access,a,size,value,user):
  reads.append({'address':hex(a),'size':size,'pc':hex(uc.reg_read(UC_ARM_REG_PC))})
  if P<=a<P+32:assert a+size<=P+20
 def write(uc,access,a,size,value,user):
  writes.append({'address':hex(a),'size':size,'value':value});assert M<=a and a+size<=M+22 or Q<=a and a+size<=Q+8 or SP-512<=a and a+size<=SP
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x56b183,0,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x100000 and u.reg_read(UC_ARM_REG_SP)==SP and all(u.reg_read(r)==v for r,v in saved.items());assert events==expected;assert bytes(u.mem_read(N,64))==before_node and bytes(u.mem_read(P,32))==before_packet
 assert bytes(u.mem_read(M+22,10))==b'\xdd'*10
 if alloc_ok:assert bytes(u.mem_read(M,22))==expected_msg and bytes(u.mem_read(Q,8))==bytes(8) and locks==['enter','exit']
 else:assert bytes(u.mem_read(M,22))==b'\xa5'*22 and bytes(u.mem_read(Q,8))==struct.pack('<II',N,N) and not locks
 results.append({'case':'normal-completion' if alloc_ok else 'temporary-allocation-failure','events':events,'source_projection_events':expected,'callback_and_release_trace':trace,'reads':reads,'writes':writes,'queue_after':bytes(u.mem_read(Q,8)).hex(),'input_packet_and_node_unchanged':True,'event_guard_unchanged':True,'ABI_preserved':True})
(O/'replay-results.json').write_text(json.dumps({'cases':results,'count':2,'stock_sha256':sha(raw),'executed_extents':[{'start':hex(a),'end':hex(b),'sha256':h} for a,b,h in extents],'source_function_sha256':sourcehash,'bindings':{'hciCb':hex(H),'secCb':hex(SE),'aesQueue':hex(Q),'lengthTable':hex(L),'parserTable':hex(T),'event27Size':22,'event27Parser':'0x56a0d1'},'projection_scope':'independent selected SDK source branch, fixed LE_ENCRYPT complete20byte parameters; not unchanged compiled full source'},indent=2)+'\n');print('PASS 2 original HCI caller/parser/security-handler cases against selected-source contract')
