#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_init_phy_state_321150(uintptr_t a,uint32_t b){(void)a;(void)b;abort();}
uint32_t opencfw_em9305_init_slave_phy_state_32b04c(uintptr_t a,uint32_t b){(void)a;(void)b;abort();}
#include "radio-init-registration-prepared.c"
int main(void){uint8_t record[640]={0};unsigned vectors=0;for(unsigned a=0;a<256;a++)for(unsigned b=0;b<256;b++){record[635]=a;record[625]=b;if(opencfw_em9305_init_slave_phy_predicate_329534((uintptr_t)record)!=(a==21&&(b==1||b==2)))abort();vectors++;}if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();if(opencfw_em9305_init_lower_307d64(0xabcdef)!=0x803d38||*(uint32_t*)0x803d38!=(uint32_t)(uintptr_t)&opencfw_em9305_init_phy_state_321150||opencfw_em9305_init_lower_30a37c(0xabcdef)!=0x8056ac||*(uint32_t*)0x805688!=(uint32_t)(uintptr_t)&opencfw_em9305_init_slave_phy_predicate_329534||*(uint32_t*)0x8056ac!=(uint32_t)(uintptr_t)&opencfw_em9305_init_slave_phy_state_32b04c)abort();vectors++;printf("PASS %u predicate/source-function registration projections; imported state machines not invoked\n",vectors);return 0;}
