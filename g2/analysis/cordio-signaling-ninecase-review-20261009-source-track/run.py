from pathlib import Path
import json,hashlib,ctypes,subprocess,struct,sys
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';im=raw[32:];v=im[0x53076e-0x438000:0x5308e6-0x438000];assert sha(v)=='c26ae1510d3d56ca5de518313cd89389c877a3f1047c4512ab0a547e05db9f7d'
index_before=sha((R/'.git/index').read_bytes())
sdk=(R/'g2/analysis/cordio-sdk520-parser-lead-2026-10-09-source-track/sdk-licensed-source/l2c_main.c').read_text();old=(D/'public-l2c-main.c').read_text()
assert sha(sdk.encode())=='16de435673010a4de3c1b182012981f53684703c4a0a982df9e117f8a0d8284f'
def extract(s):
 a=s.index('void l2cRxSignalingPkt(');b=s.index('{',a);depth=1;b+=1
 while depth:depth+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[a:b]
pre='''#include <stdint.h>
#include <stddef.h>
typedef uint8_t dmConnId_t;
#define DM_CONN_ID_NONE 0
#define DM_ROLE_MASTER 0
#define DM_ROLE_SLAVE 1
#define L2C_SIG_HDR_LEN 4
#define L2C_CHECK_DATA_LENGTH(len,min_len) if ((len)<(min_len)) return
static uint32_t events[64],count;
static uint8_t ci,rr;
static uint16_t ch,cl; static uintptr_t cp;
static void ev(uint32_t x){events[count++]=x;}
static dmConnId_t DmConnIdByHandle(uint16_t h){ev(0x10000000|h);return ci;}
static uint8_t DmConnRole(dmConnId_t c){ev(0x20000000|c);return rr;}
static void master(uint16_t h,uint16_t l,uint8_t *p){ev(0x30000000);ch=h;cl=l;cp=(uintptr_t)p;}
static void slave(uint16_t h,uint16_t l,uint8_t *p){ev(0x40000000);ch=h;cl=l;cp=(uintptr_t)p;}
#define L2C_TRACE_ERR1(fmt,role) ev(0x50000000|(role))
static struct {void (*masterRxSignalingPkt)(uint16_t,uint16_t,uint8_t*);void (*slaveRxSignalingPkt)(uint16_t,uint16_t,uint8_t*);} l2cCb;
'''
post='''
void test(uint16_t h,uint16_t l,uint8_t*p,uint8_t c,uint8_t r,uint8_t cb){count=0;ci=c;rr=r;ch=cl=0;cp=0;l2cCb.masterRxSignalingPkt=cb?master:NULL;l2cCb.slaveRxSignalingPkt=cb?slave:NULL;l2cRxSignalingPkt(h,l,p);}
uint32_t event_count(void){return count;} uint32_t event_at(uint32_t i){return events[i];}
uint32_t callback_h(void){return ch;} uint32_t callback_l(void){return cl;} uintptr_t callback_p(void){return cp;}
'''
libs={}
for name,s in [('sdk',sdk),('old',old)]:
 p=D/(name+'-harness.c');p.write_text(pre+extract(s)+post)
 subprocess.run(['clang','-shared','-fPIC','-O0',str(p),'-o',str(D/(name+'.dylib'))],check=True)
 lib=ctypes.CDLL(str(D/(name+'.dylib')));lib.test.argtypes=[ctypes.c_uint16,ctypes.c_uint16,ctypes.c_void_p,ctypes.c_uint8,ctypes.c_uint8,ctypes.c_uint8];lib.callback_p.restype=ctypes.c_size_t;libs[name]=lib
