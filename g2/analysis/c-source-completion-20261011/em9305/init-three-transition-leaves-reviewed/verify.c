#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_transition_3249ac(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_3249b8(uintptr_t);
extern uintptr_t opencfw_em9305_init_transition_refresh_327dbc(void);
uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t p){assert(p==0x810030&&*(uint8_t*)0x810002==1);return 0x456;}
uint32_t opencfw_em9305_init_secondary_cleanup_321450(uintptr_t p){assert(p==0x810000);return 0x789;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);for(unsigned n=0;n<256;n++){*(uint8_t*)0x810002=n;assert(opencfw_em9305_init_transition_3249ac(0x810000)==0x456);assert(opencfw_em9305_init_transition_3249b8(0x810000)==0x789);*(uint32_t*)0x805398=0x12340000|n;assert(opencfw_em9305_init_transition_refresh_327dbc()==0x805398&&*(uint32_t*)0x805398==0);}puts("PASS768 transition leaf paths");}
