#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_init_secondary_current_303f5c(void);
int main(void)
{
    void *a=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
        MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    void *b=mmap((void *)0x806000u,4096u,PROT_READ|PROT_WRITE,
        MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    assert(a==(void *)0x805000u && b==(void *)0x806000u);
    *(uint32_t *)(uintptr_t)0x805c18u=0x806140u;
    for(uint32_t value=0u;value<65536u;value+=257u){
        *(uint16_t *)(uintptr_t)0x806140u=(uint16_t)value;
        assert(opencfw_em9305_init_secondary_current_303f5c()==value);
    }
    return 0;
}
