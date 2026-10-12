#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
static void map_page(uintptr_t address)
{
    void *mapped=mmap((void *)(address&~(uintptr_t)4095u),4096u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(mapped==(void *)(address&~(uintptr_t)4095u));
}
static uint32_t modeled(uint32_t a,uint32_t b,uint32_t payload)
{
    uint64_t first=(uint64_t)a*b;
    uint32_t high=(uint32_t)(first>>32u);
    uint32_t correction=high*0x10c7u;
    uint64_t second=(uint64_t)(uint32_t)first*0x10c7u;
    uint32_t low=(uint32_t)second;
    uint32_t carry=low>UINT32_MAX-0x6ef9u;
    return payload+(uint32_t)(second>>32u)+correction+carry+17u;
}
int main(void)
{
    map_page(0x805a8bu);map_page(0x805cacu);map_page(0x806000u);
    *(uint32_t *)(uintptr_t)0x805cacu=0x806000u;
    *(uint8_t *)(uintptr_t)0x806029u=0x79u;
    *(uint8_t *)(uintptr_t)0x805a8bu=0u;
    assert(opencfw_em9305_init_secondary_time_317ebc(0xffffffffu,0xffffffffu)==0u);
    *(uint8_t *)(uintptr_t)0x805a8bu=8u;
    for(uint32_t a=0u;a<256u;a++)for(uint32_t b=0u;b<17u;b++)
        assert(opencfw_em9305_init_secondary_time_317ebc(a*0x1020304u,b*0x1234567u)==
            modeled(a*0x1020304u,b*0x1234567u,0x79u));
    return 0;
}
