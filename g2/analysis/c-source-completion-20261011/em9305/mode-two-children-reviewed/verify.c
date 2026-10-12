#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t);
extern uint32_t opencfw_em9305_mode_callback_value_318920(uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cde0(uintptr_t,uintptr_t);
int main(void){assert(mmap((void*)0x800000,0x40000,3,0x32,-1,0)==(void*)0x800000);*(uint32_t*)0x805c18=0x830000;unsigned limits[]={21,31,51,76,101,151,251};unsigned adjustments[]={500,250,150,100,75,50,30,20};for(unsigned v=0;v<65536;v++){*(uint16_t*)0x830000=v;unsigned rank=0;for(unsigned j=0;j<7;j++)rank+=v<limits[j];for(unsigned local=0;local<256;local+=17){*(uint8_t*)0x8102ea=local;assert(opencfw_em9305_mode_callback_value_318920(0x810000)==(uint8_t)(rank+local));}unsigned sel=v&255;assert(opencfw_em9305_mode_callback_child_317ea4(sel)==(uint16_t)(v+adjustments[sel<8?sel:7]));*(uint8_t*)0x810002=1;*(uint8_t*)0x80281c=sel;*(uint16_t*)0x8100c8=0;assert(opencfw_em9305_mode_callback_32cde0(0x810000,0)==(uint16_t)(v+adjustments[sel<8?sel:7]));assert(*(uint16_t*)0x8100c8==(uint16_t)(v+adjustments[sel<8?sel:7]));assert(*(uint8_t*)0x810228==sel);}puts("PASS1179648 connected threshold/selector/local paths");}
