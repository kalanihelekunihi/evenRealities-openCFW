#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_32c828(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_31635c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_3163ac(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_316594(uintptr_t,uintptr_t);
static unsigned calls;
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t c,uint32_t r){assert(c==0x810000&&r==73);calls++;return 0xbeef;}
static uint32_t target(uintptr_t c,uintptr_t code){assert(code==(uintptr_t)target);return (uint32_t)c^0xabc;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint16_t*)0x810106=0xfffe;for(unsigned d=0;d<65536;d++)for(unsigned nonzero=0;nonzero<2;nonzero++){*(uint32_t*)0x802824=d+0xfffe;*(uint32_t*)0x80281c=nonzero;*(uint32_t*)0x802820=0;unsigned prior=calls;uint32_t r=opencfw_em9305_mode_callback_32c828(0x810000,0);unsigned reject=d>=0x7fff||!nonzero;assert(calls==prior+reject&&r==(reject?0xbeef:0x810000));assert(*(uint32_t*)0x8102c4==nonzero&&*(uint32_t*)0x8102c8==0&&*(uint32_t*)0x8102cc==d+0xfffe);}uint32_t (*f[])(uintptr_t,uintptr_t)={opencfw_em9305_mode_callback_31635c,opencfw_em9305_mode_callback_3163ac,opencfw_em9305_mode_callback_316594};uintptr_t slots[]={0x8051f4,0x8052c4,0x8056d8};for(unsigned j=0;j<3;j++)for(unsigned n=0;n<256;n++){*(uint32_t*)slots[j]=0;assert(f[j](n,17)==n);*(uint32_t*)slots[j]=(uint32_t)(uintptr_t)target;assert(f[j](n,17)==(n^0xabc));}puts("PASS132608 anchor and indirect paths");}
