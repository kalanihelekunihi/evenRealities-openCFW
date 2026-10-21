/* Apollo Main animation value setter, native span 0x4506ce..0x4506d9. */
#include <stdint.h>

void audio_uart_lv_anim_values_4506ce(void *animation, int32_t start, int32_t end) {
    uint8_t *const bytes = (uint8_t *)animation;
    *(uint32_t *)(void *)(bytes + 0x24u) = (uint32_t)start;
    *(uint32_t *)(void *)(bytes + 0x28u) = 0x80000000u;
    *(uint32_t *)(void *)(bytes + 0x2cu) = (uint32_t)end;
}
