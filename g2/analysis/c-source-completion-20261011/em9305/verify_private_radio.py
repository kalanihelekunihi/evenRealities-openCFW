from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30d8fc..'):s.index('/* Native30e38c..')]
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x805a96u','feature_flags').replace('*(volatile uint8_t *)(uintptr_t)(0x805aa9u+index)','gain_cells[index]').replace('*(volatile uint8_t *)(uintptr_t)(0x805aacu+index)','channel_cells[index]').replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t configuration[40],feature_flags,handler_cell=7,gain_cells[3],channel_cells[3];static _Alignas(2) uint8_t messages[3][6];
static unsigned variant,current,allocations,sends,active_calls,mask,channel,gain;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id<configuration[34]);current=id;active_calls++;return variant!=1;}
uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t id){assert(id==current);return variant==2?0:1;}
uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t id,uint32_t op){assert(id==current&&op==33);return variant==3&&id==1;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==6);allocations++;return variant==4&&current==1?0:(uintptr_t)messages[current];}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==7&&p==(uintptr_t)messages[current]);uint8_t expected[6]={(uint8_t)current,0,1,0x21,(uint8_t)mask,(uint8_t)channel};assert(memcmp((void *)p,expected,6)==0);sends++;return 0xdeadbeef;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;
for(mask=0;mask<9;mask++){for(channel=0;channel<256;channel++){for(unsigned f=0;f<2;f++){for(variant=0;variant<5;variant++){for(unsigned g=0;g<3;g++){
 gain=g==0?0:g==1?0xffffff80u:0xffffffffu;feature_flags=f;memset(gain_cells,0xa5,3);memset(channel_cells,0xa5,3);memset(messages,0xa5,sizeof messages);allocations=sends=active_calls=0;
 unsigned valid=mask>=1&&mask<=7&&channel>=2&&channel<=37;unsigned want=!f?12:!valid?18:variant==3?12:0;
 assert(opencfw_em9305_ll_private_radio_30d8fc(mask,gain,channel)==want);
 for(unsigned i=0;i<3;i++){unsigned written=f&&valid&&(mask&(1u<<i));assert(gain_cells[i]==(written?(uint8_t)gain:0xa5)&&channel_cells[i]==(written?channel:0xa5));}
 if(!f||!valid)assert(active_calls==0&&allocations==0&&sends==0);
 else if(variant==1||variant==2)assert(active_calls==3&&allocations==0&&sends==0);
 else if(variant==3)assert(active_calls==2&&allocations==1&&sends==1);
 else assert(active_calls==3&&allocations==3&&sends==(variant==4?2:3));cases++;
}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'30d8fc..30d9b0','scope':'Actual selected C with normalized live RAM and controlled active/state/pending/allocation/send children; all byte channel values, mask bounds, gain truncation, gate statuses and complete six-byte messages; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('private-radio-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled private radio cases')
