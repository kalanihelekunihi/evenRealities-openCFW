from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native3073ec..'):s.index('/* Native3072e0..')]
body=body.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;','uintptr_t slots=(uintptr_t)records;').replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t records[5*912];static uint8_t configuration[40],handler_cell=7;static _Alignas(2) uint8_t message[4];static unsigned id,active,pending,allocation_ok,live,kind,active_calls,pending_calls,allocations,sends;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id);active_calls++;return active;}
uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t x,uint32_t op){assert(x==id&&op==(kind?28:27));pending_calls++;return pending;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4);allocations++;return allocation_ok?(uintptr_t)message:0;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==7&&p==(uintptr_t)message&&*(uint16_t *)message==id&&*(uint16_t *)(message+2)==(kind?0x1c01:0x1b01));sends++;return 0xdeadbeef;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;
for(id=0;id<5;id++){for(active=0;active<2;active++){for(pending=0;pending<2;pending++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){for(live=0;live<2;live++){for(unsigned byte=0;byte<256;byte++){for(kind=0;kind<2;kind++){
 memset(records,0xa5,sizeof records);uint8_t *r=records+id*912;r[0]=live;uint32_t word=0xc57b1200u|byte;*(uint32_t *)(r+636)=word;assert(opencfw_em9305_ll_connection_read_ready_3073ec(id)==(live&&((byte&4)!=0)));cases++;
 memset(message,0xa5,4);active_calls=pending_calls=allocations=sends=0;unsigned valid=id<3&&active,ready=live&&(byte&4);
 unsigned want=kind?(!valid?2:pending?12:0):pending?(!active||!ready?12:0):(!valid?2:0);
 unsigned result=kind?opencfw_em9305_ll_connection_action_30c8c8(id):opencfw_em9305_ll_connection_read_30c860(id);
 assert(result==want);assert(active_calls==(!kind&&pending?1:id<3));assert(pending_calls==(kind?valid:1));unsigned allocate=valid&&!pending;assert(allocations==allocate&&sends==(allocate&&allocation_ok));assert(*(uint32_t *)(r+636)==word);if(!sends)for(unsigned i=0;i<4;i++)assert(message[i]==0xa5);cases++;
 assert(opencfw_em9305_ll_connection_read_mark_309030(id)==(uint32_t)(uintptr_t)r&&*(uint32_t *)(r+636)==(word|4));cases++;
}}}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['3073ec..30740e','309030..309046','30c860..30c8c6','30c8c8..30c916'],'scope':'Actual connected selected C with normalized slot/config/handler RAM and stride; controlled pending/active/allocator/send; exhaustive byte636, full-word preservation and pending-before-max boundary; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-read-action-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connection read/action cases')
