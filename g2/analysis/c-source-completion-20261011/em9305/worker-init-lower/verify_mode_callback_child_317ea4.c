#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t);
extern uint32_t opencfw_em9305_mode_callback_32cde0(uintptr_t,uintptr_t);
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *global=mmap((void *)0x802000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *context=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                          MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&global!=(void *)-1&&context!=(void *)-1);
    *(uint32_t *)(root+0xc18u)=(uint32_t)(uintptr_t)(root+0x200u);
    *(uint16_t *)(root+0x200u)=0xfff0u;
    const uint16_t increments[8]={500u,250u,150u,100u,75u,50u,30u,20u};
    for (uint32_t n=0;n<256u;++n) {
        uint32_t k=n<7u?n:7u;
        assert(opencfw_em9305_mode_callback_child_317ea4(n)==
               (uint16_t)(0xfff0u+increments[k]));
    }
    global[0x81cu]=5u;context[2]=1u;
    assert(opencfw_em9305_mode_callback_32cde0((uintptr_t)context,0)==34u);
    assert(context[552]==5u&&*(uint16_t *)(context+200u)==34u);
    context[2]=0u;global[0x81cu]=9u;
    assert(opencfw_em9305_mode_callback_32cde0((uintptr_t)context,0)==9u);
    assert(context[552]==9u&&*(uint16_t *)(context+200u)==34u);
    return 0;
}
