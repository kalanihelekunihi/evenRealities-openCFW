#include <assert.h>
#include <stdint.h>
#include <string.h>

extern uint32_t opencfw_em9305_radio_key_operation_30ff70(uintptr_t,
                                                            uintptr_t,
                                                            uintptr_t);
extern uint32_t opencfw_em9305_radio_key_operation_30ffbc(uintptr_t,
                                                            uintptr_t);
static uint8_t point[64],scalar[32],output[64];
static uint32_t failure,word_calls,multiply_calls,base_calls;

uint32_t opencfw_em9305_vendor_words_3333d0(uintptr_t destination,
                                               uintptr_t source)
{
    ++word_calls;
    for(unsigned group=0;group<8u;++group)
        for(unsigned byte=0;byte<4u;++byte)
            *(uint8_t *)(destination+group*4u+byte)=
                *(uint8_t *)(source+(7u-group)*4u+byte);
    return 0u;
}
uint32_t opencfw_em9305_rom_curve_multiply_1081e8(uintptr_t input,
                                                    uintptr_t key,
                                                    uintptr_t product)
{
    ++multiply_calls;assert(key==(uintptr_t)scalar);
    for(unsigned i=0;i<64u;++i)
        assert(*(uint8_t *)(input+i)==point[(i<32u?0u:32u)+
                                            (7u-(i%32u)/4u)*4u+i%4u]);
    if(failure)return 0x42u;
    for(unsigned i=0;i<32u;++i)*(uint8_t *)(product+i)=(uint8_t)(i+1u);
    return 0u;
}
uint32_t opencfw_em9305_rom_curve_base_108178(uintptr_t key,
                                                uintptr_t product)
{
    ++base_calls;assert(key==(uintptr_t)scalar);
    if(failure)return 0x43u;
    for(unsigned i=0;i<64u;++i)*(uint8_t *)(product+i)=(uint8_t)(i+1u);
    return 0u;
}
int main(void)
{
    for(unsigned i=0;i<64u;++i)point[i]=(uint8_t)(i+0x20u);
    memset(output,0xa5,sizeof output);
    failure=1u;
    assert(opencfw_em9305_radio_key_operation_30ff70(
               (uintptr_t)point,(uintptr_t)scalar,(uintptr_t)output)==0x42u);
    assert(word_calls==2u&&multiply_calls==1u);
    for(unsigned i=0;i<64u;++i)assert(output[i]==0xa5u);
    failure=0u;
    assert(opencfw_em9305_radio_key_operation_30ff70(
               (uintptr_t)point,(uintptr_t)scalar,(uintptr_t)output)==32u);
    for(unsigned i=0;i<32u;++i)
        assert(output[i]==(uint8_t)((7u-i/4u)*4u+i%4u+1u));
    memset(output,0xa5,sizeof output);failure=1u;
    assert(opencfw_em9305_radio_key_operation_30ffbc(
               (uintptr_t)scalar,(uintptr_t)output)==0x43u);
    for(unsigned i=0;i<64u;++i)assert(output[i]==0xa5u);
    failure=0u;
    assert(opencfw_em9305_radio_key_operation_30ffbc(
               (uintptr_t)scalar,(uintptr_t)output)==0x403f3e3du);
    for(unsigned i=0;i<32u;++i) {
        assert(output[i]==(uint8_t)((7u-i/4u)*4u+i%4u+1u));
        assert(output[i+32u]==(uint8_t)((7u-i/4u)*4u+i%4u+33u));
    }
    assert(base_calls==2u);
    return 0;
}
