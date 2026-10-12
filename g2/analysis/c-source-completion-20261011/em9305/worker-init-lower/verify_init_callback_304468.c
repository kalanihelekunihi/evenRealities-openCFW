#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_callback_304468(uintptr_t,uintptr_t);
static uint32_t cancel_calls,callback_calls,alternate_calls,expected_first,expected_args;
static volatile uint32_t *callback_slot;
static uint32_t alternate(uintptr_t first,uint32_t r1,uint32_t r2,uint32_t r3,uint32_t r4);
uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t value)
{ assert(value==9u);++cancel_calls;*callback_slot=(uint32_t)(uintptr_t)alternate;return 0xdeadbeefu; }
static uint32_t cb(uintptr_t first,uint32_t r1,uint32_t r2,uint32_t r3,uint32_t r4)
{
    assert(first==expected_first && r4==0x12345678u);
    if(expected_args)assert(r1==0x11u&&r2==0x22u&&r3==0x33u);
    else assert(r1==0u&&r2==0u&&r3==0u);
    ++callback_calls;return 0xabcdef01u;
}
static uint32_t alternate(uintptr_t first,uint32_t r1,uint32_t r2,uint32_t r3,uint32_t r4)
{
    assert(first==expected_first && r1==0x11u && r2==0x22u && r3==0x33u && r4==0x12345678u);
    ++alternate_calls;
    return 0x98765432u;
}
int main(void)
{
    for(uintptr_t base=0x810000u;base<=0x813000u;base+=0x1000u)
        assert(mmap((void *)base,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)base);
    uint8_t *request=(uint8_t *)(uintptr_t)0x810000u;
    uint8_t *ctx=(uint8_t *)(uintptr_t)0x811000u;
    uint8_t *mode=(uint8_t *)(uintptr_t)0x812000u;
    uint8_t *payload=(uint8_t *)(uintptr_t)0x813000u;
    *(uint32_t *)(ctx+104u)=0x812000u;
    *(uint32_t *)(request+44u)=0x813000u;
    *(uint32_t *)(ctx+168u)=0x12345678u;
    callback_slot=(volatile uint32_t *)(ctx+232u);
    *(uint32_t *)(ctx+236u)=0x11u;
    *(uint32_t *)(ctx+244u)=0x22u;
    *(uint32_t *)(ctx+252u)=0x33u;
    ctx[225u]=2u;ctx[228u]=9u;ctx[261u]=1u;
    mode[0]=7u;payload[0]=8u;
    assert(opencfw_em9305_init_callback_304468((uintptr_t)request,(uintptr_t)ctx)==1u);
    assert(cancel_calls==0u&&callback_calls==0u);
    *(uint32_t *)(ctx+232u)=(uint32_t)(uintptr_t)cb;
    expected_args=1u;expected_first=(uint32_t)(uintptr_t)(ctx+216u);
    assert(opencfw_em9305_init_callback_304468((uintptr_t)request,(uintptr_t)ctx)==0u);
    assert(cancel_calls==1u&&callback_calls==0u&&alternate_calls==1u&&ctx[261u]==2u);
    *callback_slot=(uint32_t)(uintptr_t)cb;
    mode[0]=5u;expected_args=0u;expected_first=(uint32_t)(uintptr_t)(ctx+208u);
    assert(opencfw_em9305_init_callback_304468((uintptr_t)request,(uintptr_t)ctx)==0u);
    assert(cancel_calls==1u&&callback_calls==1u&&alternate_calls==1u);
    mode[0]=7u;payload[0]=9u;
    assert(opencfw_em9305_init_callback_304468((uintptr_t)request,(uintptr_t)ctx)==1u);
    assert(cancel_calls==1u&&callback_calls==1u&&alternate_calls==1u);
    return 0;
}
