#include <stdint.h>

/* Original 0x0800ca4c uses base literal 0x20000128. */
uint32_t case_scheduler_state(void)
{
    volatile uint32_t *const base = (volatile uint32_t *)(uintptr_t)0x20000128u;
    if (base[0x14u / 4u] == 0u) return 1u;
    if (base[0x30u / 4u] == 0u) return 2u;
    return 0u;
}
