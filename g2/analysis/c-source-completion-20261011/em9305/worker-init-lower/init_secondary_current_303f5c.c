#include <stdint.h>

/* Full native 0x303f5c..0x303f66. The pointer at 0x805c18 is read first;
 * the pointed-to halfword is a live runtime value, not initialized data. */
uint32_t opencfw_em9305_init_secondary_current_303f5c(void)
{
    uintptr_t current=*(volatile uint32_t *)(uintptr_t)0x805c18u;
    return *(volatile uint16_t *)current;
}
