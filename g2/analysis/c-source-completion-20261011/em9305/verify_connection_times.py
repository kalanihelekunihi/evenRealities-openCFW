from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30d3c4..'):s.index('/* Native30b1b0..')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t configuration[40],handler_cell=7;static _Alignas(2) uint8_t message[8];static unsigned id,active,pending,allocation_ok,version,size,timing,active_calls,pending_calls,allocations,sends;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id&&id<3);active_calls++;return active;}
uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t x,uint32_t op){assert(x==id&&op==31);pending_calls++;configuration[4]=version;return pending;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==8);allocations++;return allocation_ok?(uintptr_t)message:0;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==7&&p==(uintptr_t)message&&*(uint16_t *)message==id&&*(uint16_t *)(message+2)==0x1f01&&*(uint16_t *)(message+4)==size&&*(uint16_t *)(message+6)==timing);sends++;return 7;}
"""+body+r"""
static void check(void){configuration[34]=3;configuration[4]=(uint8_t)(version==9?8:9);active_calls=pending_calls=allocations=sends=0;memset(message,0xa5,8);
unsigned valid=id<3&&active,allowed=size>=27&&size<=251&&timing>=328&&timing<=(version<9?2120:17040);unsigned want=!valid?2:pending?12:!allowed?18:0;
assert(opencfw_em9305_ll_connection_times_30d3c4(id,size,timing)==want);assert(active_calls==(id<3)&&pending_calls==valid&&allocations==(valid&&!pending&&allowed)&&sends==(valid&&!pending&&allowed&&allocation_ok));if(!sends)for(unsigned i=0;i<8;i++)assert(message[i]==0xa5);}
int main(void){unsigned cases=0;unsigned times[]={0,327,328,2120,2121,17040,17041,65535},versions[]={0,8,9,255},sizes[]={0,26,27,100,251,252,65535};
id=1;active=1;pending=0;
for(size=0;size<65536;size++){for(unsigned t=0;t<8;t++){for(unsigned v=0;v<4;v++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){timing=times[t];version=versions[v];check();cases++;}}}}
for(id=0;id<5;id++){for(active=0;active<2;active++){for(pending=0;pending<2;pending++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){for(unsigned z=0;z<7;z++){for(unsigned t=0;t<8;t++){for(unsigned v=0;v<4;v++){size=sizes[z];timing=times[t];version=versions[v];check();cases++;}}}}}}}
printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'30d3c4..30d45a','scope':'Actual selected C with normalized config/handler RAM and controlled active/pending/allocator/send; exhaustive16-bit size, timing/version gates, pending-child configuration mutation and complete eight-byte messages; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-times-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connection times cases')
