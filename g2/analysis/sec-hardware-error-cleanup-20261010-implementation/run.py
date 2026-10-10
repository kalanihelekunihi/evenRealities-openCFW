from pathlib import Path
import json,hashlib,struct,subprocess,ctypes
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).parent;R=Path('/repo');raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
libs={}
for name in ['sdk','public']:
 p=D/(name+'-projection.so');subprocess.run(['gcc','-O0','-shared','-fPIC',str(D/(name+'-projection.c')),'-o',str(p)],check=True);libs[name]=ctypes.CDLL(str(p));libs[name].test.argtypes=[ctypes.c_uint32]*3
G=0x20072cb8;QS=[G+40,G+48,G+32];N=0x20082000;M=0x20081000;SP=0x200ff000;STOP=0x100000
ranges=[(int(x['start'],16),int(x['end'],16)) for x in json.loads((D/'original-receipts.json').read_text())]
cases=[('empty',[0,0,0]),('one-each',[1,1,1]),('mixed',[2,3,1]),('dh-only',[0,2,0]),('pub-aes',[2,0,1]),('aes-only',[0,0,3])];results=[]
for name,lengths in cases:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(STOP,0x1000)
 nodes={};events=[];trace=[];locks=[];reads=[];writes=[];released=[]
 for qi,(q,n) in enumerate(zip(QS,lengths)):
  first=N+qi*0x1000;u.mem_write(q,struct.pack('<II',first if n else 0,first+64*(n-1) if n else 0))
  for k in range(n):
   a=first+64*k;nodes[a]=qi*10+k;u.mem_write(a,struct.pack('<IB3x',a+64 if k+1<n else 0,qi*10+k)+bytes([(qi*43+k+0x80)&255])*56)
 for k in range(8):u.mem_write(G+60+k*4,struct.pack('<I',STOP+0x101))
 u.mem_write(M,struct.pack('<HBB',0x1234,20,0xa5)+bytes([0xc6])*28);beforeG=bytes(u.mem_read(G,128));beforeM=bytes(u.mem_read(M,32));beforeNodes={a:bytes(u.mem_read(a,64)) for a in nodes};guard=b'\xef'*32;u.mem_write(N-32,guard);u.mem_write(N+0x3000,guard)
 saved={r:0x43210000+i for i,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
 for r,v in saved.items():u.reg_write(r,v)
 for r,v in [(UC_ARM_REG_R0,M),(UC_ARM_REG_SP,SP),(UC_ARM_REG_LR,STOP|1)]:u.reg_write(r,v)
 def code(u,a,n,d):
  if a==STOP:u.emu_stop();return
  r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
  if a==0x4bf9ec:
   assert r0 in QS and SP-128<=r1<SP;qi=QS.index(r0);events.append(100+qi);trace.append(dict(kind='dequeue',queue_index=qi,queue=hex(r0),handler_output=hex(r1)))
  if a==0x4bf9b0:assert r0-8 in nodes;trace.append(dict(kind='message-free',message=hex(r0)))
  if any(lo<=a<hi for lo,hi in ranges):return
  if a==0x52b8a4:locks.append('enter');u.reg_write(UC_ARM_REG_R0,0)
  elif a==0x52b8b6:locks.append('exit')
  elif a==0x5304d4:
   assert r0 in nodes and r0 not in released
   for q in QS:
    pointer=int.from_bytes(u.mem_read(q,4),'little')
    while pointer:assert pointer!=r0;pointer=int.from_bytes(u.mem_read(pointer,4),'little')
   released.append(r0);events.append(200+nodes[r0]);trace.append(dict(kind='buffer-release-boundary',header=hex(r0),id=nodes[r0],absent_from_all_queues=True))
  else:raise RuntimeError(('unknown dependency/callback',hex(a)))
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def write(u,acc,a,n,v,d):
  assert any(q<=a and a+n<=q+8 for q in QS) or SP-128<=a and a+n<=SP;writes.append(dict(address=hex(a),size=n,value=v,pc=hex(u.reg_read(UC_ARM_REG_PC))))
 def read(u,acc,a,n,v,d):
  for pointer in nodes:
   if pointer<=a<pointer+64:assert (a-pointer,n) in [(0,4),(4,1)];reads.append(dict(address=hex(a),size=n))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read);u.emu_start(0x536235,0,count=20000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP and all(u.reg_read(r)==v for r,v in saved.items());assert bytes(u.mem_read(M,32))==beforeM and all(bytes(u.mem_read(a,64))==b for a,b in beforeNodes.items());assert bytes(u.mem_read(N-32,32))==guard and bytes(u.mem_read(N+0x3000,32))==guard
 after=bytes(u.mem_read(G,128));diff=[i for i,(a,b) in enumerate(zip(beforeG,after)) if a!=b];assert all(any(q-G<=i<q-G+8 for q in QS) for i in diff);assert all(bytes(u.mem_read(q,8))==bytes(8) for q in QS);assert released==list(nodes);assert locks==['enter','exit']*(sum(lengths)+3)
 projection={}
 for variant,lib in libs.items():
  lib.test(*lengths);projection[variant]=dict(events=[lib.event_at(i) for i in range(lib.event_count())],remaining=[lib.remaining(i) for i in range(3)])
 assert events==projection['sdk']['events'] and projection['sdk']['remaining']==[0,0,0];assert projection['public']['events']==[] and projection['public']['remaining']==lengths
 results.append(dict(case=name,lengths=lengths,events=events,source=projection,trace=trace,released_headers=[hex(a) for a in released],critical_sections=locks,writes=writes,node_reads=reads,changed_control_offsets=diff,all_inputs_and_guards_retained=True,abi_preserved=True,stock_differs_old=events!=projection['public']['events']))
(D/'results.json').write_text(json.dumps(dict(cases=results,count=6,all_pass=True,scope='real stock callback/dequeue/message-free/queue-dequeue; critical sections and final WsfBufFree mocked; old/new full callback projections with modeled providers'),indent=2)+'\n');print('Six hardware-error drain comparisons PASS')
