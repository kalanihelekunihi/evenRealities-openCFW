from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30b1b0..'):s.index('/* Native32f70c..')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805a94u','feature_flags').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t configuration[40],feature_flags,handler_cell,controls[12];static _Alignas(2) uint8_t message[16];static unsigned id,active,pending,state,allocation_ok,status,active_calls,pending_calls,state_calls,validations,allocations,copies,sends;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id&&id<3);active_calls++;return active;}
uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t x,uint32_t op){assert(x==id&&op==21);pending_calls++;return pending;}
uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t x){assert(x==id);state_calls++;return state;}
uint32_t opencfw_em9305_ll_connection_parameters_validate_30a6b4(uintptr_t p){assert(p==(uintptr_t)controls);validations++;return status;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==16);allocations++;return allocation_ok?(uintptr_t)message:0;}
void *opencfw_em9305_memcpy(void *a,const void *b,uint32_t n){assert(a==message+4&&b==controls&&n==12&&*(uint16_t *)message==id&&*(uint16_t *)(message+2)==0x1501);copies++;handler_cell=9;return memcpy(a,b,n);}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==9&&p==(uintptr_t)message&&memcmp(message+4,controls,12)==0);sends++;return 7;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;unsigned statuses[]={0,18,0x12345678};
for(id=0;id<5;id++){for(active=0;active<2;active++){for(pending=0;pending<2;pending++){for(state=0;state<3;state++){for(unsigned f=0;f<4;f++){for(unsigned si=0;si<3;si++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){for(unsigned byte=0;byte<256;byte++){
 feature_flags=f;status=statuses[si];handler_cell=7;for(unsigned i=0;i<12;i++)controls[i]=(uint8_t)(byte+17*i);memset(message,0xa5,16);active_calls=pending_calls=state_calls=validations=allocations=copies=sends=0;
 unsigned valid=id<3&&active,ready=valid&&!pending&&(state!=1||(f&2));unsigned want=!valid?2:!ready?12:status;
 assert(opencfw_em9305_ll_connection_parameters_30b1b0(id,(uintptr_t)controls)==want);
 assert(active_calls==(id<3)&&pending_calls==valid&&state_calls==(valid&&!pending)&&validations==ready&&allocations==(ready&&status==0)&&copies==(ready&&status==0&&allocation_ok)&&sends==copies);
 if(!sends)for(unsigned i=0;i<16;i++)assert(message[i]==0xa5);cases++;
}}}}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'30b1b0..30b22c','scope':'Actual selected C with normalized product/handler RAM; controlled slot/pending/state/validator/allocation/send; every feature byte gate combination sampled, full controls copy/status propagation and handler-after-copy ordering; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-legacy-parameters-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled legacy connection parameter cases')
