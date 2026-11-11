#include <stdint.h>

/* Native 0x3256c8..0x325708: scan backoff update. Every second call halves
 * the backoff window +98 (minimum 1); then clear +102 and pick a random
 * count in 1..window into +100, which is also returned. */
extern uint32_t opencfw_em9305_scan_random_30c478(void);

uint32_t opencfw_em9305_child_3256c8(uintptr_t scan)
{
    uint32_t calls = *(volatile uint8_t *)(scan + 101u) + 1u;
    *(volatile uint8_t *)(scan + 101u) = (uint8_t)calls;
    if ((uint8_t)calls >= 2u) {
        uint32_t window = *(volatile uint16_t *)(scan + 98u);
        *(volatile uint8_t *)(scan + 101u) = 0u;
        window >>= 1;
        if (window == 0u) window = 1u;
        *(volatile uint16_t *)(scan + 98u) = (uint16_t)window;
    }
    *(volatile uint8_t *)(scan + 102u) = 0u;
    uint32_t random = opencfw_em9305_scan_random_30c478();
    uint32_t count = (random & (*(volatile uint16_t *)(scan + 98u) - 1u)) + 1u;
    *(volatile uint8_t *)(scan + 100u) = (uint8_t)count;
    return count;
}
