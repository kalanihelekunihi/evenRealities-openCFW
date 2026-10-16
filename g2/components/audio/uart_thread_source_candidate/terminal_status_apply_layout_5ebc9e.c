/* Stock Terminal status-indicator layout child at 0x5ebc9e. */
#include <stdint.h>

extern uint32_t audio_uart_ring_secondary_head_cell; /* stock 0x200746e0 */
extern int32_t audio_uart_lv_obj_x_43fc70(void *object);
extern int32_t audio_uart_lv_obj_y_43fce0(void *object);
extern void audio_lv_object_position_43f09a(uint32_t object,
                                            uint32_t x,
                                            uint32_t y);

void audio_terminal_status_apply_layout_5ebc9e(uint32_t state,
                                                 uint32_t mode) {
    if (state == 0u)
        return;
    const uint8_t *ui = (const uint8_t *)(uintptr_t)state;
    uint32_t indicator = *(const uint32_t *)(const void *)(ui + 0x208u);
    uint32_t anchor = *(const uint32_t *)(const void *)(ui + 0x200u);
    if (indicator == 0u || anchor == 0u)
        return;
    const uint8_t *font = (const uint8_t *)(uintptr_t)
        audio_uart_ring_secondary_head_cell;
    int32_t height = *(const int32_t *)(const void *)(font + 12u);
    int32_t y = 8;
    if (height >= 17)
        y += (height - 16) / 2;
    int32_t x = audio_uart_lv_obj_x_43fc70((void *)(uintptr_t)anchor) - 20;
    y += audio_uart_lv_obj_y_43fce0((void *)(uintptr_t)anchor);
    if ((uint8_t)mode == 1u)
        y += height + 2;
    audio_lv_object_position_43f09a(indicator, (uint32_t)x, (uint32_t)y);
}
