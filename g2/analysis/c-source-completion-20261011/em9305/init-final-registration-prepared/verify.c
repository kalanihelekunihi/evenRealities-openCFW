#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_lower_308630(uint32_t);
extern uint32_t opencfw_em9305_init_lower_309cb8(uint32_t);
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
void opencfw_em9305_init_callback_325450(void){} void opencfw_em9305_init_callback_325474(void){}
void opencfw_em9305_init_callback_327de0(void){} void opencfw_em9305_init_callback_3280c8(void){}
void opencfw_em9305_init_callback_327dc8(void){} void opencfw_em9305_init_callback_32c254(void){}
void *opencfw_em9305_memset(void *p,int v,unsigned long n){assert(p==(void *)0x8052d4);assert(n==304 && v==0);assert(W(0x802960)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_327de0);assert(W(0x80520c)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3280c8);assert(W(0x8028b0)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_327dc8);assert(W(0x8028a0)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32c254);return memset(p,v,n);}
int main(void){assert(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);
for(unsigned c=0;c<256;c++){memset((void *)0x806060,0xa5,16);B(0x80606c)=c;W(0x805b30)=c*0x1020304u;B(0x805b83)=99;uint32_t old=W(0x805b30);assert(opencfw_em9305_init_lower_308630(0xdead)==(old|(1u<<27)));assert(W(0x805b30)==(old|(1u<<27)));assert(B(0x805b83)==0);assert(W(0x8028a8)==(uint32_t)(uintptr_t)opencfw_em9305_init_callback_325450);assert(B(0x80606c)==(c<=2?c+1:c));for(unsigned i=0;i<3;i++)assert(W(0x806060+i*4)==(c<=2&&i==c?(uint32_t)(uintptr_t)opencfw_em9305_init_callback_325474:0xa5a5a5a5u));memset((void *)0x8052d3,0xa5,306);assert(opencfw_em9305_init_lower_309cb8(c)==0x8052d4);assert(B(0x8052d3)==0xa5&&B(0x805404)==0xa5);for(unsigned i=0;i<304;i++)assert(B(0x8052d4+i)==0);}
puts("PASS 256 registration capacity/state and exact buffer-clear cases");}
