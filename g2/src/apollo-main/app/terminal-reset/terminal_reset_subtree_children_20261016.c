/* Stock Terminal subtree helpers at 0x5ea224 and 0x5ea2d4. */
#include <stdint.h>

extern uint32_t audio_uart_ring_primary_head_cell; /* stock 0x200746dc */
extern void audio_uart_page_44122a(void *, uint32_t, uint32_t);
extern void audio_uart_page_441238(void *, uint32_t, uint32_t);
extern void audio_uart_page_44120e(void *, uint32_t, uint32_t);
extern void audio_uart_page_44121c(void *, uint32_t, uint32_t);

void audio_terminal_lv_style_four_5ea224(uint32_t object, uint32_t value,
                                         uint32_t selector) {
    void *page = (void *)(uintptr_t)object;
    audio_uart_page_44122a(page, value, selector);
    audio_uart_page_441238(page, value, selector);
    audio_uart_page_44120e(page, value, selector);
    audio_uart_page_44121c(page, value, selector);
}

uint32_t audio_terminal_initial_image_y_5ea2d4(void) {
    uint32_t font = audio_uart_ring_primary_head_cell;
    int32_t height = *(const int32_t *)(const void *)(uintptr_t)(font + 0xcu);
    return height >= 17 ? (uint32_t)((height - 16) / 2) : 0u;
}
