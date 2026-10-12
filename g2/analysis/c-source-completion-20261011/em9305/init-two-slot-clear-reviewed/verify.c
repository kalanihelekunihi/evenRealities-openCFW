#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_callback_31810c(uint32_t);
static unsigned calls;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(s==0);unsigned i=calls/2;uintptr_t old=0x820000+i*512,new=old+256;if(!(calls&1)){assert(d==(void*)(old+100)&&n==44);assert(*(uint16_t*)(old+96)==0&&*(uint16_t*)(old+94)==0&&*(uint8_t*)(old+80)==0&&*(uint16_t*)(old+76)==0);*(uint32_t*)(uintptr_t)(0x810000+i*0xb08+0xafc)=new;*(uint32_t*)0x805c38=0;}else assert(d==(void*)(new+82)&&n==12);calls++;return d;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);for(unsigned n=0;n<256;n++){*(uint32_t*)0x805c38=0x810000;for(unsigned i=0;i<2;i++){uintptr_t o=0x820000+i*512;*(uint32_t*)(uintptr_t)(0x810000+i*0xb08+0xafc)=o;*(uint16_t*)(o+96)=n+1;*(uint16_t*)(o+94)=n+2;*(uint8_t*)(o+80)=n;*(uint16_t*)(o+76)=n+3;}calls=0;assert(opencfw_em9305_init_callback_31810c(n)==1&&calls==4);*(uint32_t*)0x805c38=0;calls=0;assert(opencfw_em9305_init_callback_31810c(n)==1&&calls==0);}puts("PASS512 slot mutation/null-base paths");}
