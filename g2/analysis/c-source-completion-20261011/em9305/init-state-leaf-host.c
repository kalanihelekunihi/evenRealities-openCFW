#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned calls;
static uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t object){if(object!=0x803c2c||*(uint8_t *)(uintptr_t)0x803c29!=1)abort();calls++;return 98;}
#include "init-state-leaf-prepared.c"
int main(void){if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)0x800000)abort();unsigned cases=0;
for(unsigned value=0;value<256;value++)for(unsigned prior=0;prior<2;prior++){
 *(uint8_t *)(uintptr_t)0x805a74=value;*(uint8_t *)(uintptr_t)0x803c29=prior?127:0;calls=0;
 uint32_t result=opencfw_em9305_init_state_action_31b6b0(0xdeadbeef,0x12345678);
 if(result!=(value?98:0)||calls!=(value?1u:0u)||*(uint8_t *)(uintptr_t)0x803c29!=(value?1:prior?127:0))abort();
 cases++;
}printf("PASS %u trigger leaf cases\n",cases);return 0;}
