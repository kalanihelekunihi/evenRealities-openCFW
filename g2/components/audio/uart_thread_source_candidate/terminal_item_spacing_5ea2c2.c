/* Stock Terminal item line-spacing calculation at 0x5ea2c2. */
#include <stdint.h>

extern uint32_t audio_uart_ring_primary_head_cell; /* stock 0x200746dc */

int32_t audio_terminal_item_spacing_5ea2c2(void) {
    uint32_t font = audio_uart_ring_primary_head_cell;
    uint32_t line_height = *(const uint32_t *)(const void *)(uintptr_t)(font + 0xcu);
    return (int32_t)(0x1cu - line_height);
}
