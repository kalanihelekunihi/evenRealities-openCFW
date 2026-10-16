/* Stock Terminal item text-height calculation at 0x5ea67a. */
#include <stdint.h>

extern uint32_t audio_uart_ring_primary_head_cell; /* stock 0x200746dc */
extern void audio_uart_buffer_zero(void *buffer, uint32_t length, uint32_t fill);
extern int32_t audio_terminal_item_spacing_5ea2c2(void);
extern void audio_uart_page_event_calculate_489546(void *output, const char *text,
                                                    const void *font, int32_t letter_spacing,
                                                    int32_t line_spacing, int32_t max_width,
                                                    uint32_t flags);

uint32_t audio_terminal_item_height_5ea67a(uint32_t item) {
    uint32_t measured[2];
    audio_uart_buffer_zero(measured, 8u, 0u);
    if (item == 0u || *(const uint8_t *)(const void *)(uintptr_t)(item + 2u) == 0u)
        return 0x1cu;
    uint32_t font = audio_uart_ring_primary_head_cell;
    if (font == 0u)
        return 0x1cu;
    int32_t spacing = audio_terminal_item_spacing_5ea2c2();
    audio_uart_page_event_calculate_489546(measured,
        (const char *)(uintptr_t)(item + 2u), (const void *)(uintptr_t)font,
        0, spacing, 0x21a, 0u);
    int32_t height = (int32_t)measured[1];
    if (height < 0x1c)
        height = 0x1c;
    return (uint32_t)(0x1c * ((height + 0x1b) / 0x1c));
}
