from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('extern uint32_t opencfw_em9305_ll_test_30b1ac'):s.index('/* Native30bb14..')]
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x805854u','test_flag')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request,command;static uint8_t input[20],buffer[64],test_flag;static uint32_t status,id;static unsigned allocations,sends,childcalls,alloc_ok,mutation,prehandled;static uint32_t expected_length;
uint32_t opencfw_em9305_dispatch_32fd18(uintptr_t r,uintptr_t in){assert(r==(uintptr_t)&request);(void)in;return prehandled;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t length,uint32_t cmd){assert(length==expected_length&&cmd==command);allocations++;if(mutation)request=0;if(!alloc_ok)return 0;return (uintptr_t)(buffer+5);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)buffer);sends++;return 123;}
uint32_t opencfw_em9305_ll_pack_byte(uintptr_t p,uint32_t v){*(uint8_t*)p=v;return 1;}
uint32_t opencfw_em9305_ll_pack_halfword(uintptr_t p,uint32_t v){*(uint8_t*)p=v;*(uint8_t*)(p+1)=v>>8;return 2;}
uint32_t opencfw_em9305_ll_test_30b1ac(uintptr_t p){assert(memcmp((void*)p,input,3)==0&&*(uint32_t*)(p+4)==(uint32_t)((uintptr_t)input+3));childcalls++;return status;}
uint32_t opencfw_em9305_ll_test_30d35c(uint32_t x){assert(x==id);childcalls++;return status;}
uint32_t opencfw_em9305_ll_test_30e050(uintptr_t p){assert(*(uint16_t*)p==id&&*(uint8_t*)(p+2)==input[2]&&*(uint8_t*)(p+3)==input[3]&&*(uint8_t*)(p+4)==input[4]);assert(*(uint16_t*)(p+6)==input[5]+256u*input[6]&&*(uint16_t*)(p+8)==input[7]+256u*input[8]);assert(*(uint32_t*)(p+12)==input[9]+256u*input[10]+65536u*input[11]&&*(uint8_t*)(p+16)==input[12]&&*(uint32_t*)(p+20)==(uint32_t)((uintptr_t)input+13));childcalls++;return status;}
#define CONTROL(name) uint32_t name(uint32_t x,uint32_t a){assert(x==id&&a==input[2]);childcalls++;return status;}
CONTROL(opencfw_em9305_ll_test_30cb24)
CONTROL(opencfw_em9305_ll_test_30c2dc)
CONTROL(opencfw_em9305_ll_test_30c2d4)
uint32_t opencfw_em9305_ll_test_30bc3c(uintptr_t p){*(uint16_t*)p=0x1234;childcalls++;return 99;}
uint32_t opencfw_em9305_ll_test_30bd18(uint32_t x,uintptr_t p){assert(x==id);*(uint8_t*)p=0x67;childcalls++;return status;}
uint32_t opencfw_em9305_ll_test_30bb14(void){childcalls++;return 0x1234;}
uint32_t opencfw_em9305_ll_test_30bb20(void){childcalls++;return 0x56;}
uint32_t opencfw_em9305_ll_test_30bdc4(void){childcalls++;return 0x789a;}
uint32_t opencfw_em9305_ll_test_30bdd0(void){childcalls++;return 0xbc;}
uint32_t opencfw_em9305_ll_test_30c728(uint32_t x,uintptr_t a,uintptr_t b,uintptr_t c){assert(x==id&&*(uint16_t*)a==0&&*(uint32_t*)b==0&&*(uint32_t*)c==0);*(uint16_t*)a=0x1234;*(uint32_t*)b=0x89abcdef;*(uint32_t*)c=0x76543210;childcalls++;return status;}
#define QUERY(name) uint32_t name(uint32_t x,uintptr_t p){assert(x==id);for(unsigned i=0;i<28;i++)*(uint8_t*)(p+i)=i+0x30;childcalls++;return status;}
QUERY(opencfw_em9305_ll_test_30c2bc)
QUERY(opencfw_em9305_ll_test_30c2d8)
QUERY(opencfw_em9305_ll_test_30c724)
uint32_t opencfw_em9305_ll_test_response_330f08(uintptr_t p,uint32_t st,uint32_t x,uintptr_t scratch){assert(st==status&&x==id);*(uint8_t*)p=st;*(uint8_t*)(p+1)=x;*(uint8_t*)(p+2)=x>>8;memcpy((void*)(p+3),(void*)scratch,12);childcalls++;return 0;}
"""+body+r"""
static unsigned length(unsigned c){switch(c){case 0xc15:return 3;case 0xc16:case 0xc83:return 1;case 0x2060:return 7;case 0x2061:return 12;case 0x206e:case 0x206f:case 0x2070:case 0x2071:return 3;case 0x2072:case 0x2073:return 15;case 0x2075:return 31;case 0x1405:return 4;default:return 0;}}
int main(void){unsigned count=0;uint32_t statuses[]={0,2,12,18,255,256,0xdeadbeef};
for(unsigned c=0;c<65536;c++){if(length(c))continue;request=c;prehandled=0;assert(opencfw_em9305_dispatch_32f85c((uintptr_t)&request,0)==0);count++;}
unsigned commands[]={0xc15,0xc16,0xc83,0x2060,0x2061,0x206e,0x206f,0x2070,0x2071,0x2072,0x2073,0x2075,0x1405};
for(unsigned q=0;q<13;q++){for(unsigned pattern=0;pattern<256;pattern++){for(unsigned st=0;st<7;st++){for(alloc_ok=0;alloc_ok<2;alloc_ok++){for(mutation=0;mutation<2;mutation++){for(prehandled=0;prehandled<2;prehandled++){
 command=request=commands[q];expected_length=length(command);status=statuses[st];for(unsigned i=0;i<20;i++)input[i]=pattern+i*17;id=input[0]+256u*input[1];memset(buffer,0xa5,64);test_flag=0xa5;allocations=sends=childcalls=0;
 assert(opencfw_em9305_dispatch_32f85c((uintptr_t)&request,(uintptr_t)input)==1);assert(allocations==!prehandled&&sends==(!prehandled&&alloc_ok));
 uint8_t expected[64];memset(expected,0xa5,64);uint8_t *out=expected+5;
 if(!prehandled&&alloc_ok&&!mutation){
  switch(command){case 0xc15:out[0]=0;out[1]=0x34;out[2]=0x12;break;case 0xc16:case 0xc83:out[0]=status;break;case 0x2060:{uint8_t v[]={0,0x34,0x12,0x56,0x9a,0x78,0xbc};memcpy(out,v,7);break;}case 0x2061:{uint8_t v[]={status,id,id>>8,0x34,0x12,0xef,0xcd,0xab,0x89,0x10,0x32,0x54};memcpy(out,v,12);break;}case 0x1405:out[0]=status;out[1]=id;out[2]=id>>8;out[3]=0x67;break;case 0x206e:case 0x206f:case 0x2070:case 0x2071:out[0]=status;out[1]=id;out[2]=id>>8;break;case 0x2072:case 0x2073:case 0x2075:out[0]=status;out[1]=id;out[2]=id>>8;for(unsigned i=3;i<expected_length;i++)out[i]=0x30+i-3;break;}
 }
 assert(memcmp(buffer,expected,64)==0);
 unsigned expectedflag=!prehandled&&command==0x2071&&status==0?1:0xa5;if(!prehandled&&alloc_ok&&!mutation&&command==0x2073&&status==0)expectedflag=0;assert(test_flag==expectedflag);count++;
}}}}}}printf("%u\n",count);}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-dispatch-receipt.json').write_text(json.dumps({'cases_passed':n,'native_range':'32f85c..32fc86','scope':'Actual C with controlled preliminary dispatcher and genuine children; all command values, decoded fields, allocation failure, post-allocation command reload to unsupported command, response bytes and flag changes. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
