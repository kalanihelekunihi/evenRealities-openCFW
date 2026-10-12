#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_callback_324698(uintptr_t);
static unsigned calls;static uint32_t size;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(calls++==0&&d==(void*)0x820000&&s==0&&n==size);*(uint32_t*)0x810000=0x830000;return d;}
uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t q,uintptr_t n){assert(calls++==1&&q==0x805194&&n==0x830000&&*(uint32_t*)0x810000==n);return 0x456;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805cac=0x830000;for(unsigned n=0;n<256;n++){size=n*257;*(uint16_t*)0x83001a=size;*(uint32_t*)0x810000=0x820000;calls=0;assert(opencfw_em9305_init_callback_324698(0x810000)==0x456&&calls==2&&*(uint32_t*)0x810000==0);}puts("PASS256 zero-source-contract/queue reload paths");}
