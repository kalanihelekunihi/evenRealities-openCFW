from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path('/Users/kalani/Repo/evenRealities-openCFW');p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();start=s.index('/* Native30e054..30e0d4:');body=s[start:s.index('/* Native3072f0..30730c:',start)]
bound=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','(uintptr_t)config_store').replace('(uintptr_t)0x805b18u','(uintptr_t)handler_store')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint8_t config_store[64],handler_store[1],first[8],second[16];static _Alignas(4) uint8_t packet[30];
static uint32_t pending,callback,active,state,fail,step;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id==2&&step==2);step=3;return active;}
uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t id){assert(id==2&&step==3);step=4;return state;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==30&&step==4);step=5;return fail?0:(uintptr_t)packet;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){if(n==8){assert(step==5&&d==packet+4&&s==first&&*(uint16_t*)packet==2);step=6;}else{assert(n==16&&step==6&&d==packet+14&&s==second&&*(uint16_t*)(packet+12)==0xface);step=7;}return memcpy(d,s,n);}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==7&&p==(uintptr_t)packet&&step==7);assert(*(uint16_t*)(packet+2)==0x1801);assert(memcmp(packet+4,first,8)==0&&memcmp(packet+14,second,16)==0);step=8;return 77;}
'''+bound+r'''
uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t id,uint32_t op){assert(id==2&&op==24&&step==0);step=1;return pending;}
uint32_t opencfw_em9305_ll_slot_callback_3072f0(uint32_t id){assert(id==2&&step==1);step=2;return callback;}
static uint32_t run(void){step=0;return opencfw_em9305_ll_command_30e054(2,(uintptr_t)first,0xface,(uintptr_t)second);}
int main(void){config_store[34]=3;handler_store[0]=7;for(unsigned i=0;i<8;i++)first[i]=i+9;for(unsigned i=0;i<16;i++)second[i]=i+33;
pending=1;assert(run()==12&&step==1);pending=0;callback=1;assert(run()==12&&step==2);callback=0;
config_store[34]=2;assert(run()==2&&step==2);config_store[34]=3;assert(run()==2&&step==3);active=1;state=1;assert(run()==12&&step==4);state=0;fail=1;assert(run()==0&&step==5);fail=0;assert(run()==0&&step==8);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':7,'scope':'Actual selected C body isolated with fixed-address host bindings and controlled genuine child contracts; native-reading checks only, not native runtime equality','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_range':'30e054..30e0d4','unresolved_children':['307434','3072f0']}
(root/'g2/analysis/c-source-completion-20261011/em9305/command-controller-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS7 controlled C controller-command cases')
