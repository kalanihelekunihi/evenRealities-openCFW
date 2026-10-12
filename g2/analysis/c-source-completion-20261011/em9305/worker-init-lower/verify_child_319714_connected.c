#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_child_319714(uint32_t,uint32_t,uint32_t);
static unsigned copy_calls;
static uintptr_t copy_out[3],copy_in[3];
static uint32_t copy_size[3];
uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t context,
                                                     uintptr_t packet)
{
    (void)context;
    return (*(volatile uint8_t *)packet&0x20u)!=0u?3u:2u;
}
void *opencfw_em9305_memcpy(void *destination,const void *source,uint32_t bytes)
{
    assert(copy_calls<3u);
    copy_out[copy_calls]=(uintptr_t)destination;
    copy_in[copy_calls]=(uintptr_t)source;
    copy_size[copy_calls]=bytes;
    ++copy_calls;
    volatile uint8_t *out=(volatile uint8_t *)destination;
    volatile const uint8_t *in=(volatile const uint8_t *)source;
    for(uint32_t i=0;i<bytes;++i) out[i]=in[i];
    return destination;
}

int main(void)
{
    assert(mmap((void *)0x800000u,0x100000u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
    unsigned cases=0;
    for(unsigned opcode=3;opcode<=19;++opcode)
    for(unsigned header=2;header<=3;++header)
    for(unsigned mode=0;mode<=2;++mode)
    for(unsigned state_ok=0;state_ok<2;++state_ok)
    for(unsigned flag=0;flag<2;++flag) {
        memset((void *)0x800000u,0,0x100000u);
        uintptr_t payload=0x801000u+header+1u;
        *(volatile uint8_t *)0x801000u=header==3u?0x20u:0u;
        *(volatile uint8_t *)(uintptr_t)(0x801000u+header)=(uint8_t)opcode;
        for(unsigned i=0;i<32;++i)
            *(volatile uint8_t *)(payload+i)=(uint8_t)(i*7u+1u);
        *(volatile uint8_t *)0x805a94u=flag?0x10u:0u;
        uint8_t wanted=opcode==3u?23u:opcode==4u?13u:1u;
        *(volatile uint8_t *)0x800005u=state_ok?wanted:0xffu;
        copy_calls=0u;
        uint32_t result=opencfw_em9305_child_319714(0x800000u,0x801000u,mode);
        assert(*(volatile uint8_t *)0x800008u==opcode);
        unsigned copies=opcode==3u&&mode!=0u?3u:opcode==4u&&mode!=1u?1u:0u;
        assert(copy_calls==copies);
        if(copies) {
            assert(copy_out[0]==0x80000cu && copy_in[0]==payload);
            assert(copy_size[0]==(opcode==3u?8u:12u));
            if(copies==3u) {
                assert(copy_out[1]==0x800016u && copy_in[1]==payload+10u && copy_size[1]==8u);
                assert(copy_out[2]==0x80001eu && copy_in[2]==payload+18u && copy_size[2]==4u);
                assert(*(volatile uint16_t *)0x800014u==
                       (uint16_t)((uint16_t)*(volatile uint8_t *)(payload+8u)|
                                  ((uint16_t)*(volatile uint8_t *)(payload+9u)<<8)));
            }
        }
        int checks=opcode==3u?mode!=0u:opcode==4u||opcode==5u?mode!=1u:
                   opcode==6u||opcode==11u?1:opcode==10u?mode!=0u:
                   opcode==18u||opcode==19u?flag:0;
        assert(result==(checks&&state_ok?0u:25u));
        ++cases;
    }
    for(unsigned opcode=0;opcode<21;opcode+=20) {
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x801002u=(uint8_t)opcode;
        assert(opencfw_em9305_child_319714(0x800000u,0x801000u,0u)==25u);
        assert(*(volatile uint8_t *)0x800008u==opcode);
        ++cases;
    }
    printf("PASS 319714 connected dispatcher %u host route fixtures\n",cases);
    return 0;
}
