#include <assert.h>
#include <stdint.h>
#include <string.h>

uint32_t opencfw_em9305_init_transition_packet_copy_32dd54(
    uintptr_t,uintptr_t);
static unsigned pack_calls;
static uintptr_t output_base;
uint64_t opencfw_em9305_controller_pack_address(uintptr_t input)
{
    const uint8_t *p=(const uint8_t *)input;
    assert(pack_calls<2u);
    if(pack_calls==1u)
        assert(*(uint32_t *)(void *)(output_base+4u)==
            ((uint32_t)((const uint8_t *)input)[-2]| 
             ((uint32_t)((const uint8_t *)input)[-1]<<8u)));
    pack_calls++;
    uint32_t low=(uint32_t)p[0]|((uint32_t)p[1]<<8u)|
        ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
    uint32_t high=(uint32_t)p[4]|((uint32_t)p[5]<<8u);
    return ((uint64_t)high<<32u)|low;
}
static uint16_t get16(const uint8_t *p)
{return (uint16_t)((uint32_t)p[0]|((uint32_t)p[1]<<8u));}
static uint32_t get32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|
    ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);}
int main(void)
{
    uint8_t source[34],output[48];
    for(unsigned seed=0u;seed<64u;seed++){
        for(unsigned i=0u;i<34u;i++)source[i]=(uint8_t)(seed*19u+i*37u);
        memset(output,0xa5,sizeof output);pack_calls=0u;
        output_base=(uintptr_t)output;
        assert(opencfw_em9305_init_transition_packet_copy_32dd54(
            (uintptr_t)output,(uintptr_t)source)==34u);
        assert(pack_calls==2u);
        assert(get32(output)==get32(source));
        assert(get32(output+4u)==get16(source+4u));
        assert(get32(output+8u)==get32(source+6u));
        assert(get32(output+12u)==get16(source+10u));
        assert(get32(output+16u)==get32(source+12u));
        assert(get32(output+20u)==(get32(source+16u)&0x00ffffffu));
        assert(get32(output+24u)==get32(source+28u));
        assert(get32(output+28u)==source[32]);
        assert(get16(output+32u)==get16(source+22u));
        assert(get16(output+34u)==get16(source+24u));
        assert(get16(output+36u)==get16(source+26u));
        assert(output[38]==source[19]);
        assert(get16(output+40u)==get16(source+20u));
        assert(output[42]==(source[33]&31u));
        assert(output[43]==(source[33]>>5u));
    }
    return 0;
}
