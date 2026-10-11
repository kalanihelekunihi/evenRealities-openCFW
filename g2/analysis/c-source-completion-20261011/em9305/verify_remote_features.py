from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();a=s.index('/* Native306ebc..');body=s[a:s.index('extern uint32_t opencfw_em9305_ll_private_mask_',a)]
body=body.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;','uintptr_t slots=(uintptr_t)records;').replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t records[4*912],configuration[40],output[7],expected[7];static unsigned phase,active;
uint32_t opencfw_em9305_wsf_critical_enter(void){assert(phase==0);phase=1;return 7;}
uint32_t opencfw_em9305_wsf_critical_exit(void){assert(phase==1&&memcmp(output,expected,7)==0);phase=2;return 9;}
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(phase==1&&id<3);return active;}
'''+body+r'''
int main(void){unsigned cases=0;configuration[34]=3;for(unsigned n=0;n<256;n++){uint32_t low=0x01020304u*n,high=0x12345600u|n;for(unsigned id=0;id<4;id++){*(uint32_t*)(records+id*912+276)=low;*(uint32_t*)(records+id*912+280)=high;assert(opencfw_em9305_ll_connection_feature_words_306ebc(id)==(((uint64_t)high<<32)|low));cases++;}
for(unsigned id=0;id<5;id++)for(active=0;active<2;active++){unsigned ok=id<3&&active;phase=0;memset(output,0xa5,7);memset(expected,0xa5,7);if(ok){for(unsigned i=0;i<4;i++)expected[i+1]=low>>(8*i);expected[5]=high;}assert(opencfw_em9305_ll_connection_remote_features_30bbbc(id,(uintptr_t)(output+1))==(ok?0:2));assert(phase==2);cases++;}}printf("%u\n",cases);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['306ebc..306ed4','30bbbc..30bc04'],'scope':'Actual selected C with bounded named stride and RAM normalized, controlled active/critical contracts; native-reading tests, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('remote-features-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled remote feature cases')
