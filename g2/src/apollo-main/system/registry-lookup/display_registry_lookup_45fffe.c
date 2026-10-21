/* Apollo two-level registry lookup, native 0x45fffe..0x46004f. */
#include <stdint.h>

extern const void *audio_uart_display_context_list_cell;
extern const void *audio_uart_display_context_active_cell;

static uint32_t read32(uint32_t address) {
    return *(volatile const uint32_t *)(uintptr_t)address;
}

uint32_t audio_uart_page_45fffe(uint32_t fallback, uint32_t index) {
    uint32_t first = (uint32_t)(uintptr_t)audio_uart_display_context_active_cell;
    if (first == 0u || index == 0xffffu) return fallback;
    uint32_t table = read32(first + 4u);
    if (table != 0u) {
        uint32_t value = read32(table + index * 4u);
        if (value != 0u) return value;
    }
    uint32_t second_root = (uint32_t)(uintptr_t)audio_uart_display_context_list_cell;
    uint32_t second = read32(second_root);
    if (first == second) return fallback;
    table = read32(second + 4u);
    if (table == 0u) return fallback;
    uint32_t value = read32(table + index * 4u);
    return value != 0u ? value : fallback;
}
