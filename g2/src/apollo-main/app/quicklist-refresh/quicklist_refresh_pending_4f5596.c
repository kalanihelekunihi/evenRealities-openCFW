/* Apollo QuickList pending-count update at 0x4f5596..0x4f55df. */
#include <stdint.h>

void audio_quicklist_refresh_pending_4f5596(void) {
    const uint8_t state = *(volatile uint8_t *)(uintptr_t)0x2012d57au;
    volatile uint16_t *const count = (volatile uint16_t *)(uintptr_t)0x2012a72cu;
    const volatile uint16_t *const increment =
        (const volatile uint16_t *)(uintptr_t)0x2012d574u;
    if (state == 1u) {
        *count = *increment;
    } else if (state == 2u || state == 3u) {
        const uint32_t sum = (uint32_t)*count + (uint32_t)*increment;
        *count = (uint16_t)(sum >= 41u ? 40u : sum);
    }
}
