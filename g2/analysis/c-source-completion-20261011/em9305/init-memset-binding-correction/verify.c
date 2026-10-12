#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_callback_324698(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_31810c(uint32_t);
static unsigned size;
uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t q,uintptr_t n){assert(q==0x805194&&n==0x820000);for(unsigned j=0;j<size;j++)assert(*(uint8_t*)(n+j)==0);assert(*(uint8_t*)(n+size)==0xa5);return 0x456;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805cac=0x830000;for(unsigned n=0;n<256;n++){size=n;*(uint16_t*)0x83001a=n;*(uint32_t*)0x810000=0x820000;for(unsigned j=0;j<257;j++)*(uint8_t*)(uintptr_t)(0x820000+j)=0xa5;assert(opencfw_em9305_init_callback_324698(0x810000)==0x456&&*(uint32_t*)0x810000==0);*(uint32_t*)0x805c38=0x810000;for(unsigned i=0;i<2;i++){uintptr_t o=0x820000+i*512;*(uint32_t*)(uintptr_t)(0x810000+i*0xb08+0xafc)=o;for(unsigned j=0;j<160;j++)*(uint8_t*)(o+j)=0xa5;}assert(opencfw_em9305_init_callback_31810c(n)==1);for(unsigned i=0;i<2;i++)for(unsigned j=0;j<160;j++){unsigned zero=(j>=76&&j<78)||j==80||(j>=82&&j<98)||(j>=100&&j<144);assert(*(uint8_t*)(uintptr_t)(0x820000+i*512+j)==(zero?0:0xa5));}}puts("PASS512 connected native-zero-fill callback paths");}
