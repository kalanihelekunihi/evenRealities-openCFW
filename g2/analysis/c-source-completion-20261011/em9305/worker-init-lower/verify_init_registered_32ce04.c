#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_registered_32ce04(uintptr_t);
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *source=mmap((void *)0x806000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *context=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                          MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&source!=(void *)-1&&context!=(void *)-1);
    *(uint32_t *)(root+0xc6cu)=(uint32_t)(uintptr_t)source;
    for (unsigned n=0;n<256u;++n) {
        source[4]=(uint8_t)n;
        *(uint16_t *)(source+6)=(uint16_t)(0x1234u+n);
        *(uint16_t *)(source+8)=(uint16_t)(0x5678u+n);
        assert(opencfw_em9305_init_registered_32ce04((uintptr_t)context)==
               0x810262u);
        assert(context[609]==(uint8_t)n);
        assert(*(uint16_t *)(context+610)==(uint16_t)(0x5678u+n));
        assert(*(uint16_t *)(context+612)==(uint16_t)(0x1234u+n));
    }
    return 0;
}
