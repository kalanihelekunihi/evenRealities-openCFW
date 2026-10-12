#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_325b14(uintptr_t,uintptr_t);
static uint32_t slot;static unsigned timing;
uint32_t opencfw_em9305_test_mpywhl(uint32_t f,uint32_t p){assert(f==0x30d40);return p*17;}
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){assert(n==4);return slot;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x820000);*(uint8_t*)0x830004=1;return 7;}
uint32_t opencfw_em9305_pal_current_time(void){assert(*(uint32_t*)0x8100ec==*(uint8_t*)0x830005*17u);*(uint32_t*)0x8100ec=99;*(uint32_t*)0x81027c=0x12345;timing++;return 1000;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t c,uint32_t r){assert(c==0x810000&&r==110);return 0x456;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805c6c=0x830000;*(uint32_t*)0x8103a0=0xaaaa;*(uint32_t*)0x8103b0=0xbbbb;for(unsigned n=0;n<256;n++)for(unsigned fail=0;fail<2;fail++){*(uint8_t*)0x810002=0;slot=fail?0:0x820000;*(uint8_t*)0x830004=0;*(uint8_t*)0x830005=n;*(uint8_t*)0x830006=n+1;assert(opencfw_em9305_mode_callback_325b14(0x810000,0)==0x456);assert(*(uint32_t*)0x8100e8==901&&*(uint32_t*)0x8100ec==99);assert(*(uint32_t*)0x81027c==(0x12345&~256u));assert(*(uint8_t*)0x810235==!fail);if(!fail)assert(*(uint8_t*)0x820000==40&&*(uint8_t*)0x820001==0&&*(uint8_t*)0x820002==n&&*(uint8_t*)0x820003==(uint8_t)(n+1));}assert(timing==512);for(unsigned n=1;n<256;n++){*(uint8_t*)0x810002=n;*(uint32_t*)0x81027c=0xffffffff;*(uint32_t*)0x810280=77;assert(opencfw_em9305_mode_callback_325b14(0x810000,0)==0x456);assert(*(uint32_t*)0x81027c==0xfffffeff&&*(uint32_t*)0x810280==0);}assert(*(uint32_t*)0x8103a0==0xaaaa&&*(uint32_t*)0x8103b0==0xbbbb);puts("PASS767 timer-product paths with host multiply model");}
