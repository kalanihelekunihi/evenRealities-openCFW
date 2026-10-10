from pathlib import Path
import json,struct,hashlib,sys,ctypes,subprocess
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import *
from unicorn.arm_const import *
O=Path(__file__).resolve().parent; D=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/source-discovery-parallel-2026-10-09/smp-stale-queue-20261010'); R=next(p for p in D.parents if (p/'g2/blobs').exists())
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes(); sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
extents=[(0x537d0c,0x537e9e,'c6c182f8937a91efc42995289820d0589b5ae839960cde0d83aec3f40ba0dbba'),(0x4bf9ec,0x4bfa00,'a0a7fa1b14bb01ca88fa84046451d92d37a5df0e01effffeb5c3cbe4c87a152d'),(0x4bf9b0,0x4bf9ba,'52a3c4e96bd27c58ae08a64f5ecf63cd67877de12306fbeb9245865fe9e2fead'),(0x538c4a,0x538c6e,'b89add9a6f39622dc9277b91669b4978b136cf95d4c09bff5a8f65d02c3a7080')]
for a,b,h in extents: assert sha(raw[a-0x437fe0:b-0x437fe0])==h
Q=struct.unpack_from('<I',raw,0x537ee8-0x437fe0)[0];assert Q==0x20072cd8
t=(D/'sources/smp_main.c').read_text();a=t.index('void SmpHandler(');i=t.index('{',a);depth=0
while i<len(t):
 depth+=(t[i]=='{')-(t[i]=='}');i+=1
 if not depth: break
