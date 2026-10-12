#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_callback_318168(uint32_t);
static uint32_t gate;static unsigned calls;
uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
static uint32_t callback(uintptr_t p,uint32_t z,uintptr_t code,uintptr_t object){assert(p==0x82002c&&z==0&&code==(uintptr_t)callback&&object==0x820000);*(uint32_t*)0x805180=0x820100;*(uint32_t*)0x805cac=0x830100;*(uint8_t*)0x83010d=1;calls++;return 9;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);for(unsigned n=0;n<256;n++){gate=0;calls=0;assert(opencfw_em9305_init_callback_318168(n)==0);gate=1;*(uint32_t*)0x805cac=0x830000;*(uint8_t*)0x83000d=3;*(uint32_t*)0x805180=0x820000;*(uint8_t*)0x805184=1;*(uint8_t*)0x820040=2;*(uint8_t*)0x820140=99;*(uint32_t*)0x805cdc=(uint32_t)(uintptr_t)callback;assert(opencfw_em9305_init_callback_318168(n)==1&&calls==1);assert(*(uint8_t*)0x820040==2&&*(uint8_t*)0x820140==0);*(uint32_t*)0x805cac=0x830000;*(uint8_t*)0x83000d=3;*(uint8_t*)0x805184=0;*(uint8_t*)0x805190=0;*(uint8_t*)0x80519c=0;assert(opencfw_em9305_init_callback_318168(n)==3&&calls==1);}puts("PASS768 stream-gate/null/child mutation paths");}
