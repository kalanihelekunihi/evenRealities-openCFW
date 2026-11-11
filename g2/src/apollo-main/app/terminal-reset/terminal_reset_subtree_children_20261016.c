/* Stock Terminal subtree helpers at 0x5ea224 and 0x5ea2d4. */
#include <stdint.h>

extern uint32_t audio_uart_ring_primary_head_cell; /* stock 0x200746dc */
extern void lv_obj_set_style_pad_left(void *, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_right(void *, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_top(void *, uint32_t, uint32_t);
extern void lv_obj_set_style_pad_bottom(void *, uint32_t, uint32_t);

void audio_terminal_lv_style_four_5ea224(uint32_t object, uint32_t value,
                                         uint32_t selector) {
    void *page = (void *)(uintptr_t)object;
    lv_obj_set_style_pad_left(page, value, selector);
    lv_obj_set_style_pad_right(page, value, selector);
    lv_obj_set_style_pad_top(page, value, selector);
    lv_obj_set_style_pad_bottom(page, value, selector);
}

uint32_t audio_terminal_initial_image_y_5ea2d4(void) {
    uint32_t font = audio_uart_ring_primary_head_cell;
    int32_t height = *(const int32_t *)(const void *)(uintptr_t)(font + 0xcu);
    return height >= 17 ? (uint32_t)((height - 16) / 2) : 0u;
}
