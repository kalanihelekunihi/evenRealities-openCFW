#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_callback_31ae84(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_3245ec(uint32_t,uintptr_t,uintptr_t,uint32_t);
static unsigned expected;
uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t a,uint32_t b,uint32_t c,uint32_t d,uintptr_t h,uintptr_t s,uintptr_t o,uint32_t t,uint32_t n){assert(!a&&!b&&c==(expected&255)&&!d&&s==0x830000&&o==0x820000&&t==8&&n==expected+17);assert(*(uint8_t*)h==7);for(unsigned j=1;j<5;j++)assert(*(uint8_t*)(h+j)==0);return 0x456;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805cac=0x830000;for(unsigned count=0;count<65;count++)for(unsigned key=0;key<256;key++){*(uint8_t*)0x83000d=count;*(uint8_t*)0x810001=key;for(unsigned j=0;j<65;j++){*(uint8_t*)(uintptr_t)(0x805184+j*12)=j&1;*(uint8_t*)(uintptr_t)(0x805185+j*12)=j;}assert(opencfw_em9305_init_callback_31ae84(0x810000)==0x810000);for(unsigned j=0;j<65;j++){unsigned cleared=j<count&&(j&1)&&j==key;assert(*(uint8_t*)(uintptr_t)(0x805184+j*12)==(cleared?0:j&1));assert(*(uint8_t*)(uintptr_t)(0x805185+j*12)==(cleared?0:j));}}for(unsigned n=0;n<512;n++){expected=n;assert(opencfw_em9305_init_callback_3245ec(n,0x820000,0x830000,n+17)==0x456);}puts("PASS17152 scan/compositor paths");}
