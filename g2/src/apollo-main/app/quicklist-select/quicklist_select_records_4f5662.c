/* Apollo QuickList row selection 0x4f5662..0x4f570d.
 * The source table is live RAM; the caller may compact it in place. */
#include <stdint.h>

extern void audio_uart_checksum_copy(void *, const void *, uint32_t); /* 0x439c04 */

uint32_t audio_quicklist_select_records_4f5662(void *output, uint32_t capacity,
                                                uint32_t *selected, uint32_t filter) {
    if (selected == 0)
        return 2u;
    uint8_t *const source = (uint8_t *)(uintptr_t)0x20101a1cu;
    uint8_t *const destination = output == 0 ?
        (uint8_t *)(uintptr_t)0x20367bd8u : (uint8_t *)output;
    *selected = 0u;
    for (uint32_t index = 0u; index < 20u && *selected < capacity; ++index) {
        uint8_t *const row = source + 232u * index;
        if (*(volatile uint8_t *)(void *)(row + 228u) == 0u ||
            *(volatile uint8_t *)(void *)(source + 0x1222u) != (uint8_t)filter)
            continue;
        const uint32_t id = *(volatile uint32_t *)(void *)row;
        uint8_t duplicate = 0u;
        const volatile uint8_t *const existing = (const volatile uint8_t *)(uintptr_t)0x2012a72cu;
        const uint16_t existing_count = *(const volatile uint16_t *)(const void *)existing;
        for (uint32_t prior = 1u; prior < existing_count; ++prior) {
            const uint32_t prior_id = *(const volatile uint32_t *)(const void *)(
                existing + 296u * prior + 0x114u);
            if (prior_id == id) {
                duplicate = 1u;
                break;
            }
        }
        if (duplicate == 0u) {
            audio_uart_checksum_copy(destination + 232u * *selected, row, 232u);
            ++*selected;
        }
    }
    return 0u;
}
