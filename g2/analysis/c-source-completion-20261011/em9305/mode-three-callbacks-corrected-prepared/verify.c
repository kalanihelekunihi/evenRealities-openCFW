#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_mode_callback_32cde0(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325f0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325f50(uintptr_t,uintptr_t);
static unsigned mode,fail,kind,calls;static uint32_t low,high,cword;
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define H(a) (*(volatile uint16_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_mode_callback_child_317ea4(uintptr_t c){assert(c==0x7b&&B(0x810000+552)==0x7b);calls++;return 0x12345;}
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){assert(n==9);B(0x810002)=mode;W(0x805a94)=low;W(0x805a98)=high;W(0x810220)=cword;return fail?0:0x820000;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x820000);assert(B(p)==(kind==0?(mode==0?8:14):9));uint32_t l=kind==0?(low&0xf787cf2f):((cword&0xcf2f)|(low&0xf7870000));uint32_t h=high&0x1bef;for(unsigned i=0;i<4;i++){assert(B(p+1+i)==((l>>(8*i))&255));assert(B(p+5+i)==((h>>(8*i))&255));}calls++;return 0x2468;}
int main(void){assert(mmap((void *)0x800000,0x30000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);for(mode=0;mode<256;mode++){B(0x810002)=mode;B(0x80281c)=0x7b;H(0x8100c8)=0xa5a5;H(0x810190)=0x55aa;unsigned old=calls;assert(opencfw_em9305_mode_callback_32cde0(0x810000,0)==(mode==1?0x12345:0x7b));assert(H(0x8100c8)==(mode==1?0x2345:0xa5a5));assert(H(0x810190)==0x55aa);assert(calls==old+(mode==1));low=0x1020304u*mode;high=~low;cword=low^0xaabbccdd;for(fail=0;fail<2;fail++)for(kind=0;kind<2;kind++){memset((void *)0x820000,0xa5,10);old=calls;uint32_t r=kind==0?opencfw_em9305_mode_callback_325f0c(0x810000,0):opencfw_em9305_mode_callback_325f50(0x810000,0);assert(r==(fail?0:0x2468)&&calls==old+!fail);assert(B(0x820009)==0xa5);}}puts("PASS1280 state/allocator/mode paths with actual selected serializer");}
