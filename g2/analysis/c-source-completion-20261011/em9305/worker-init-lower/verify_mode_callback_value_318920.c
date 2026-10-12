#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_mode_callback_value_318920(uintptr_t);
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *context=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                          MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&context!=(void *)-1);
    *(uint32_t *)(root+0xc18u)=(uint32_t)(uintptr_t)(root+0x200u);
    for (uint32_t n=0;n<65536u;++n) {
        *(uint16_t *)(root+0x200u)=(uint16_t)n;
        context[746]=(uint8_t)(n>>3);
        uint32_t rank=n<21u?7u:n<31u?6u:n<51u?5u:n<76u?4u:
                      n<101u?3u:n<151u?2u:n<251u?1u:0u;
        assert(opencfw_em9305_mode_callback_value_318920((uintptr_t)context)==
               (uint8_t)(rank+context[746]));
    }
    return 0;
}
