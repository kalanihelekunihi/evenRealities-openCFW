from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native307044..'):s.index('/* Native30c944..')]
body=body.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;','uintptr_t slots=(uintptr_t)records;').replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t records[5*912];static uint8_t configuration[40],handler_cell=7;static _Alignas(2) uint8_t message[6];static unsigned active,allocation_ok,id,active_calls,allocations,sends;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id&&x<3);active_calls++;return active;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==6);allocations++;return allocation_ok?(uintptr_t)message:0;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){uint8_t want[6]={(uint8_t)id,0,1,0x23,2,0xa5};assert(h==7&&p==(uintptr_t)message&&memcmp(message,want,6)==0);sends++;return 0xdeadbeef;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;
for(id=0;id<5;id++){for(unsigned bit=0;bit<64;bit++){for(active=0;active<2;active++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){
 uint64_t words=1ull<<bit;*(uint32_t *)(records+id*912+544)=(uint32_t)words;*(uint32_t *)(records+id*912+548)=(uint32_t)(words>>32);assert(opencfw_em9305_ll_connection_query_words_307044(id)==words);cases++;
 memset(message,0xa5,6);active_calls=allocations=sends=0;unsigned valid=id<3&&active,feature=bit==26;
 assert(opencfw_em9305_ll_connection_query_30cb28(id)==(!valid?2:!feature?26:0));assert(active_calls==(id<3)&&allocations==(valid&&feature)&&sends==(valid&&feature&&allocation_ok));
 if(sends==0)for(unsigned i=0;i<6;i++)assert(message[i]==0xa5);cases++;
}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['307044..307058','30cb28..30cb7a'],'scope':'Actual connected selected C with normalized configuration/slot/handler RAM and named stride; controlled allocation/active/send children; all64 featureword bits and complete six-byte message including untouched byte5; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-query-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connection query cases')
