#include <stdint.h>

/* Full native 0x321820..0x321828. The store executes in the return jump's
 * delay slot; the returned R0 remains the product-owned byte address. */
uint32_t opencfw_em9305_init_secondary_finish_321820(void)
{
    *(volatile uint8_t *)(uintptr_t)0x803d71u=0u;
    return 0x803d71u;
}
