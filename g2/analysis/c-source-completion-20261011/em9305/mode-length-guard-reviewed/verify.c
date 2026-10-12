#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_32ce84(uintptr_t,uintptr_t);
static unsigned notify,limit;
uint32_t opencfw_em9305_phy_length_notify_32317c(uintptr_t c,uint32_t r){assert(c==0x810000&&r==0);notify++;return 9;}
uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x81023e);limit++;return 0x12345;}
static unsigned min(unsigned a,unsigned b){return a<b?a:b;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint16_t*)0x80281c=500;*(uint16_t*)0x802820=600;for(unsigned n=0;n<328;n++){*(uint16_t*)0x802822=n;*(uint16_t*)0x80281e=0xffff;assert(opencfw_em9305_mode_callback_32ce84(0x810000,0)==n);*(uint16_t*)0x802822=400;*(uint16_t*)0x80281e=n;assert(opencfw_em9305_mode_callback_32ce84(0x810000,0)==400);}assert(!limit&&!notify);for(unsigned n=0;n<256;n++)for(unsigned modes=0;modes<4;modes++)for(unsigned flags=0;flags<4;flags++){*(uint16_t*)0x802822=400;*(uint16_t*)0x80281e=450;*(uint8_t*)0x810216=flags&1;*(uint8_t*)0x810221=(flags&2)?8:0;*(uint8_t*)0x81004d=(modes&1)?3:0;*(uint8_t*)0x81004c=(modes&2)?3:0;unsigned lo=n*13,hi=n*17;*(uint16_t*)0x810238=lo;*(uint16_t*)0x81023c=hi;*(uint16_t*)0x81023a=n+100;*(uint16_t*)0x810236=n+200;for(unsigned j=0;j<4;j++)*(uint16_t*)(uintptr_t)(0x81023e + j*2)=0xffff;if(flags!=3){lo=min(lo,0x848);hi=min(hi,0x848);}lo=min(lo,400);hi=min(hi,450);if((modes&1)&&lo<0xa90)lo=0xa90;if((modes&2)&&hi<0xa90)hi=0xa90;assert(opencfw_em9305_mode_callback_32ce84(0x810000,0)==0x12345);assert(*(uint16_t*)0x810240==lo&&*(uint16_t*)0x810244==hi);assert(*(uint16_t*)0x810242==min(n+100,500)&&*(uint16_t*)0x81023e==min(n+200,600));assert(*(uint16_t*)0x810250==0x2345);}assert(limit==4096&&notify==4096);puts("PASS4752 carry-guard/length paths");}