body=t[a:i]
pre=r'''#include <stdint.h>
#include <stddef.h>
typedef uint8_t wsfEventMask_t; typedef uint8_t wsfHandlerId_t;typedef uint8_t dmConnId_t;
typedef struct{uint16_t param;uint8_t event,status;}wsfMsgHdr_t;
typedef struct{uint8_t connId,token;}smpCcb_t;typedef wsfMsgHdr_t smpMsg_t;
typedef struct{wsfMsgHdr_t hdr;void*pPlainText;}secCmacMsg_t;
typedef struct{uint32_t id;}secQueueBuf_t;
typedef struct{secQueueBuf_t entries[4];uint32_t pos,n;}Queue;
typedef struct{Queue aesEncQueue;}secCb_t;secCb_t secCb;
static smpCcb_t ccb;static uint32_t events[32],count;
#define SMP_DB_SERVICE_IND 32
#define SMP_MSG_WSF_CMAC_CMPL 28
#define SMP_MSG_WSF_AES_CMPL 11
#define DM_CONN_ID_NONE 0
#define SMP_TRACE_WARN2(...) ((void)0)
static void rec(uint32_t x){events[count++]=x;}
static void SmpDbService(void){rec(900);}
static void WsfBufFree(void*p){rec(901);}
static smpCcb_t*smpCcbByConnId(dmConnId_t x){return &ccb;}
static void smpSmExecute(smpCcb_t*c,smpMsg_t*m){rec(500);}
static void*WsfMsgDeq(Queue*q,wsfHandlerId_t*h){rec(100);if(q->pos==q->n)return NULL;*h=(uint8_t)q->entries[q->pos].id;return &q->entries[q->pos++];}
static void WsfMsgFree(secQueueBuf_t*p){rec(200+p->id);}
'''
post=r'''
void test(uint8_t token,uint8_t status,uint8_t conn,uint32_t n){count=0;secCb.aesEncQueue.pos=0;secCb.aesEncQueue.n=n;for(uint32_t i=0;i<n;i++)secCb.aesEncQueue.entries[i].id=i;ccb.connId=conn;ccb.token=token;wsfMsgHdr_t msg={1,11,status};SmpHandler(0,&msg);}
uint32_t event_count(void){return count;}uint32_t event_at(uint32_t i){return events[i];}uint32_t remaining(void){return secCb.aesEncQueue.n-secCb.aesEncQueue.pos;}
'''
assert (D/'source-projection.c').read_text()==pre+body+post
# Replay the sealed existing source projection library; no rebuild.
lib=ctypes.CDLL(str(D/'projection.dylib'));lib.test.argtypes=[ctypes.c_uint8,ctypes.c_uint8,ctypes.c_uint8,ctypes.c_uint32]
results=[];C=0x20080000;M=0x20081000;N=0x20082000;SP=0x200ff000
cases=[('empty-stale',7,6,1,[]),('stale-only',7,6,1,[6,6]),('current-token',7,7,1,[7,7]),('mixed-queue-stale-trigger',7,6,1,[6,7,8]),('closed-connection',7,6,0,[6,7])]
for title,token,status,conn,node_tokens in cases:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000)
 u.mem_write(C+61,bytes([conn]));u.mem_write(C+65,bytes([token]));u.mem_write(M,struct.pack('<HBB',1,11,status)+bytes(12));n=len(node_tokens)
 u.mem_write(Q,struct.pack('<II',N if n else 0,N+64*(n-1) if n else 0))
 for k,nt in enumerate(node_tokens):u.mem_write(N+64*k,struct.pack('<IB3x',N+64*(k+1) if k+1<n else 0,k)+struct.pack('<HBB',1,11,nt)+bytes([0xa0+k])*52)
 before_nodes=bytes(u.mem_read(N,64*n));before_msg=bytes(u.mem_read(M,16));before_ccb=bytes(u.mem_read(C,80));events=[];trace=[];writes=[];reads=[];locks=[];stack_saved={r:0x12340000+k for k,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
 for r,v in stack_saved.items():u.reg_write(r,v)
 for r,v in [(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,M),(UC_ARM_REG_SP,SP),(UC_ARM_REG_LR,0x100001)]:u.reg_write(r,v)
 def hook(uc,a,size,user):
  if a==0x100000:uc.emu_stop();return
  regs=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
  if a==0x4bf9ec:assert regs[0]==Q;events.append(100);trace.append({'kind':'dequeue','queue':hex(regs[0]),'handler_output':hex(regs[1])})
  elif a==0x4bf9b0:assert (regs[0]-N-8)%64==0;trace.append({'kind':'message-free','message':hex(regs[0])})
  if any(lo<=a<hi for lo,hi,h in extents):return
  if a==0x5375fc:assert regs[0]==1;uc.reg_write(UC_ARM_REG_R0,C)
  elif a==0x4c9c50:uc.reg_write(UC_ARM_REG_R0,0)
  elif a==0x43d0ce:uc.reg_write(UC_ARM_REG_R0,0)
  elif a==0x52a63c:assert uc.reg_read(UC_ARM_REG_R2)==token and uc.reg_read(UC_ARM_REG_R3)==status
  elif a==0x52b8a4:locks.append('enter');uc.reg_write(UC_ARM_REG_R0,0)
  elif a==0x52b8b6:locks.append('exit')
  elif a==0x5304d4:
   assert regs[0] in [N+64*k for k in range(n)];k=(regs[0]-N)//64;events.append(200+k);trace.append({'kind':'buffer-free','header':hex(regs[0]),'id':k})
  elif a==0x56ee62:assert regs[:2]==[C,M];events.append(500)
  else:raise RuntimeError('unmodeled provider '+hex(a))
  uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def write(uc,access,a,size,value,user):writes.append({'address':hex(a),'size':size,'value':value});assert Q<=a and a+size<=Q+8 or SP-256<=a and a+size<=SP
 def read(uc,access,a,size,value,user):
  if N<=a<N+64*n:
   assert (a-N)%64 in [0,4] and size in [1,4]
   reads.append({'address':hex(a),'size':size})
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read);u.emu_start(0x537d0d,0,count=5000)
 assert u.reg_read(UC_ARM_REG_PC)==0x100000 and u.reg_read(UC_ARM_REG_SP)==SP and all(u.reg_read(r)==v for r,v in stack_saved.items())
 assert bytes(u.mem_read(M,16))==before_msg and bytes(u.mem_read(C,80))==before_ccb and bytes(u.mem_read(N,64*n))==before_nodes
 head,tail=struct.unpack('<II',bytes(u.mem_read(Q,8)));remaining=0 if not head else n
 lib.test(token,status,conn,n);source_events=[lib.event_at(k) for k in range(lib.event_count())];assert events==source_events and remaining==lib.remaining()
 assert locks==['enter','exit']*(n+1 if conn and token!=status else 0)
 results.append({'case':title,'token':token,'status':status,'connection':conn,'node_tokens':node_tokens,'events':events,'source_events':source_events,'queue_after':[hex(head),hex(tail)],'remaining':remaining,'provider_trace':trace,'critical_section_events':locks,'writes':writes,'node_reads':reads,'inputs_unchanged':True,'ABI_preserved':True})
(O/'replay-results.json').write_text(json.dumps({'count':len(results),'cases':results,'stock_sha256':sha(raw),'executed_extents':[{'start':hex(a),'end':hex(b),'sha256':h} for a,b,h in extents],'queue_literal_address':'0x537ee8','queue_address':hex(Q),'literal_sha256':sha(raw[0x537ee8-0x437fe0:0x537eec-0x437fe0]),'source_body_sha256':sha(body.encode()),'scope':'original handler/dequeue/queue-dequeue/message-free; lookup, logging gates, critical section, buffer-free and state-machine mocked'},indent=2)+'\n')
print('PASS',len(results),'original-byte/source-projection queue fixtures')
