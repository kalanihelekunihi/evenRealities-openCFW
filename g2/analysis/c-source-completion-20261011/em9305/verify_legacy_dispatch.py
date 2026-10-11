from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();a=s.index('/* Native32ef10..');body=s[a:s.index('extern uint32_t opencfw_em9305_ll_connection_limits_',a)]
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t cmd;static uint8_t input[24];static unsigned early,calls,events,responses,expect_child,expect_status,expect_len,expect_id;static uintptr_t expect_payload;
static uint32_t id(void){return input[0]+((uint32_t)input[1]<<8);}
uint32_t opencfw_em9305_dispatch_32f494(uintptr_t r,uintptr_t i){assert(r==(uintptr_t)&cmd&&i==(uintptr_t)input);return early;}
uint32_t opencfw_em9305_ll_stream_control_decode_332a78(uintptr_t c,uintptr_t i){assert(i==(uintptr_t)(input+2));memcpy((void*)c,input+2,12);return 12;}
static uint32_t take(unsigned tag,uint32_t a){assert(tag==expect_child&&a==id());calls++;return 0x91;}
#define ONE(name,tag) uint32_t name(uint32_t a){return take(tag,a);}
ONE(opencfw_em9305_ll_connection_query_30cb28,1)
ONE(opencfw_em9305_ll_connection_read_30c860,2)
ONE(opencfw_em9305_ll_connection_action_30c8c8,3)
#define CONTROL(name,tag) uint32_t name(uint32_t a,uintptr_t b){assert(memcmp((void*)b,input+2,12)==0);return take(tag,a);}
CONTROL(opencfw_em9305_ll_connection_parameters_30b1b0,4)
CONTROL(opencfw_em9305_ll_connection_modify_30c998,5)
#define BYTE(name,tag) uint32_t name(uint32_t a,uint32_t b){assert(b==input[2]);return take(tag,a);}
BYTE(opencfw_em9305_ll_connection_mode_30c944,6)
BYTE(opencfw_em9305_ll_connection_disconnect_30b570,7)
uint32_t opencfw_em9305_ll_connection_times_30d3c4(uint32_t a,uint32_t b,uint32_t c){assert(b==input[2]+((uint32_t)input[3]<<8)&&c==input[4]+((uint32_t)input[5]<<8));return take(8,a);}
uint32_t opencfw_em9305_ll_connection_value_30e38c(uint32_t a,uint32_t b){assert(b==input[2]+((uint32_t)input[3]<<8));return take(9,a);}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t r,uint32_t s){assert(r==(uintptr_t)&cmd&&s==0x91&&calls==1);events++;return 0;}
uint32_t opencfw_em9305_ll_connection_response_32f34c(uintptr_t r,uint32_t s,uint32_t n,uintptr_t p,uint32_t i){assert(r==(uintptr_t)&cmd&&s==expect_status&&n==expect_len&&p==expect_payload&&i==expect_id);responses++;return 0;}
'''+body+r'''
static void reset(uint16_t c){cmd=c;early=calls=events=responses=expect_child=expect_status=expect_len=expect_id=0;expect_payload=0;for(unsigned i=0;i<24;i++)input[i]=3+7*i;}
static uint32_t run(void){return opencfw_em9305_dispatch_32ef10((uintptr_t)&cmd,(uintptr_t)input);}
int main(void){unsigned count=0;uint16_t commands[]={0x2013,0x2020,0x206d,0x2016,0x41d,0x2021,0x406,0x2022,0x2024,0x2015,0x1405,0xc2d,0x2023,0x202f};unsigned tags[]={4,5,1,2,3,6,7,8,9,0,0,0,0,0};
for(unsigned i=0;i<14;i++){reset(commands[i]);expect_child=tags[i];unsigned event=i==0||i==2||i==3||i==4||i==6;
if(!event){expect_status=tags[i]?0x91:0;expect_len=i==8?1:i==9?8:i==10||i==11?4:i==12?5:i==13?9:3;expect_id=i==8||i==12||i==13?0:id();if(i==11)expect_payload=(uintptr_t)(input+2);}
assert(run()==1&&calls==(tags[i]!=0)&&events==event&&responses==!event);count++;
reset(commands[i]);early=1;assert(run()==1&&calls==0&&events==0&&responses==0);count++;}
for(uint16_t c=0x2013;c<=0x2024;c++){if(c==0x2013||c==0x2015||c==0x2016||(c>=0x2020&&c<=0x2024))continue;reset(c);assert(run()==0&&calls==0&&events==0&&responses==0);count++;}
uint16_t other[]={0,0x2012,0x2025,0xffff};for(unsigned i=0;i<4;i++){reset(other[i]);assert(run()==0&&calls==0&&events==0&&responses==0);count++;}printf("%u\n",count);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'32ef10..32f0a0','scope':'Actual selected C under controlled native child contracts; field and route checks from native reading, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()}
Path(__file__).with_name('legacy-dispatch-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled legacy dispatcher cases')
