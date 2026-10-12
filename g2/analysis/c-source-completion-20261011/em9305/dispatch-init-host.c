#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
/* Native331ac0..331aea: argument ignored, 28-byte tail clear and ordered masks.
 * R0 at native return is the mask 0x1fff, retained for the caller ABI. */
uint32_t opencfw_em9305_ll_dispatch_initialize(uint32_t ignored)
{
 (void)ignored;
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x805700u,0u,28u);
 *(volatile uint32_t *)(uintptr_t)0x8056f8u=31u;
 *(volatile uint32_t *)(uintptr_t)0x8056e8u=UINT32_MAX;
 *(volatile uint32_t *)(uintptr_t)0x8056fcu=0u;
 *(volatile uint32_t *)(uintptr_t)0x8056f4u=0u;
 *(volatile uint32_t *)(uintptr_t)0x8056f0u=0u;
 *(volatile uint32_t *)(uintptr_t)0x8056ecu=0x1fffu;
 return 0x1fffu;
}

int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;for(unsigned seed=0;seed<256;seed++){memset((void*)0x8056e0,seed,68);uint8_t expected[68];memset(expected,seed,68);memset(expected+32,0,28);uint32_t words[]={0xffffffff,0x1fff,0,0,31,0};memcpy(expected+8,words,24);if(opencfw_em9305_ll_dispatch_initialize(seed)!=0x1fff||memcmp(expected,(void*)0x8056e0,68))abort();}puts("PASS 256 initialization sparse-boundary fixtures");}
