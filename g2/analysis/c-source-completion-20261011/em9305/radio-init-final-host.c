#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls;static uint8_t upper;static uint32_t expectbits;
uint32_t opencfw_em9305_init_features_3099cc(uint32_t v){if(*(uint8_t*)0x805b18!=(uint8_t)v)abort();calls=1;return 0x12345678;}
uint32_t opencfw_em9305_init_features_308ff8(uint32_t v){if(v!=0x12345678||calls!=1)abort();calls++;return 0x87654321;}
static uint32_t opencfw_em9305_ll_signed_bounds_31026c(uintptr_t a,uintptr_t b){if(calls!=2)abort();*(uint8_t*)a=0xf1;*(uint8_t*)b=upper;calls++;return a;}
uint32_t opencfw_em9305_init_event_state_30e0e8(uint32_t v){if(calls!=4||v!=expectbits)abort();calls++;return 0xabcdef;}
static void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){if(calls!=3||p!=(void*)0x805a70||n!=64||v||*(uint32_t*)0x805b30!=expectbits||*(uint32_t*)0x805a70||*(uint8_t*)0x805aa8||*(uint8_t*)0x805a78||*(uint8_t*)0x805a76||*(uint8_t*)0x805a74||*(uint32_t*)0x805b40||*(uint32_t*)0x805b44)abort();calls++;return memset(p,v,n);}
static uint32_t opencfw_em9305_pal_current_time(void);
static uint32_t opencfw_em9305_pal_elapsed_raw(uint32_t,uint32_t);
#include "radio-init-callback-prepared.c"
#include "radio-init-final-prepared.c"
/* Callback isn't entered by this fixture; these imports remain controlled. */
static uint32_t opencfw_em9305_pal_current_time(void){abort();}
static uint32_t opencfw_em9305_pal_elapsed_raw(uint32_t a,uint32_t b){(void)a;(void)b;abort();}
uint32_t opencfw_em9305_init_event_dispatch_306c7c(uint32_t a){(void)a;abort();}
uint32_t opencfw_em9305_init_message_3075cc(uintptr_t a){(void)a;abort();}
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();*(uint32_t*)0x805cac=0x806000;unsigned vectors=0;for(unsigned v=0;v<65536;v++)for(unsigned mode=0;mode<4;mode++){
uint32_t prev=0x20000000u|v;for(unsigned i=0;i<4;i++)*(uint8_t*)(uintptr_t)(0x80603eu+i)=(v>>(i*4))&0xff;upper=(uint8_t[]){19,20,0x80,0x7f}[mode];expectbits=prev|((uint32_t)*(uint8_t*)0x80603e<<8)|((uint32_t)*(uint8_t*)0x80603f<<11)|((uint32_t)*(uint8_t*)0x806040<<9)|((uint32_t)*(uint8_t*)0x806041<<10);if((int8_t)upper>19)expectbits|=1u<<15;memset((void*)0x805a70,0xa5,64);*(uint32_t*)0x805b30=prev;*(uint32_t*)0x805b34=0x87654321;calls=0;if(opencfw_em9305_init_final_30bf6c(v)!=0xabcdef||calls!=5||*(uint32_t*)0x805a94!=expectbits||*(uint32_t*)0x805a98!=0x87654321)abort();vectors++;}printf("PASS %u init final-state source projections; actual state reset C; genuine features/event lower controlled\n",vectors);return 0;}
