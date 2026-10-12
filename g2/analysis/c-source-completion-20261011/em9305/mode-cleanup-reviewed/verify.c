#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_32cf94(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_3269ec(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_323668(uintptr_t,uintptr_t);
static uint32_t slot;static unsigned kind;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){assert(n==3);return slot;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x820000);*(uint32_t*)0x81027c=0xdeadbeef;return 0x555;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t c,uint32_t r){assert(c==0x810000&&r==110);if(kind){assert(*(uint32_t*)0x810280==0);assert((*(uint32_t*)0x81027c&32)==0);}return 0x456;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);for(unsigned n=0;n<256;n++){kind=0;*(uint8_t*)0x80281c=n;*(uint8_t*)0x80281d=173;for(unsigned j=0;j<4;j++)*(uint8_t*)(uintptr_t)(0x810256+j)=99;assert(opencfw_em9305_mode_callback_32cf94(0x810000,0)==0x456);for(unsigned j=0;j<3;j++)assert(*(uint8_t*)(uintptr_t)(0x810256+j)==((n&(1u<<j))?173:99));assert(*(uint8_t*)0x810259==99);kind=1;for(unsigned fail=0;fail<2;fail++){slot=fail?0:0x820000;*(uint32_t*)0x81027c=n|32;*(uint32_t*)0x810280=0xffffffff;*(uint8_t*)0x81025e=n;*(uint8_t*)0x81025f=n+1;assert(opencfw_em9305_mode_callback_3269ec(0x810000,0)==0x456);assert(*(uint32_t*)0x81027c==((fail?(n|32):0xdeadbeef)&~32u));if(!fail)assert(*(uint8_t*)0x820000==25&&*(uint8_t*)0x820001==n&&*(uint8_t*)0x820002==(uint8_t)(n+1));}assert(opencfw_em9305_mode_callback_323668(n,0)==n);}puts("PASS1024 cleanup/loop/pass-through paths");}
