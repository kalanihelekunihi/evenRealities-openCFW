from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();body=s[s.index('/* Native30dd94..'):s.index('extern uint32_t opencfw_em9305_ll_private_mask_apply_308b20')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t configuration[40];static unsigned phase,active,queries,applies,current_id,selector;static uint32_t current_value;
uint32_t opencfw_em9305_wsf_critical_enter(void){assert(phase==0);phase=1;return 7;}
uint32_t opencfw_em9305_wsf_critical_exit(void){assert(phase==1);phase=2;return 9;}
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(phase==1&&id==current_id&&id<configuration[34]);queries++;return active;}
uint32_t opencfw_em9305_ll_signed_pair_apply_309910(uint32_t id,uint32_t value,uint32_t choice){assert(phase==1&&id==current_id&&value==current_value&&choice==selector);applies++;return 0xdeadbeef;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;
for(unsigned v=0;v<256;v++){for(current_id=0;current_id<5;current_id++){for(active=0;active<2;active++){for(selector=0;selector<7;selector++){
 current_value=v&128?v|0xffffff00u:v;phase=queries=applies=0;
 unsigned valid=current_id<3,ok=valid&&active&&selector<5;
 assert(opencfw_em9305_ll_private_signed_pair_30dd94(current_id,current_value,selector)==(!valid||!active?2:selector>=5?18:0));
 assert(phase==2&&queries==valid&&applies==ok);cases++;
}}}}
printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'30dd94..30ddd2','scope':'Actual selected C with fixed RAM normalized and controlled active/apply/critical children; native-reading contract, not native-runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('private-signed-pair-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled private signed pair cases')
