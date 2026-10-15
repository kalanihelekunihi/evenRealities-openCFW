/* Apollo S200 Ambiq clip update at 0x4b077e and Nema scissor at 0x4b1488. */
#include <stdint.h>

extern uint32_t audio_uart_ambiq_default_unit_4c791a(void);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_uart_nema_child_514846(uint32_t, uint32_t);
extern volatile uint32_t audio_uart_nema_context_cell[];

void audio_uart_ambiq_scissor_4b1488(int32_t x, int32_t y,
                                      int32_t width, int32_t height) {
    volatile uint32_t *const state = (volatile uint32_t *)(uintptr_t)
        audio_uart_nema_context_cell[0];
    state[0x24 / 4] = (uint32_t)x;
    state[0x28 / 4] = (uint32_t)y;
    state[0x2c / 4] = (uint32_t)width;
    state[0x30 / 4] = (uint32_t)height;
    const uint32_t right = (uint32_t)x + (uint32_t)width;
    const uint32_t bottom = (uint32_t)y + (uint32_t)height;
    const uint32_t clipped_x = x < 0 ? 0u : (uint32_t)x;
    const uint32_t clipped_y = y < 0 ? 0u : (uint32_t)y;
    audio_uart_nema_child_514846(0x110u,
                                  (clipped_x & 0xffffu) | (clipped_y << 16));
    audio_uart_nema_child_514846(0x114u,
                                  (right & 0xffffu) | (bottom << 16));
}

void audio_uart_ambiq_clip_change_4b077e(uint32_t unit,
                                            const int32_t clip[4],
                                            uint32_t force) {
    if (unit == 0u) unit = audio_uart_ambiq_default_unit_4c791a();
    const int32_t *const previous =
        (const int32_t *)(uintptr_t)(unit + 0x74u);
    if (force != 0u || clip[0] != previous[0] || clip[1] != previous[1] ||
        clip[2] != previous[2] || clip[3] != previous[3]) {
        audio_uart_ambiq_scissor_4b1488(
            clip[0], clip[1], clip[2] - clip[0] + 1,
            clip[3] - clip[1] + 1);
        audio_uart_checksum_copy((void *)(uintptr_t)(unit + 0x74u), clip, 16u);
    }
}
