from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path('/Users/kalani/Repo/evenRealities-openCFW');p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();start=s.index('extern uint32_t opencfw_em9305_ll_flags_command_30d54c');body=s[start:s.index('/* Native30c33c..30c3a4:',start)]
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint16_t command;static uint8_t input[32],packet[32];
static uint32_t fail,allocs,sends,kind,length,child,query,flag0,flag1,mutate;
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){assert(c==command);kind=c;length=n;allocs++;if(mutate)command=0x201b;return fail?0:(uintptr_t)(packet+5);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)packet);sends++;return 71;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
uint32_t opencfw_em9305_ll_event_fallback_30c2e0(uint32_t id){assert(id==0xabcd);child=1;return 40;}
'''+body+r'''
uint32_t opencfw_em9305_ll_flags_command_30d54c(uint32_t id,uintptr_t f){assert(id==0xabcd);flag0=((uint8_t*)f)[0];flag1=((uint8_t*)f)[1];child=5;return 0xe7;}
uint32_t opencfw_em9305_ll_data_command_30b644(uintptr_t i,uintptr_t o){assert(i==(uintptr_t)input&&o==(uintptr_t)(input+16));for(unsigned n=0;n<16;n++)input[16+n]=0xa0+n;child=2;return 0;}
uint32_t opencfw_em9305_ll_pair_command_30e350(uint32_t id,uint32_t v){assert(id==0xabcd&&v==0x1234);child=3;return 42;}
uint32_t opencfw_em9305_ll_payload_command_30c33c(uint32_t id,uintptr_t i){assert(id==0xabcd&&i==(uintptr_t)(input+2));child=4;return 41;}
uint32_t opencfw_em9305_ll_query_command_30c6d4(uint32_t id,uintptr_t o){assert(id==0xabcd&&*(uint16_t*)o==0&&allocs==1);*(uint16_t*)o=0x9876;query++;return 43;}
static void reset(uint16_t c){command=c;memset(packet,0xcc,sizeof packet);memset(input,0,sizeof input);input[0]=0xcd;input[1]=0xab;input[2]=0x34;input[3]=0x12;fail=allocs=sends=child=query=mutate=0;}
static uint32_t run(void){return opencfw_em9305_dispatch_332278((uintptr_t)&command,(uintptr_t)input);}
int main(void){reset(0x1234);assert(run()==0&&allocs==0&&child==0);
for(unsigned a=0;a<2;a++)for(unsigned b=0;b<3;b++){reset(0xfff7);input[2]=a*2;input[3]=b;assert(run()==1&&child==5&&length==1&&kind==0xfff7&&sends==1&&packet[5]==0xe7&&flag0==a&&flag1==(b==1));}
reset(0xfff7);fail=1;assert(run()==1&&child==5&&allocs==1&&sends==0);
uint16_t cmds[]={0x2017,0x201a,0x201b,0xc7b,0xc7c};
for(unsigned i=0;i<5;i++)for(unsigned f=0;f<2;f++){reset(cmds[i]);fail=f;assert(run()==1&&allocs==1&&sends==!f&&kind==cmds[i]);if(i==0){assert(child==2&&length==17);if(!f)assert(packet[5]==0&&memcmp(packet+6,input+16,16)==0);}else if(i==3){assert(length==5&&query==!f);if(!f)assert(packet[5]==43&&packet[6]==0xcd&&packet[7]==0xab&&packet[8]==0x76&&packet[9]==0x98);}else{assert(length==3);if(!f){uint8_t st=i==1?41:i==2?40:42;assert(packet[5]==st&&packet[6]==0xcd&&packet[7]==0xab);}}}
reset(0xc7b);mutate=1;assert(run()==1&&query==0&&packet[5]==0&&packet[6]==0xcd&&packet[7]==0xab);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':19,'scope':'Actual selected dispatcher C bodies isolated with controlled true lower contracts; source-reading check, not native runtime comparison','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_ranges':['332490..3324e0','332278..332394'],'remaining_children':['30d54c','30b644','30e350','30c33c','30c6d4']}
(root/'g2/analysis/c-source-completion-20261011/em9305/response-dispatch-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS19 controlled C response dispatch cases')
