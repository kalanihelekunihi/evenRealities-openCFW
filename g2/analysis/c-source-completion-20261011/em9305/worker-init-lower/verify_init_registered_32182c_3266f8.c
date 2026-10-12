#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_registered_32182c(uint32_t);
extern uint32_t opencfw_em9305_init_registered_3266f8(uintptr_t);
static unsigned common_calls,stop_calls;
uint32_t opencfw_em9305_common_init_303650(uint32_t value)
{++common_calls;return value^0x1234u;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t context,uint32_t reason)
{assert(context==0x810000u&&reason==110u);++stop_calls;return 0x5678u;}
int main(void)
{
    uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                      MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(ctx!=(void *)-1);
    for (uint32_t n=0;n<256u;++n)
        assert(opencfw_em9305_init_registered_32182c(n)==(n^0x1234u));
    assert(common_calls==256u);
    *(uint32_t *)(ctx+636u)=0xffffffffu;
    *(uint32_t *)(ctx+640u)=0xa5a5a5a5u;
    assert(opencfw_em9305_init_registered_3266f8((uintptr_t)ctx)==0x5678u);
    assert(stop_calls==1u&&ctx[608]==1u);
    assert(*(uint32_t *)(ctx+636u)==0xffffffbfu);
    assert(*(uint32_t *)(ctx+640u)==0u);
    assert(opencfw_em9305_init_registered_3266f8((uintptr_t)ctx)==0x810000u);
    assert(stop_calls==1u);
    return 0;
}
