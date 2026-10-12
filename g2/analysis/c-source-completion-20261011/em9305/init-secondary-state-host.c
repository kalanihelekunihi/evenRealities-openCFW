#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,mutate;static uint32_t expected_state,expected_event;
static uint32_t action_check(uintptr_t incoming,uint32_t offset,uint32_t state,uintptr_t self){if(incoming!=self||state!=expected_state||offset!=expected_state*24+expected_event*4)abort();calls++;if(mutate)*(uint8_t*)0x8051a4=3;return 17;}
uint32_t opencfw_em9305_init_secondary_action_318fc0(uintptr_t a,uint32_t b,uint32_t c){return action_check(a,b,c,(uintptr_t)opencfw_em9305_init_secondary_action_318fc0);}
uint32_t opencfw_em9305_init_secondary_action_318fe8(uintptr_t a,uint32_t b,uint32_t c){return action_check(a,b,c,(uintptr_t)opencfw_em9305_init_secondary_action_318fe8);}
uint32_t opencfw_em9305_init_secondary_action_319094(uintptr_t a,uint32_t b,uint32_t c){return action_check(a,b,c,(uintptr_t)opencfw_em9305_init_secondary_action_319094);}
uint32_t opencfw_em9305_init_secondary_action_3190e0(uintptr_t a,uint32_t b,uint32_t c){return action_check(a,b,c,(uintptr_t)opencfw_em9305_init_secondary_action_3190e0);}
#include "init-secondary-state-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
const uint8_t native_transitions[24]={0,1,0,0,0,0,3,1,2,2,0,1,2,2,2,2,2,0,3,3,3,3,0,0};
for(expected_state=0;expected_state<4;expected_state++)for(expected_event=0;expected_event<6;expected_event++)for(mutate=0;mutate<2;mutate++){
memset((void*)0x800000,0,0x10000);*(uint8_t*)0x8051a4=expected_state;*(uint8_t*)0x8051a5=7;*(uint8_t*)0x807003=expected_event;calls=0;
unsigned cut=(expected_state==0&&expected_event==1)||(expected_state==1&&(expected_event==0||expected_event==2||expected_event==3))||(expected_state>=2&&expected_event==5);
unsigned state=cut&&mutate?3:expected_state;uint32_t result=opencfw_em9305_init_registered_31e8fc(0x807000);
if(result!=native_transitions[state*6+expected_event]||*(uint8_t*)0x8051a4!=result||*(uint32_t*)0x805c80!=0x807000||calls!=cut)abort();
if(*(uint8_t*)0x8051a5!=(expected_state==1&&expected_event==4?0:7))abort();
cases++;
}
for(unsigned prior=0;prior<256;prior++){*(uint8_t*)0x8051a5=prior;if(opencfw_em9305_init_secondary_action_319080(0,0,0)!=prior||*(uint8_t*)0x8051a5)abort();
cases++;}
printf("PASS %u isolated secondary-state cases\n",cases);return 0;}
