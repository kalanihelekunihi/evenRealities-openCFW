/* Apollo MAIN 0x4D3F3C and 0x47EF38; file-backed INFO space validation. */
#include <stdint.h>

extern uint32_t audio_info_space_read(uint32_t space, uint32_t offset,
                                      uint32_t count, uint32_t *out);

uint32_t stock_info_read(uint32_t space, uint32_t offset,
                         uint32_t count, uint32_t *out) {
    uint32_t selected = (uint8_t)space;
    if (selected != 1 && selected != 3 && selected != 5) return 6;
    return audio_info_space_read(selected, offset, count, out);
}

uint32_t stock_revision(uint32_t *out) {
    volatile uint32_t * const revision = (volatile uint32_t *)0x200001e8u;
    if (*revision == UINT32_MAX) {
        uint32_t status = stock_info_read(1, 0x244, 1, (uint32_t *)revision);
        if (*revision == 0 || status != 0) *revision = 0;
    }
    if (!out) return 6;
    *out = *revision;
    return 0;
}
