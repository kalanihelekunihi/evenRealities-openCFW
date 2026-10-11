from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path('/Users/kalani/Repo/evenRealities-openCFW');p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();start=s.index('/* Native30c2e0..30c33a:');body=s[start:s.index('/* Native306fdc/30731c/307480',start)]
bound=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','(uintptr_t)config_store').replace('(uintptr_t)0x805b18u','(uintptr_t)handler_store')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint8_t config_store[64],handler_store[1];static uint16_t message_store[2];
static uint32_t active,state,flag,fail,step;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4&&step==3);step=4;return fail?0:(uintptr_t)message_store;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==7&&p==(uintptr_t)message_store&&step==4);assert(message_store[0]==2&&message_store[1]==0x1a01);step=5;return 55;}
'''+bound+r'''
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id==2&&step==0);step=1;return active;}
uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t id){assert(id==2&&step==1);step=2;return state;}
uint32_t opencfw_em9305_ll_slot_flag_307480(uint32_t id,uint32_t m){assert(id==2&&m==2&&step==2);step=3;return flag;}
int main(void){config_store[34]=3;handler_store[0]=7;
assert(opencfw_em9305_ll_event_fallback_30c2e0(3)==2&&step==0);assert(opencfw_em9305_ll_event_fallback_30c2e0(65536)==2&&step==0);
assert(opencfw_em9305_ll_event_fallback_30c2e0(2)==2&&step==1);
active=1;step=0;assert(opencfw_em9305_ll_event_fallback_30c2e0(2)==12&&step==2);
state=1;step=0;assert(opencfw_em9305_ll_event_fallback_30c2e0(2)==12&&step==3);
flag=1;fail=1;step=0;assert(opencfw_em9305_ll_event_fallback_30c2e0(2)==0&&step==4);
fail=0;step=0;assert(opencfw_em9305_ll_event_fallback_30c2e0(2)==0&&step==5);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':7,'scope':'Selected C body isolated; configuration pointer and handler fixed addresses bound to host storage; controlled genuine child contracts. Native reading checks only, not runtime equality','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_range':'30c2e0..30c33a','unresolved_children':['30731c','306fdc','307480']}
(root/'g2/analysis/c-source-completion-20261011/em9305/controller-fallback-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS7 controlled C fallback cases')
