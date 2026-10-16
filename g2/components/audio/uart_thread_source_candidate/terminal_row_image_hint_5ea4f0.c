/* Stock Terminal row image inheritance hint at 0x5ea4f0. */
#include <stdint.h>

extern uint32_t audio_terminal_item_59737c(uint32_t index);

uint32_t audio_terminal_row_image_hint_5ea4f0(uint32_t index, uint32_t item) {
    if (item == 0u ||
        *(const uint8_t *)(const void *)(uintptr_t)(item + 1u) != 0u ||
        (uint16_t)index == 0u)
        return 0u;
    uint32_t previous = audio_terminal_item_59737c((uint16_t)(index - 1u));
    if (previous == 0u)
        return 0u;
    return *(const uint8_t *)(const void *)(uintptr_t)(previous + 1u) == 1u ? 1u : 0u;
}
