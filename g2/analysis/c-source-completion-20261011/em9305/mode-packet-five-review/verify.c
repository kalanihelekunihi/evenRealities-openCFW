#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_326a64(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_326aa8(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325dec(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325df4(uintptr_t,uintptr_t);
static uint32_t slot;static unsigned calls,rejects;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){assert(n==2||n==6||n==9);if(n==6)assert(*(uint8_t*)(uintptr_t)0x81020d==1);calls++;*(uint8_t*)(uintptr_t)0x81000c=199;return slot;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x820000);return 0x2468;}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t c,uint32_t r,uint32_t z){assert(c==0x810000&&r==36&&z==0);rejects++;return 0xface;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805cac=0x830000;for(unsigned n=0;n<256;n++){for(unsigned fail=0;fail<2;fail++){slot=fail?0:0x820000;*(uint8_t*)(uintptr_t)0x81000c=n;assert(opencfw_em9305_mode_callback_326a64(0x810000,0)==(fail?0:0x2468));if(!fail){assert(*(uint8_t*)(uintptr_t)slot==2&&*(uint8_t*)(uintptr_t)(slot+1)==199);}*(uint8_t*)(uintptr_t)0x81020d=0;for(unsigned j=0;j<5;j++)*(uint8_t*)(uintptr_t)(0x830000+j)=n+j;assert(opencfw_em9305_mode_callback_326aa8(0x810000,0)==(fail?0:0x2468));assert(*(uint8_t*)(uintptr_t)0x81020d==1);if(!fail){unsigned idx[]={4,0,1,2,3};assert(*(uint8_t*)(uintptr_t)slot==12);for(unsigned j=0;j<5;j++)assert(*(uint8_t*)(uintptr_t)(slot+1+j)==(uint8_t)(n+idx[j]));}}*(uint8_t*)(uintptr_t)0x81020d=1;unsigned old=calls;assert(opencfw_em9305_mode_callback_326aa8(0x810000,0)==0xface);assert(calls==old);}assert(rejects==256);slot=0x820000;
for(unsigned flags=0;flags<2;flags++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned modes=0;modes<4;modes++)for(unsigned k=0;k<256;k++){
uint16_t lower=k*31u,upper=k*23u;*(uint16_t*)0x810238=lower;*(uint16_t*)0x81023c=upper;*(uint8_t*)(uintptr_t)0x810216=enabled;*(uint8_t*)(uintptr_t)0x810221=flags?8:0;*(uint8_t*)(uintptr_t)0x81004d=(modes&1)?3:0;*(uint8_t*)(uintptr_t)0x81004c=(modes&2)?3:0;
uint16_t lo=lower,hi=upper;if(enabled&&flags){if((modes&1)&&lo<0xa90)lo=0xa90;if((modes&2)&&hi<0xa90)hi=0xa90;}else{if(lo>0x848)lo=0x848;if(hi>0x848)hi=0x848;}
assert(opencfw_em9305_mode_callback_325dec(0x810000,0)==0x2468);assert(*(uint8_t*)(uintptr_t)slot==20);assert(*(uint16_t*)0x820003==lo&&*(uint16_t*)0x820007==hi);
assert(opencfw_em9305_mode_callback_325df4(0x810000,0)==0x2468);assert(*(uint8_t*)(uintptr_t)slot==21);assert(*(uint16_t*)0x820003==lo&&*(uint16_t*)0x820007==hi);
}
puts("PASS9472 short and clamped packet paths");}
