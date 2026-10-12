#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_32c908(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325b98(uintptr_t,uintptr_t);
static uint32_t slot;static unsigned kind;
uint32_t opencfw_em9305_pal_current_time(void){return 100;}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t n,uint32_t p){assert(n==100&&p==11);return 89;}
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){assert(n==11);return slot;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t c,uintptr_t p){assert(c==0x810000&&p==0x820000);*(uint32_t*)0x81027c=0xdeadbeef;return 77;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t c,uint32_t r){assert(c==0x810000&&r==110);if(kind)assert(*(uint32_t*)0x810280==0&&(*(uint32_t*)0x81027c&512)==0);return 0x123;}
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805c6c=0x830000;*(uint32_t*)0x8103a0=0x87654321;*(uint32_t*)0x8103b0=0x76543210;for(unsigned n=0;n<256;n++){kind=0;*(uint8_t*)0x810002=0;*(uint8_t*)0x810235=1;*(uint32_t*)0x8100e8=11;*(uint32_t*)0x8100ec=89;for(unsigned j=0;j<10;j++)*(uint8_t*)(uintptr_t)(0x80281c+j)=n+j;*(uint8_t*)0x8100e6=99;assert(opencfw_em9305_mode_callback_32c908(0x810000,0)==((n+9)&3));for(unsigned j=0;j<9;j++)for(unsigned f=0;f<4;f++)assert(*(uint8_t*)(uintptr_t)(0x8100c1+j*4+f)==((uint8_t)(n+j)&(3u<<(2*f))));assert(*(uint8_t*)0x8100e6==99);*(uint32_t*)0x8100ec=90;assert(opencfw_em9305_mode_callback_32c908(0x810000,0)==89);*(uint8_t*)0x810002=1;assert(opencfw_em9305_mode_callback_32c908(0x810000,0)==0x123);*(uint8_t*)0x810002=0;*(uint8_t*)0x810235=0;assert(opencfw_em9305_mode_callback_32c908(0x810000,0)==0x123);kind=1;for(unsigned fail=0;fail<2;fail++){slot=fail?0:0x820000;for(unsigned j=0;j<41;j++)*(uint8_t*)(uintptr_t)(0x830000+j)=n+j;*(uint32_t*)0x81027c=0xffffffff;assert(opencfw_em9305_mode_callback_325b98(0x810000,0)==0x123);if(!fail){assert(*(uint8_t*)0x820000==41);for(unsigned j=0;j<9;j++){unsigned a=0;for(unsigned f=0;f<4;f++)a|=(uint8_t)(n+4+j*4+f)<<(2*f);assert(*(uint8_t*)(uintptr_t)(0x820001+j)==(uint8_t)a);}assert(*(uint8_t*)0x82000a==(uint8_t)(n+40));}}}assert(*(uint32_t*)0x8103a0==0x87654321&&*(uint32_t*)0x8103b0==0x76543210);puts("PASS1536 packed record/gate paths");}
