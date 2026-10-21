/* Apollo Main LVGL animation descriptor defaults, 0x4503d6..0x450407. */
#include <stdint.h>

extern int32_t audio_uart_lv_anim_default_path_450634(void *);

void audio_uart_lv_anim_init_4503d6(void *descriptor) {
    uint8_t *const bytes = (uint8_t *)descriptor;
    for (uint32_t i = 0; i < 0x60u; ++i) bytes[i] = 0u;
    *(uint32_t *)(void *)(bytes + 0x30u) = 500u;
    *(uint32_t *)(void *)(bytes + 0x24u) = 0u;
    *(uint32_t *)(void *)(bytes + 0x2cu) = 100u;
    *(uint32_t *)(void *)(bytes + 0x44u) = 1u;
    *(uint32_t *)(void *)(bytes + 0x20u) = (uint32_t)(uintptr_t)audio_uart_lv_anim_default_path_450634;
    bytes[0x5cu] |= 0x10u;
}
