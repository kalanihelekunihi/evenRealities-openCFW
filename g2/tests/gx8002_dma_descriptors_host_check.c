/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern void open_cfw_gx8002_dma_descriptors(volatile uint32_t *,volatile uint32_t *,int32_t,int32_t,uint8_t);
static uint32_t translations[32];
static unsigned calls;
uint32_t open_cfw_gx8002_dma_bus_address(uint32_t address)
{
    if (calls>=32) abort();
    translations[calls++]=address;
    return address>=0x10000000u && address<0x30000000u ? address&0x0fffffffu : address;
}
static uint32_t bus(uint32_t p) {return p>=0x10000000u && p<0x30000000u ? p&0x0fffffffu : p;}
int main(void)
{
    const uint32_t step[4]={4095,61441,0,0};
    const int32_t lengths[]={0,1,4094,4095,4096,8190,69615,-1,-4095};
    const uint8_t widths[]={0,1,2,4,128,255};
    unsigned cases=0;
    for (int count=0;count<=17;++count)
    for (unsigned src=0;src<4;++src) for (unsigned dst=0;dst<4;++dst)
    for (unsigned w=0;w<sizeof(widths);++w)
    for (unsigned n=0;n<sizeof(lengths)/sizeof(lengths[0]);++n) {
        uint32_t pattern[6]={0xfffffff0u,0x20000000u,0xdeadbeef,0x18000000u|(src<<9)|(dst<<7),0x12345678,0xaabbccdd};
        uint32_t output[18*6],wanted[18*6],before[6];
        memcpy(before,pattern,sizeof(pattern));
        for (unsigned i=0;i<18*6;++i)output[i]=wanted[i]=0xa5a50000u+i;
        unsigned used=count>0?(unsigned)count:1;
        for (unsigned i=0;i<used;++i) {
            wanted[i*6]=pattern[0]+i*step[src]*widths[w];
            wanted[i*6+1]=pattern[1]+i*step[dst]*widths[w];
            wanted[i*6+2]=i+1<used?bus((uint32_t)(uintptr_t)(output+(i+1)*6)):0;
            wanted[i*6+3]=i+1<used?pattern[3]:pattern[3]&~0x18000000u;
            int32_t rem=lengths[n]%4095;
            wanted[i*6+4]=i+1<used?4095u:rem?(uint32_t)rem:4095u;
        }
        calls=0;
        open_cfw_gx8002_dma_descriptors(pattern,output,count,lengths[n],widths[w]);
        if (memcmp(wanted,output,sizeof(output)) || memcmp(before,pattern,sizeof(pattern)) || calls!=used-1) abort();
        for (unsigned i=0;i<calls;++i)if (translations[i]!=(uint32_t)(uintptr_t)(output+(i+1)*6))abort();
        ++cases;
    }
    printf("Descriptor host cases: %u\n",cases);
}
