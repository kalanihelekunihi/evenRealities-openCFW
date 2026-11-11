#include <stdint.h>

/* Native 0x317498..0x3174d6: clear the two configured buffers: *0x805c40
 * for (config byte 58) * 256 bytes and *0x805c3c for (config byte 57) *
 * 512 bytes; the config pointer (*0x805cac) is re-read for each. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);

void opencfw_em9305_dispatch_child_317498(void)
{
    uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uintptr_t first=*(volatile uint32_t *)(uintptr_t)0x805c40u;
    (void)opencfw_em9305_memset((void *)first,0u,
        (uint32_t)*(volatile uint8_t *)(config+58u)<<8);
    config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uintptr_t second=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
    (void)opencfw_em9305_memset((void *)second,0u,
        (uint32_t)*(volatile uint8_t *)(config+57u)<<9);
}
