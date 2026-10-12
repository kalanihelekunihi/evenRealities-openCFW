#include <assert.h>
#include <stdint.h>
#include <string.h>

uintptr_t opencfw_em9305_radio_secondary_encode_32e164(uintptr_t,uintptr_t);
static uint16_t get16(const uint8_t *p)
{return (uint16_t)((uint32_t)p[0]|((uint32_t)p[1]<<8u));}
static uint32_t get32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|
    ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);}
int main(void)
{
    uint8_t source[18],output[32];
    for(unsigned seed=0u;seed<64u;seed++){
        for(unsigned i=0u;i<18u;i++)source[i]=(uint8_t)(seed*7u+i*19u);
        memset(output,0xa5,sizeof output);
        assert(opencfw_em9305_radio_secondary_encode_32e164(
            (uintptr_t)output,(uintptr_t)source)==(uintptr_t)output);
        uint16_t first=get16(source);
        assert(get16(output)==(first&0x1fffu));
        assert(output[2]==((first>>13u)&1u));
        assert(output[3]==((first>>14u)&1u));
        assert(get16(output+4u)==get16(source+2u));
        assert(get32(output+8u)==get32(source+4u));
        assert(get32(output+12u)==(source[8]&31u));
        assert(output[16]==(source[8]>>5u));
        assert(get32(output+20u)==get32(source+9u));
        assert(get32(output+24u)==(get32(source+13u)&0xffffffu));
        assert(get16(output+28u)==get16(source+16u));
        assert(output[6]==0xa5u&&output[7]==0xa5u);
    }
    return 0;
}
