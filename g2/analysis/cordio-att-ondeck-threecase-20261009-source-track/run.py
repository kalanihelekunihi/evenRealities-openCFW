from pathlib import Path
import json,struct,hashlib,ctypes,subprocess,sys
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'g2/analysis/cordio-att-ondeck-source-lead-20261009-source-track';raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';im=raw[32:];body=im[0x4b5448-0x438000:0x4b557a-0x438000];assert sha(body)=='f8256375f5cad966c0c74be78977523bce416b3fdeb41f06c9b98537cd9edd18'
def extract(t):
 a=t.index('void attcProcRsp(');i=t.index('{',a);depth=0
 while i<len(t):
  depth+=(t[i]=='{')-(t[i]=='}');i+=1
  if not depth:return t[a:i]
pre=r'''#include <stdint.h>
#include <stddef.h>
#define ATTC_MSG_API_NONE 0
#define ATT_OPCODE_2_METHOD(x) ((x)/2)
#define ATT_METHOD_SIGNED_WRITE_CMD 17
#define ATT_METHOD_ERR 0
#define ATT_METHOD_MTU 1
#define L2C_PAYLOAD_START 8
#define ATT_HDR_LEN 1
#define ATT_SUCCESS 0
#define ATTC_NOT_CONTINUING 0
#define ATT_CCB_STATUS_FLOW_DISABLED 2
#define ATT_BEARER_SLOT_ID 0
#define ATT_CHECK_DATA_LENGTH(l,m) if((l)<(m))return
struct hdr {uint16_t param;uint8_t event,status;};
typedef struct {struct hdr hdr;uint8_t*pPkt;uint16_t handle;} Msg;
typedef struct {struct hdr hdr;uint8_t*pValue;uint16_t valueLen,handle;uint8_t continuing;} attEvt_t;
struct Main {struct {uint8_t control;} sccb[3];};
typedef struct {struct Main*pMainCcb;Msg outReq;uint8_t outReqTimer[16],slot,connId;} attcCcb_t;
static struct {Msg onDeck[3];} attcCb;
static struct {void(*cback)(attEvt_t*);} attCb;
static uint32_t ev[32],cnt,selected;
static void rec(uint32_t x){ev[cnt++]=x;}
static void WsfTimerStop(void*p){rec(1);}
static void attcFreePkt(Msg*m){rec(3);m->pPkt=NULL;}
static void attcSendReq(attcCcb_t*c){rec(5);}
static void attcSetupReq(attcCcb_t*c,Msg*m){selected=(uint32_t)(m-attcCb.onDeck);rec(100+selected);}
static void process(attcCcb_t*c,uint16_t l,uint8_t*p,attEvt_t*e){rec(2);}
typedef void(*attcProcRsp_t)(attcCcb_t*,uint16_t,uint8_t*,attEvt_t*);
static attcProcRsp_t attcProcRspTbl[18]={[9]=process};
static uint8_t attcMinPduLen[18]={[9]=1};
'''
post=r'''
void test(uint8_t e0,uint8_t e1){cnt=0;selected=99;struct Main main={0};attcCcb_t c={0};uint8_t p[32]={0};p[8]=0x13;c.pMainCcb=&main;c.outReq.hdr.event=9;c.outReq.hdr.status=0;c.connId=1;c.slot=0;c.outReq.handle=0x234;attCb.cback=NULL;attcCb.onDeck[0].hdr.event=e0;attcCb.onDeck[1].hdr.event=e1;attcCb.onDeck[2].hdr.event=0;attcProcRsp(&c,1,p);}
uint32_t count(void){return cnt;}uint32_t event(uint32_t i){return ev[i];}uint32_t select_index(void){return selected;}uint32_t remaining(uint32_t i){return attcCb.onDeck[i].hdr.event;}
'''
libs={};sourcehash={}
for name in ['sdk','public']:
 t=(S/(name+'-attc_proc.c')).read_text();f=extract(t);sourcehash[name]=sha(f.encode());c=D/(name+'-harness.c');c.write_text(pre+f+post);libpath=D/(name+'.dylib');subprocess.run(['clang','-O0','-shared','-fPIC',str(c),'-o',str(libpath)],check=True);lib=ctypes.CDLL(str(libpath));lib.test.argtypes=[ctypes.c_uint8,ctypes.c_uint8];libs[name]=lib
