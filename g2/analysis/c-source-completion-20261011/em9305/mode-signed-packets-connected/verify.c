#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_326090(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_3260e4(uintptr_t,uintptr_t);
static uint32_t slot;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){assert(n==2);return slot;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x820000);return 0x456;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805c18=0x830000;*(uint16_t*)0x830000=75;for(unsigned mode=0;mode<3;mode++)for(unsigned local=0;local<256;local++)for(unsigned limit=0;limit<256;limit++)for(unsigned fail=0;fail<2;fail++){*(uint8_t*)0x8102e8=mode;*(uint8_t*)0x8102ea=local;*(uint8_t*)0x805aa8=limit;slot=fail?0:0x820000;int a=(int8_t)local,b=(int8_t)limit;unsigned expected=((mode==0&&a<b)||(mode==1&&b<a))?limit:local;assert(opencfw_em9305_mode_callback_326090(0x810000,0)==(fail?0:0x456));assert(*(uint8_t*)0x8102ea==expected);if(!fail){assert(*(uint8_t*)0x820000==29&&*(uint8_t*)0x820001==(uint8_t)(4+expected));assert(opencfw_em9305_mode_callback_3260e4(0x810000,0)==0x456);assert(*(uint8_t*)0x820000==30&&*(uint8_t*)0x820001==(uint8_t)(4+expected));}}puts("PASS589824 connected signed-clamp/packet paths");}
