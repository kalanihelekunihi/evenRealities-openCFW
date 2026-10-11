from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();a=s.index('/* Native32f34c..');body=s[a:s.index('/* Native30c714..',a)]
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t cmd;static uint8_t packet[20],expected[15],selector=4;static unsigned fail,mutate,sends,children;
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){assert(n==9&&c==cmd);if(mutate)cmd=0x205d;return fail?0:(uintptr_t)(packet+5);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)packet&&memcmp(packet+5,expected,15)==0);sends++;return 63;}
uint32_t opencfw_em9305_ll_connection_limits_30c714(uintptr_t i,uintptr_t n){((uint8_t*)i)[0]=0x12;((uint8_t*)i)[1]=0x34;*(uint16_t*)n=0x9876;children++;return 0;}
uint32_t opencfw_em9305_ll_connection_capabilities_30c78c(uintptr_t i,uintptr_t a,uintptr_t b,uintptr_t c){((uint8_t*)i)[0]=0x12;((uint8_t*)i)[1]=0x34;*(uint16_t*)a=0x9876;*(uint16_t*)b=0xabcd;*(uint16_t*)c=0xef01;children++;return 0;}
uint32_t opencfw_em9305_ll_connection_remote_features_30bbbc(uint32_t id,uintptr_t p){assert(id==0x2468&&p==(uintptr_t)(packet+8));for(unsigned i=0;i<5;i++)((uint8_t*)p)[i]=i+1;children++;return 0x91;}
uint32_t opencfw_em9305_ll_connection_version_30beb4(uint32_t id,uint32_t s,uintptr_t p){assert(id==0x2468&&s==selector&&*(uint8_t*)p==0);*(uint8_t*)p=0x77;children++;return 0x91;}
uint32_t opencfw_em9305_ll_connection_quality_30be68(uint32_t id,uintptr_t p){assert(id==0x2468);*(uint8_t*)p=0x77;children++;return 0x91;}
'''+body+r'''
int main(void){unsigned cases=0;uint16_t cmds[]={0x2020,0x2021,0x2022,0x205a,0x205b,0x205c,0x2023,0x2015,0x2024,0x2059,0x205d,0xc2d,0x1405,0x202f,0x2025};
for(unsigned i=0;i<15;i++)for(unsigned f=0;f<2;f++){cmd=cmds[i];fail=f;mutate=sends=children=0;memset(packet,0xa5,sizeof packet);memset(expected,0xa5,sizeof expected);
if(i<6){expected[0]=0x81;expected[1]=0x68;expected[2]=0x24;}
else if(i==6){uint8_t e[]={0x81,0x12,0x34,0x76,0x98};memcpy(expected,e,5);}
else if(i==7){expected[0]=0x91;expected[1]=0x68;expected[2]=0x24;for(unsigned j=0;j<5;j++)expected[j+3]=j+1;}
else if(i>=8&&i<=10)expected[0]=0x81;
else if(i==11||i==12){uint8_t e[]={0x91,0x68,0x24,0x77};memcpy(expected,e,4);}
else if(i==13){uint8_t e[]={0x81,0x12,0x34,0x76,0x98,0xcd,0xab,0x01,0xef};memcpy(expected,e,9);}
assert(opencfw_em9305_ll_connection_response_32f34c((uintptr_t)&cmd,0x81,9,(uintptr_t)&selector,0x2468)==(f?0:63));assert(sends==!f&&children==(!f&&(i==6||i==7||i==11||i==12||i==13)));cases++;}
cmd=0x2015;fail=0;mutate=1;sends=children=0;memset(packet,0xa5,sizeof packet);memset(expected,0xa5,sizeof expected);expected[0]=0x81;assert(opencfw_em9305_ll_connection_response_32f34c((uintptr_t)&cmd,0x81,9,0,0x2468)==63&&children==0&&sends==1);cases++;printf("%u\n",cases);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'32f34c..32f494','scope':'Actual C formatter with controlled query/allocator/send children; native-reading field/reload contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('legacy-response-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled legacy response cases')
