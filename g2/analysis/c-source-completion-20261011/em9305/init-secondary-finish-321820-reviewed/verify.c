#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_init_secondary_finish_321820(void);
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    *(volatile uint8_t *)(uintptr_t)0x803d71u=0xa5u;
    assert(opencfw_em9305_init_secondary_finish_321820()==0x803d71u);
    assert(*(volatile uint8_t *)(uintptr_t)0x803d71u==0u);
    return 0;
}
