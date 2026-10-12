#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_callback_318168(uint32_t);
static uint32_t gate_result, calls, mutate;
uint32_t opencfw_em9305_ll_stream_gate_30e510(void) { return gate_result; }

static uint32_t on_stop(uintptr_t field, uint32_t zero, uintptr_t self,
                        uintptr_t object)
{
    assert(self==(uintptr_t)on_stop && zero==0u && field==object+44u);
    ++calls;
    if (mutate) {
        /* Native reloads row object and root configuration after the call. */
        *(volatile uint32_t *)(uintptr_t)0x805180u=0x811000u;
        *(volatile uint32_t *)(uintptr_t)0x805cacu=0x812000u;
    }
    return 0xdeadbeefu;
}

int main(void)
{
    for (uintptr_t base=0x805000u;base<=0x812000u;base+=0x1000u) {
        void *p=mmap((void *)base,4096u,PROT_READ|PROT_WRITE,
                     MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
        assert(p==(void *)base);
    }
    uint8_t *old=(uint8_t *)(uintptr_t)0x810000u;
    uint8_t *replacement=(uint8_t *)(uintptr_t)0x811000u;
    uint8_t *cfg=(uint8_t *)(uintptr_t)0x806000u;
    uint8_t *cfg2=(uint8_t *)(uintptr_t)0x812000u;
    *(uint32_t *)(uintptr_t)0x805cacu=0x806000u;
    *(uint32_t *)(uintptr_t)0x805cdcu=(uint32_t)(uintptr_t)on_stop;
    *(uint32_t *)(uintptr_t)0x805180u=0x810000u;
    *(uint8_t *)(uintptr_t)0x805184u=1;
    old[64]=2; replacement[64]=2; cfg[13]=1; cfg2[13]=1;
    gate_result=0;
    assert(opencfw_em9305_init_callback_318168(99)==0 && calls==0);
    gate_result=1;
    assert(opencfw_em9305_init_callback_318168(99)==1 && calls==1);
    assert(old[64]==0 && replacement[64]==2);
    old[64]=2; calls=0; mutate=1;
    assert(opencfw_em9305_init_callback_318168(99)==1 && calls==1);
    assert(old[64]==2 && replacement[64]==0);
    assert(*(uint32_t *)(uintptr_t)0x805cacu==0x812000u);
    /* Inactive, wrong kind and absent callback never invoke it. */
    mutate=0; calls=0;
    *(uint8_t *)(uintptr_t)0x805184u=0;
    assert(opencfw_em9305_init_callback_318168(99)==1 && calls==0);
    *(uint8_t *)(uintptr_t)0x805184u=1; replacement[64]=3;
    assert(opencfw_em9305_init_callback_318168(99)==1 && calls==0);
    replacement[64]=2; *(uint32_t *)(uintptr_t)0x805cdcu=0;
    assert(opencfw_em9305_init_callback_318168(99)==1 && calls==0);
    return 0;
}
