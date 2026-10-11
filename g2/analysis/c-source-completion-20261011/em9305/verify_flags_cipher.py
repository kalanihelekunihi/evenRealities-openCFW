from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path('/Users/kalani/Repo/evenRealities-openCFW');p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();a=s.index('/* Native30b644..30b654:');body=s[a:s.index('/* Native317c10..317c40:',a)]
bound=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','(uintptr_t)config_store').replace('*(volatile uint32_t *)(uintptr_t)0x805c70u','(uintptr_t)slots_store')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint8_t config_store[64];static _Alignas(4) uint8_t slots_store[912];static uint32_t active,called;
uint32_t opencfw_em9305_slot_offset(uint32_t id){assert(id==2);return 0;}
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id==2);return active;}
uint32_t opencfw_em9305_radio_cipher_30ff0c(uintptr_t a,uintptr_t b,uintptr_t c){assert(a==123&&b==456&&c==456);called++;return 71;}
'''+bound+r'''
int main(void){uint8_t flags[2];uint8_t lows[]={0,1,127,255};uint8_t highs[]={0,1,128,255};
for(unsigned i=0;i<4;i++)for(unsigned j=0;j<4;j++){memset(slots_store,0x55,sizeof slots_store);slots_store[514]=0;flags[0]=lows[i];flags[1]=highs[j];assert(opencfw_em9305_ll_slot_flags_apply_308b74(2,(uintptr_t)flags)==1);assert(slots_store[512]==flags[0]&&slots_store[513]==flags[1]&&slots_store[514]==1&&slots_store[515]==0x55);}
slots_store[514]=1;slots_store[512]=0x45;slots_store[513]=0x67;assert(opencfw_em9305_ll_slot_flags_apply_308b74(2,0)==0&&slots_store[512]==0x45&&slots_store[513]==0x67);slots_store[514]=255;assert(opencfw_em9305_ll_slot_flags_apply_308b74(2,0)==0&&slots_store[514]==255);
config_store[34]=2;assert(opencfw_em9305_ll_flags_command_30d54c(2,0)==2);config_store[34]=3;assert(opencfw_em9305_ll_flags_command_30d54c(2,0)==2);active=1;assert(opencfw_em9305_ll_flags_command_30d54c(2,0)==12);slots_store[514]=0;flags[0]=1;flags[1]=0;assert(opencfw_em9305_ll_flags_command_30d54c(2,(uintptr_t)flags)==0&&slots_store[512]==1&&slots_store[513]==0);assert(opencfw_em9305_ll_data_command_30b644(123,456)==0&&called==1);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':23,'scope':'Actual selected C isolated with fixed-address host binding and controlled slot-offset/active/cipher children; source-reading contract proof, not ISA/runtime equivalence','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_ranges':['30b644..30b654','30d54c..30d580','308b74..308ba8']}
(root/'g2/analysis/c-source-completion-20261011/em9305/flags-cipher-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS23 controlled C flag/cipher cases')
