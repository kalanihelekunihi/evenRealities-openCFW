#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t);
static unsigned calls,value;static uint32_t flags;
uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t c,uint32_t v){assert(c==0x809000&&v==value);assert(*(volatile uint32_t *)0x80927c==(flags&~(1u<<17)));assert(*(volatile uint32_t *)0x809280==0);calls++;return 0xabcdef;}
int main(void){assert(mmap((void *)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);for(value=0;value<256;value++)for(unsigned set=0;set<2;set++){flags=(0xa5a5a5a5&~(1u<<17))|(set<<17);*(volatile uint32_t *)0x80927c=flags;*(volatile uint32_t *)0x809280=0x1234;*(volatile uint8_t *)0x80900c=value;unsigned old=calls;assert(opencfw_em9305_mode_event_31ac3c(0x809000)==(set?0xabcdef:0x809000));assert(calls==old+set);if(!set)assert(*(volatile uint32_t *)0x809280==0x1234);}puts("PASS512 native gate/clear/tail prefix cases");}
