from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native3072e0..'):s.index('/* Native30d3c4..')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x8027e8u','active_callback').replace('*(volatile uint32_t *)(uintptr_t)0x8027ecu','pending_callback').replace('*(volatile uint32_t *)(uintptr_t)0x8028bcu','lookup_callback').replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t configuration[56],handler_cell;static uintptr_t active_callback,pending_callback,lookup_callback;static _Alignas(2) uint8_t message[8];
static unsigned id,reason,active,extra_active,extra_pending,lookup,allocation_ok,new_primary,active_calls,pending_calls,lookup_calls,allocations,sends,bytes;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id&&id<3);active_calls++;configuration[34]=new_primary;return active;}
static uint32_t extra_a(uint32_t x){assert(x==id&&id>=3);active_calls++;configuration[34]=new_primary;return extra_active==2?0x1234:0;}
static uint32_t extra_p(uint32_t x){assert(x==id&&id>=3);pending_calls++;return extra_pending==2?9:0;}
static uint32_t extra_l(uint32_t x){assert(x==id&&id>=3);lookup_calls++;handler_cell=9;return 0x12345678;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){allocations++;bytes=n;return allocation_ok?(uintptr_t)message:0;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(p==(uintptr_t)message);unsigned ready=id<3?active:extra_active==2;unsigned type=!ready?0x2701:id<configuration[34]?0x1701:0x170f;unsigned identity=!ready?(lookup?0x5678:0xffff):id;assert(*(uint16_t *)message==identity&&*(uint16_t *)(message+2)==type&&message[4]==reason&&message[5]==0xa5);if(type!=0x170f)assert(*(uint16_t *)(message+6)==id);else assert(message[6]==0xa5&&message[7]==0xa5);assert(h==(!ready&&lookup?9:7));sends++;return 7;}
"""+body+r"""
int main(void){unsigned cases=0;unsigned primaries[]={1,3,5};
for(id=0;id<6;id++){for(active=0;active<2;active++){for(extra_active=0;extra_active<3;extra_active++){for(extra_pending=0;extra_pending<3;extra_pending++){for(lookup=0;lookup<2;lookup++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){for(unsigned pi=0;pi<3;pi++){for(reason=0;reason<256;reason++){
 new_primary=primaries[pi];configuration[34]=3;configuration[53]=2;handler_cell=7;active_callback=extra_active?(uintptr_t)extra_a:0;pending_callback=extra_pending?(uintptr_t)extra_p:0;lookup_callback=lookup?(uintptr_t)extra_l:0;active_calls=pending_calls=lookup_calls=allocations=sends=bytes=0;memset(message,0xa5,8);
 unsigned ready=id<3?active:extra_active==2;unsigned fallback=id>=3&&id<5&&!ready;unsigned allowed=id<5&&(id<3?active:ready||extra_pending==2);
 unsigned want=id>=5||(id<3&&!active)?2:!allowed?12:0;
 assert(opencfw_em9305_ll_connection_disconnect_30b570(id,reason)==want);
 assert(active_calls==(id<5&&(id<3||extra_active!=0))&&pending_calls==(fallback&&extra_pending!=0)&&allocations==allowed&&sends==(allowed&&allocation_ok)&&lookup_calls==(fallback&&allowed&&allocation_ok&&lookup));
 if(allowed)assert(bytes==(fallback?8:id<configuration[34]?8:6));if(!sends)for(unsigned i=0;i<8;i++)assert(message[i]==0xa5);cases++;
}}}}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['3072e0..3072ee','30730c..30731a','306e54..306e66','30b570..30b620'],'scope':'Actual connected selected C with normalized callback/config/handler RAM; controlled allocation/send; exhaustive reason byte, optional callbacks, configuration mutation/reload and complete message/untouched bytes; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-disconnect-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connection disconnect cases')
