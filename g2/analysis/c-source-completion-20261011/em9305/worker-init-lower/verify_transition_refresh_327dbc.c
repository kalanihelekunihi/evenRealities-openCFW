#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

uintptr_t opencfw_em9305_init_transition_refresh_327dbc(void);
int main(void)
{
    void *mapped=mmap((void *)(uintptr_t)0x805000u,0x10000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(mapped!=(void *)-1);
    *(volatile uint32_t *)(uintptr_t)0x805398u=0xa5b6c7d8u;
    assert(opencfw_em9305_init_transition_refresh_327dbc()==
        (uintptr_t)0x805398u);
    assert(*(volatile uint32_t *)(uintptr_t)0x805398u==0u);
    return 0;
}
