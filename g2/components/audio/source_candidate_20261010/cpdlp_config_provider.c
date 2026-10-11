/* Apollo MAIN 0x47FFC4: CPDLP config write guarded by cache state. */
#include <stdint.h>

uint32_t stock_cpdlp_config(uint32_t config) {
    volatile uint32_t * const ccr = (volatile uint32_t *)0xe000ed14u;
    volatile uint32_t * const cpdlp = (volatile uint32_t *)0xe001e300u;
    uint8_t first = (uint8_t)config;
    if ((*ccr & 0x30000u) && first == 3u) return 1;
    uint32_t value = ((uint32_t)first << 8) |
                     (((config >> 8) & 0xffu) << 4) |
                     ((config >> 16) & 0xffu);
    *cpdlp = value;
    return 0;
}
