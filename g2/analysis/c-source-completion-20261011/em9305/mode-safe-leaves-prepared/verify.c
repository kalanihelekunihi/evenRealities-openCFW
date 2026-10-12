#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_event_313338(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32279c(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32c978(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cb40(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cf78(uintptr_t);
static unsigned calls;
uint32_t opencfw_em9305_auxiliary_transition_333a60(void){calls++;return 0x12345678;}
int main(void){assert(mmap((void *)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);
for(unsigned i=0;i<256;i++){*(volatile uint32_t *)0x805f14=0x809010;*(volatile uint8_t *)0x805f04=i;unsigned old=calls;assert(opencfw_em9305_mode_event_313338(0x809011)==0x809011);assert(calls==old);assert(opencfw_em9305_mode_event_32279c(0x809000)==(i==2?2:0x12345678));assert(calls==old+(i!=2));assert(opencfw_em9305_mode_event_32c978(0x809000)==0x809000);assert(*(volatile uint8_t *)0x80900c==62);assert(opencfw_em9305_mode_event_32cadc(0x809000)==0x809000);assert(*(volatile uint8_t *)0x80900c==34);assert(opencfw_em9305_mode_event_32cb40(0x809000)==0x809000);assert(*(volatile uint8_t *)0x80900c==61);assert(opencfw_em9305_mode_event_32cf78(0x809000)==0x809000);assert(*(volatile uint8_t *)0x80900c==255);}puts("PASS 256 connected state/leaf cases");}
