from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native31bb20..'):s.index('/* Native31b918..')]
body=body.replace('*(volatile uint32_t *)(descriptor+16u)','slot_pointer').replace('*(volatile uint32_t *)(uintptr_t)0x805cb0u','active_slot')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t descriptor[36],request_data[8],old_slot,new_slot;static uintptr_t slot_pointer;static uint32_t active_slot;static unsigned role,mutation,actions,schedules;
static void action(uintptr_t d,unsigned which){assert(d==(uintptr_t)descriptor&&which==role);assert(active_slot==(role?1234:(uint32_t)(uintptr_t)&old_slot));actions++;if(mutation==1)request_data[3]=255;if(mutation==2)slot_pointer=(uintptr_t)&new_slot;if(mutation==3)request_data[3]=17;}
uint32_t opencfw_em9305_ll_test_action_31b7e4(uintptr_t d){action(d,0);return 99;}
uint32_t opencfw_em9305_ll_test_action_31b8a8(uintptr_t d){action(d,1);return 99;}
static uint32_t schedule(uintptr_t d,uintptr_t r,unsigned which){assert(d==(uintptr_t)descriptor&&r==(uintptr_t)request_data&&which==role);assert(*(uint8_t*)slot_pointer==request_data[3]);assert(active_slot==(role?1234:0));schedules++;return 0xabc0+role;}
uint32_t opencfw_em9305_ll_test_schedule_first_31b7fc(uintptr_t d,uintptr_t r,uint32_t context){assert(context==0x87654321);return schedule(d,r,0);}
uint32_t opencfw_em9305_ll_test_schedule_second_31b918(uintptr_t d,uintptr_t r){return schedule(d,r,1);}
'''+body+r'''
int main(void){unsigned cases=0;for(unsigned r=0;r<4;r++){role=r<3?r:255;for(unsigned marker=0;marker<256;marker++){for(unsigned parameter=0;parameter<256;parameter++){for(mutation=0;mutation<4;mutation++){
 old_slot=marker;new_slot=42;slot_pointer=(uintptr_t)&old_slot;request_data[2]=role;request_data[3]=parameter;active_slot=1234;actions=schedules=0;
 unsigned runs=role<=1&&marker==255&&parameter!=255;unsigned schedules_expected=runs&&mutation!=1;unsigned expected=role>1?0:marker!=255?12:parameter==255?0:mutation==1?0:0xabc0+role;
 assert(opencfw_em9305_ll_test_submit_31bb20((uintptr_t)descriptor,(uintptr_t)request_data,0x87654321)==expected&&actions==runs&&schedules==schedules_expected);
 unsigned final_marker=runs?(mutation==1?255:mutation==3?17:parameter):marker;
 assert(old_slot==(runs&&mutation==2?marker:final_marker)&&new_slot==(runs&&mutation==2?final_marker:42));assert(active_slot==(runs&&role==0?0:1234));cases++;
}}}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-submit-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C submit body with normalized descriptor pointer/active slot; controlled action and scheduling children. Full marker/parameter bytes, roles0/1/2/255, callback mutation of marker and descriptor slot; checks native reloads, global lifetime, scheduling argument/context and nonzero return. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