cases=[{'name':'short-'+str(l),'length':l,'conn':1,'role':0,'callback':1} for l in range(4)]+[{'name':'no-connection','length':4,'conn':0,'role':0,'callback':1},{'name':'master','length':4,'conn':1,'role':0,'callback':1},{'name':'slave','length':4,'conn':1,'role':1,'callback':1},{'name':'null-callback','length':4,'conn':1,'role':0,'callback':0},{'name':'uint16-max','length':65535,'conn':1,'role':0,'callback':1}]
result=[]
for c in cases:
 events=[];platform=[];callback=[];vis=[];reads=[];writes=[];u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,im);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000)
 ptr=0x20090000;buf=bytes(range(32));u.mem_write(ptr,buf);ctrl=0x200737d8;u.mem_write(ctrl,bytes([0xa5])*64);u.mem_write(ctrl+24,struct.pack('<II',0x100101 if c['callback'] else 0,0x100201 if c['callback'] else 0));cb_before=bytes(u.mem_read(ctrl,64));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x100001);u.reg_write(UC_ARM_REG_R0,0x123);u.reg_write(UC_ARM_REG_R1,c['length']);u.reg_write(UC_ARM_REG_R2,ptr)
 saved={r:0x11110000+i for i,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
 for r,value in saved.items():u.reg_write(r,value)
 def hook(uc,a,size,user):
  vis.append(hex(a));lr=uc.reg_read(UC_ARM_REG_LR)
  if a==0x100000:uc.emu_stop();return
  regs=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
  if a==0x4b6e96:events.append(0x10000000|regs[0]);uc.reg_write(UC_ARM_REG_R0,c['conn']);uc.reg_write(UC_ARM_REG_PC,lr)
  elif a==0x4b73c4:events.append(0x20000000|regs[0]);uc.reg_write(UC_ARM_REG_R0,c['role']);uc.reg_write(UC_ARM_REG_PC,lr)
  elif a in [0x100100,0x100200]:events.append(0x30000000 if a==0x100100 else 0x40000000);callback.extend(regs);uc.reg_write(UC_ARM_REG_PC,lr)
  elif a==0x4c9c50:platform.append({'callee':hex(a),'return':0});uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,lr)
  elif a==0x52a63c:events.append(0x50000000|regs[2]);platform.append({'callee':hex(a),'args':regs});uc.reg_write(UC_ARM_REG_PC,lr)
  elif not(0x53076e<=a<0x5308e6):raise RuntimeError('Unmodeled provider '+hex(a))
 def memhook(uc,access,address,size,value,user):
  (reads if user=="read" else writes).append({"address":hex(address),"size":size})
 u.hook_add(UC_HOOK_MEM_READ,memhook,user_data="read");u.hook_add(UC_HOOK_MEM_WRITE,memhook,user_data="write")
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x53076f,0,count=3000)
 assert u.reg_read(UC_ARM_REG_PC)==0x100000 and u.reg_read(UC_ARM_REG_SP)==0x200ff000
 assert all(u.reg_read(r)==value for r,value in saved.items())
 assert bytes(u.mem_read(ptr,32))==buf and bytes(u.mem_read(ctrl,64))==cb_before
 source={}
 for name,lib in libs.items():
  lib.test(0x123,c['length'],ptr,c['conn'],c['role'],c['callback']);ev=[lib.event_at(i) for i in range(lib.event_count())];args=[lib.callback_h(),lib.callback_l(),lib.callback_p()] if any(e in [0x30000000,0x40000000] for e in ev) else [];source[name]={'events':ev,'callback_arguments':args}
 assert source['sdk']['events']==events and source['sdk']['callback_arguments']==callback
 if c['length']<4:assert source['old']['events']!=events
 else:assert source['old']['events']==events and source['old']['callback_arguments']==callback
 result.append({'case':c,'stock':{'events':events,'callback_arguments':callback,'platform_trace_probes':platform,'visited':vis,'reads':reads,'writes':writes,'packet_and_control_unchanged':True,'R4_R7_and_SP_preserved':True},'source':source,'SDK_semantic_projection_matches':True})
(D/'ninecase-results.json').write_text(json.dumps({'cases':result,'count':len(result),'scope':'Original parser instructions; modeled connection, role, callback and trace providers; semantic event projection distinguishes logger implementation probes','index_before':index_before,'index_after':sha((R/'.git/index').read_bytes())},indent=2)+'\n')
(D/'stock-receipts.json').write_text(json.dumps({'payload_sha256':sha(raw),'range':{'start':'0x53076e','end_exclusive':'0x5308e6','size':376,'sha256':sha(v),'original_bytes_hex':v.hex()},'shared_literal_address':'0x530b90','shared_literal_value':hex(struct.unpack_from('<I',im,0x530b90-0x438000)[0]),'source_body_sha256':{n:sha(extract(s).encode()) for n,s in [('sdk',sdk),('old',old)]}},indent=2)+'\n')
print('PASS: 9 stock/SDK semantic projections; 4 short-length differences from old source; packet/control preservation and callback args')
