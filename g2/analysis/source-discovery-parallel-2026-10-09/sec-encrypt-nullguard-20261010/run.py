from pathlib import Path
import sys,json,struct,hashlib,subprocess,ctypes
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'g2/blobs').exists());raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
extents=[(0x536234,0x536324),(0x4bf9ec,0x4bfa00),(0x538c4a,0x538c6e)]; receipts=[]
known={0x4bf9ec:'a0a7fa1b14bb01ca88fa84046451d92d37a5df0e01effffeb5c3cbe4c87a152d',0x538c4a:'b89add9a6f39622dc9277b91669b4978b136cf95d4c09bff5a8f65d02c3a7080'}
for a,b in extents:
 h=sha(raw[a-0x437fe0:b-0x437fe0]);assert a not in known or h==known[a];receipts.append({'start':hex(a),'end':hex(b),'sha256':h})
assert struct.unpack_from('<I',raw,0x5363ec-0x437fe0)[0]==0x20072cd8
def extract(t):
 a=t.index('static void secHciCback(');i=t.index('{',a);depth=0
 while i<len(t):
  depth+=(t[i]=='{')-(t[i]=='}');i+=1
  if not depth:return t[a:i]
pre=r'''#include <stdint.h>
#include <stddef.h>
#include <string.h>
typedef uint8_t wsfHandlerId_t;
typedef struct{uint16_t param;uint8_t event,status;}Hdr;
typedef union{Hdr hdr;struct{Hdr hdr;uint8_t status,data[16];}leEncryptCmdCmpl;struct{Hdr hdr;uint8_t status,randNum[8];}leRandCmdCmpl;}hciEvt_t;
typedef struct{uint8_t pad[52],type;}secQueueBuf_t;
typedef struct{int unused;}Queue;
typedef void(*CB)(secQueueBuf_t*,hciEvt_t*,wsfHandlerId_t);
static struct{uint8_t rand[32],randTop;Queue aesEncQueue,pubKeyQueue,dhKeyQueue;CB hciCbackTbl[5];}secCb;
static secQueueBuf_t buf;static hciEvt_t evt;static uint32_t events[16],count;static int empty;
#define HCI_LE_RAND_CMD_CMPL_CBACK_EVT 28
#define HCI_LE_ENCRYPT_CMD_CMPL_CBACK_EVT 27
#define HCI_LE_READ_LOCAL_P256_PUB_KEY_CMPL_CBACK_EVT 37
#define HCI_LE_GENERATE_DHKEY_CMPL_CBACK_EVT 38
#define HCI_HW_ERROR_CBACK_EVT 20
#define HCI_RAND_LEN 8
#define SEC_HCI_RAND_MULT 4
#define HCI_ENCRYPT_DATA_LEN 16
#define SEC_TYPE_CCM 3
#define SEC_TYPE_CMAC 1
#define SEC_TYPE_AES_REV 4
#define WSF_ASSERT(x) ((void)0)
static void*WsfMsgDeq(Queue*q,wsfHandlerId_t*h){events[count++]=100;*h=36;return empty?NULL:&buf;}
static void WsfMsgFree(void*p){events[count++]=400;}
static void WStrReverse(uint8_t*p,uint32_t n){events[count++]=200;for(uint32_t i=0;i<n/2;i++){uint8_t t=p[i];p[i]=p[n-1-i];p[n-1-i]=t;}}
static void callback(secQueueBuf_t*b,hciEvt_t*e,wsfHandlerId_t h){events[count++]=300+b->type;}
'''
post=r'''
void test(int type){count=0;empty=type<0;memset(&buf,0,sizeof(buf));memset(&evt,0,sizeof(evt));buf.type=type;evt.hdr.event=27;for(int i=0;i<16;i++)evt.leEncryptCmdCmpl.data[i]=i;for(int i=0;i<5;i++)secCb.hciCbackTbl[i]=callback;secHciCback(&evt);}
uint32_t event_count(void){return count;}uint32_t event_at(uint32_t i){return events[i];}uint32_t data_at(uint32_t i){return evt.leEncryptCmdCmpl.data[i];}
'''
libs={};bodyhash={}
for name in ['sdk','registered']:
 t=(D/(name+'-sec_main.c')).read_text();body=extract(t);bodyhash[name]=sha(body.encode());c=D/(name+'-projection.c');c.write_text(pre+body+post);dll=D/(name+'-projection.dylib');subprocess.run(['clang','-O0','-shared','-fPIC',str(c),'-o',str(dll)],check=True);l=ctypes.CDLL(str(dll));l.test.argtypes=[ctypes.c_int];libs[name]=l