results=[];G=0x2006f904;A=0x200610ac;P=0x20090000;Q=G+396;SP=0x200ff000
for title,e0,e1 in [('both-ready',10,11),('only-entry0',10,0),('only-entry1',0,11)]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,im);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000);u.mem_write(G,bytes(512));u.mem_write(A,bytes(128));u.mem_write(P,bytes(32));u.mem_write(P+8,b'\x13');u.mem_write(G,struct.pack('<I',A));u.mem_write(G+6,b'\x09\x00');u.mem_write(G+12,struct.pack('<H',0x234));u.mem_write(G+40,b'\x00\x01');u.mem_write(Q+2,bytes([e0]));u.mem_write(Q+14,bytes([e1]));packet=bytes(u.mem_read(P,32));before=bytes(u.mem_read(G,512));events=[];reads=[];writes=[];visited=[];selected=[]
 for reg,val in [(UC_ARM_REG_SP,SP),(UC_ARM_REG_LR,0x100001),(UC_ARM_REG_R0,G),(UC_ARM_REG_R1,1),(UC_ARM_REG_R2,P)]:u.reg_write(reg,val)
 saved={r:0x11110000+i for i,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
 for r,v in saved.items():u.reg_write(r,v)
 def hook(uc,a,size,user):
  visited.append(hex(a));lr=uc.reg_read(UC_ARM_REG_LR)
  if a==0x100000:uc.emu_stop();return
  if a==0x52a4d2:assert uc.reg_read(UC_ARM_REG_R0)==G+24;events.append(1)
  elif a==0x4b53dc:assert [uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]==[G,1,P];events.append(2)
  elif a==0x531ac0:assert uc.reg_read(UC_ARM_REG_R0)==G+4;events.append(3)
  elif a==0x531160:
   assert uc.reg_read(UC_ARM_REG_R0)==G;q=uc.reg_read(UC_ARM_REG_R1);assert q in [Q,Q+12];i=(q-Q)//12;events.append(100+i);selected.append({'index':i,'pointer':hex(q),'event':u.mem_read(q+2,1)[0]})
  elif 0x4b5448<=a<0x4b557a:return
  else:raise RuntimeError('Unmodeled provider '+hex(a))
  uc.reg_write(UC_ARM_REG_PC,lr)
 def mem(uc,access,a,size,value,user):(reads if user=='r' else writes).append({'address':hex(a),'size':size})
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,mem,user_data='r');u.hook_add(UC_HOOK_MEM_WRITE,mem,user_data='w');u.emu_start(0x4b5449,0,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x100000;assert u.reg_read(UC_ARM_REG_SP)==SP and all(u.reg_read(r)==v for r,v in saved.items());assert bytes(u.mem_read(P,32))==packet
 after=bytes(u.mem_read(G,512));diff=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b];assert set(diff)<={6,398};remaining=[u.mem_read(Q+2,1)[0],u.mem_read(Q+14,1)[0]];sr={}
 for name,l in libs.items():
  l.test(e0,e1);sr[name]={'events':[l.event(i) for i in range(l.count())],'remaining':[l.remaining(0),l.remaining(1)],'selected_index':l.select_index()}
 assert events==sr['sdk']['events'] and remaining==sr['sdk']['remaining'];assert events!=sr['public']['events'] or remaining!=sr['public']['remaining'];results.append({'case':title,'initial_events':[e0,e1],'stock':{'events':events,'selected':selected,'remaining':remaining,'changed_control_offsets':diff,'reads':reads,'writes':writes,'visited':visited,'packet_unchanged':True,'ABI_preserved':True},'source':sr})
(D/'RESULT.json').write_text(json.dumps({'cases':results,'count':3,'stock_sha256':sha(body),'source_body_sha256':sourcehash,'scope':'original dispatcher with valid write response; timer/processor/free/setup mocked; actual proc9 pointer/min1 tables authenticated; selected queue representation only'},indent=2)+'\n');print('PASS 3 stock/SDK queue-selection projections; old public differs in all 3')
