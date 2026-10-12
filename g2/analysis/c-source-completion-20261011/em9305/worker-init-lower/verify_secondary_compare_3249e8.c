#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

uintptr_t opencfw_em9305_init_secondary_compare_3249e8(uintptr_t,uintptr_t);
#define R32(p) (*(uint32_t *)(uintptr_t)(p))
#define R8(p) (*(uint8_t *)(uintptr_t)(p))
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x801000u,0x5000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p==(void *)(uintptr_t)0x801000u);
    const uintptr_t a=0x801000u,b=0x802000u;
    R32(b+44u)=0x803000u;
    R32(a+36u)=0x804000u;
    R32(b+36u)=0x805000u;
    R8(0x803000u)=8u;
    assert(opencfw_em9305_init_secondary_compare_3249e8(a,b)==b);
    R8(0x803000u)=9u;
    R32(0x805000u+708u)=0u;
    R32(0x805000u+252u)=100u;
    assert(opencfw_em9305_init_secondary_compare_3249e8(a,b)==b);
    R32(0x805000u+708u)=1000u;
    R32(0x804000u+708u)=0u;
    R32(0x804000u+252u)=100u;
    assert(opencfw_em9305_init_secondary_compare_3249e8(a,b)==a);
    /* Host fallback models the ordered decision only; ARC DSP values are
     * checked separately from the emitted named instructions. */
    R32(0x804000u+708u)=1000u;
    R32(0x804000u+252u)=20u;
    R32(0x805000u+252u)=100u;
    assert(opencfw_em9305_init_secondary_compare_3249e8(a,b)==b);
    R32(0x804000u+252u)=100u;
    R32(0x805000u+252u)=20u;
    assert(opencfw_em9305_init_secondary_compare_3249e8(a,b)==a);
    R32(0x805000u+252u)=100u;
    assert(opencfw_em9305_init_secondary_compare_3249e8(a,b)==b);
    return 0;
}
