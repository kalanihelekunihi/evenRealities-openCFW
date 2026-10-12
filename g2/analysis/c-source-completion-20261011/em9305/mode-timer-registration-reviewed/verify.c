#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_32c884(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_registered_32ce04(uintptr_t);
static unsigned ticks,mults;
uint32_t opencfw_em9305_test_mpywhl(uint32_t f,uint32_t v){assert(f==0x30d40);mults++;return v*123+7;}
uint32_t opencfw_em9305_pal_current_time(void){return ++ticks;}
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t c,uint32_t r,uint32_t z){assert(c==0x810000&&r==30&&z==1);return 0xbeef;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t c,uint32_t r){assert(c==0x810000&&r==110);assert(*(uint32_t*)0x810280==0&&*(uint32_t*)0x81027c==0xfeff);return 0xface;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint8_t*)0x810002=1;for(unsigned dir=0;dir<2;dir++)for(unsigned lo=0;lo<256;lo++)for(unsigned hi=0;hi<256;hi++){*(uint8_t*)0x80281c=dir;*(uint8_t*)0x80281d=lo;*(uint8_t*)0x80281e=hi;ticks=mults=0;uint32_t r=opencfw_em9305_mode_callback_32c884(0x810000,0);if(lo<5||hi<5||lo>150||hi>150||hi<lo){assert(r==0xbeef&&mults==0&&ticks==0);}else{assert(r==1+dir&&ticks==1+dir&&mults==2);assert(*(uint32_t*)0x8100ec==hi*123+7&&*(uint32_t*)0x8100e8==lo*123+7);assert(*(uint8_t*)0x810235==dir);if(dir)assert(*(uint32_t*)0x8100f0==1);assert(*(uint32_t*)0x8100e4==1+dir);}}for(unsigned m=0;m<256;m++)if(m!=1){*(uint8_t*)0x810002=m;*(uint32_t*)0x81027c=0xffff;assert(opencfw_em9305_mode_callback_32c884(0x810000,0)==0xface);}*(uint32_t*)0x805c6c=0x830000;for(unsigned n=0;n<256;n++){*(uint8_t*)0x830004=n;*(uint16_t*)0x830006=n+300;*(uint16_t*)0x830008=n+900;assert(opencfw_em9305_init_registered_32ce04(0x810000)==0x810262);assert(*(uint8_t*)0x810261==n&&*(uint16_t*)0x810262==n+900&&*(uint16_t*)0x810264==n+300);}puts("PASS131583 timer validation and registration paths; host multiply model");}
