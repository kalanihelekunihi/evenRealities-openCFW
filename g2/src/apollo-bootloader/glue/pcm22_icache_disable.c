/* Source-owned stock 0x41e22e PCM2.2 I-cache disable leaf.
 * Reconstructed from the locked instructions and independently compared.
 */
#include <stdint.h>

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))

uint32_t opencfw_pcm22_icache_disable(void)
{
    if ((WORD(0xe001e300u) & 0x300u) != 0u)
        return 1u;
    __asm__ volatile("dsb sy\n\tisb sy" ::: "memory");
    WORD(0xe000ed14u) &= ~0x20000u;
    WORD(0xe000ef50u) = 0u;
    __asm__ volatile("dsb sy\n\tisb sy" ::: "memory");
    return 0u;
}