SE=0x20072cb8;Q=SE+32;N=0x20082000;M=0x20081000;SP=0x200ff000;results=[]
for typ in [-1,0,1,3,4]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000)
 u.mem_write(M,struct.pack('<HBB',0,27,0)+b'\0'+bytes(range(16))+bytes(11));u.mem_write(Q,struct.pack('<II',N if typ>=0 else 0,N if typ>=0 else 0));u.mem_write(N,struct.pack('<IB3x',0,36)+bytes(52)+bytes([max(typ,0)])+bytes(3))
 for t in range(5):u.mem_write(SE+60+4*t,struct.pack('<I',0x100101+16*t))
 original_node=bytes(u.mem_read(N,64));before_event=bytes(u.mem_read(M,32));events=[];locks=[];faults=[];reads=[];writes=[];callback_args=[]
 saved={r:0x789a0000+i for i,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
 for r,v in saved.items():u.reg_write(r,v)
 for r,v in [(UC_ARM_REG_R0,M),(UC_ARM_REG_SP,SP),(UC_ARM_REG_LR,0x100001)]:u.reg_write(r,v)
 def code(uc,a,size,user):
  if a==0x100000:uc.emu_stop();return
  if a==0x4bf9ec:assert uc.reg_read(UC_ARM_REG_R0)==Q;events.append(100)
  if any(lo<=a<hi for lo,hi in extents):return
  if a==0x52b8a4:locks.append('enter');uc.reg_write(UC_ARM_REG_R0,0)
  elif a==0x52b8b6:locks.append('exit')
  elif a==0x56d8f0:
   assert [uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1]]==[M+5,16];events.append(200);uc.mem_write(M+5,bytes(uc.mem_read(M+5,16))[::-1])
  elif a in [0x100100+16*t for t in range(5)]:
   t=(a-0x100100)//16;assert t==typ;args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];assert args==[N+8,M,36];callback_args.append([hex(x) for x in args]);events.append(300+t)
  else:raise RuntimeError('unmodeled provider '+hex(a))
  uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def memread(uc,access,a,size,value,user):reads.append({'address':hex(a),'size':size,'pc':hex(uc.reg_read(UC_ARM_REG_PC))})
 def memwrite(uc,access,a,size,value,user):
  writes.append({'address':hex(a),'size':size,'value':value});assert Q<=a and a+size<=Q+8 or SP-256<=a and a+size<=SP
 def invalid(uc,access,a,size,value,user):faults.append({'address':hex(a),'size':size,'pc':hex(uc.reg_read(UC_ARM_REG_PC)),'access':access});return False
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,memread);u.hook_add(UC_HOOK_MEM_WRITE,memwrite);u.hook_add(UC_HOOK_MEM_READ_UNMAPPED,invalid)
 try:u.emu_start(0x536235,0,count=2000)
 except UcError as e:
  assert typ==-1 and e.errno==UC_ERR_READ_UNMAPPED
 assert locks==['enter','exit'];assert bytes(u.mem_read(N,64))==original_node
 after_event=bytes(u.mem_read(M,32));assert after_event[:5]==before_event[:5] and after_event[21:]==before_event[21:]
 source={}
 for name,l in libs.items():
  if name=='sdk' and typ==-1:source[name]={'execution':'not run: unchanged source dereferences null after disabled assertion; static projection only'};continue
  l.test(typ);source[name]={'events':[l.event_at(i) for i in range(l.event_count())],'data':[l.data_at(i) for i in range(16)]}
 if typ==-1:
  assert faults==[{'address':'0x34','size':1,'pc':'0x53628e','access':UC_MEM_READ_UNMAPPED}];assert events==[100] and source['registered']['events']==[100]
 else:
  assert not faults and u.reg_read(UC_ARM_REG_PC)==0x100000 and u.reg_read(UC_ARM_REG_SP)==SP and all(u.reg_read(r)==v for r,v in saved.items());assert events==source['sdk']['events']==source['registered']['events'];assert list(after_event[5:21])==source['sdk']['data']==source['registered']['data'];assert bytes(u.mem_read(Q,8))==bytes(8)
 results.append({'type':typ,'case':'direct-ABI-empty' if typ<0 else 'nonempty-type'+str(typ),'stock_events':events,'faults':faults,'callback_args':callback_args,'critical_sections':locks,'event_data_after':list(after_event[5:21]),'reads':reads,'writes':writes,'source':source,'node_unchanged':True,'return_ABI_preserved':typ>=0})
(D/'results.json').write_text(json.dumps({'count':len(results),'cases':results,'stock_sha256':sha(raw),'extents':receipts,'source_body_sha256':bodyhash,'unicorn_version':__import__('unicorn').__version__,'scope':'original security callback, message dequeue and queue dequeue; source projections with assertions disabled; critical sections, byte reversal and type callbacks mocked'},indent=2)+'\n');print('PASS 4 nonempty stock/SDK/registered comparisons; empty direct-ABI stock read fault versus registered guarded return')
