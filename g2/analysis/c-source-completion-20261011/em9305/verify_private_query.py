from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native306f44..'):s.index('extern uint32_t opencfw_em9305_ll_signed_pair_apply_309910')]
body=body.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;','uintptr_t slots=(uintptr_t)records;').replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805a96u','feature_flags')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t records[5*912],configuration[40],output[3],feature_flags;
static unsigned phase,active,state,queries,states,current_id,expected_status;
uint32_t opencfw_em9305_wsf_critical_enter(void){assert(phase==0);phase=1;return 7;}
uint32_t opencfw_em9305_wsf_critical_exit(void){assert(phase==1);if(expected_status==0)assert(memcmp(output,records+current_id*912+598,3)==0);else assert(output[0]==0xa5&&output[1]==0xa5&&output[2]==0xa5);phase=2;return 9;}
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(phase==1&&id==current_id&&id<3);queries++;return active;}
uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t id){assert(phase==1&&id==current_id&&(feature_flags&1));states++;return state;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;
for(unsigned v=0;v<256;v++){for(current_id=0;current_id<5;current_id++){for(active=0;active<2;active++){for(state=0;state<3;state++){for(unsigned flags=0;flags<4;flags++){
 feature_flags=flags;for(unsigned i=0;i<3;i++)records[current_id*912+598+i]=(uint8_t)(v+37*i);
 memset(output,0xa5,3);phase=queries=states=0;unsigned valid=current_id<3&&active;
 expected_status=!valid?2:(!(flags&1)||state)?12:0;
 assert(opencfw_em9305_ll_private_query_30bde0(current_id,(uintptr_t)output)==expected_status);
 assert(phase==2&&queries==(current_id<3)&&states==(valid&&(flags&1)));cases++;
}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['306f44..306f6e','30bde0..30be2a'],'scope':'Actual selected C with normalized fixed RAM/MPYUW stride and controlled critical/active/state children; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('private-query-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled private query cases')
