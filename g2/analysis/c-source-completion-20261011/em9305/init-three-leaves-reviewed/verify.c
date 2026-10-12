#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_registered_32182c(uint32_t);
extern uint32_t opencfw_em9305_init_registered_3266f8(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_32468c(uint32_t);
static unsigned calls;
uint32_t opencfw_em9305_common_init_303650(uint32_t x){return x^0xabcdef;}
uintptr_t opencfw_em9305_wsf_queue_remove(uintptr_t q){assert(q==0x805194);return 0x12345;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t c,uint32_t r){assert(c==0x810000&&r==110&&*(uint8_t*)0x810260==1&&*(uint32_t*)0x810280==0);calls++;return 0x456;}
int main(void){assert(mmap((void*)0x810000,4096,3,0x32,-1,0)==(void*)0x810000);for(unsigned n=0;n<256;n++){assert(opencfw_em9305_init_registered_32182c(n)==(n^0xabcdef));assert(opencfw_em9305_init_callback_32468c(n)==0x12345);*(uint8_t*)0x810260=n;*(uint32_t*)0x81027c=0xffff0000|n;*(uint32_t*)0x810280=99;unsigned old=calls;assert(opencfw_em9305_init_registered_3266f8(0x810000)==(n?0x810000:0x456));assert(calls==old+!n);assert(*(uint32_t*)0x81027c==(n?(0xffff0000|n):0xffff0000));if(n)assert(*(uint32_t*)0x810280==99);}puts("PASS768 three registered/callback leaf paths");}
