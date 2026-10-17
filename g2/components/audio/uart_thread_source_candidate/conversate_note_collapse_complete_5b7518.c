/* Apollo Main Conversate note collapse completion, 0x5b7518..0x5b7555. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern void audio_conversate_lv_object_delete_44d90e(uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_uart_page_43dfa4(uint32_t, uint32_t);

static uint32_t word(const volatile uint8_t *bytes, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(bytes + offset);
}

static void put_word(volatile uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(bytes + offset) = value;
}

uint32_t audio_conversate_note_collapse_complete_5b7518(
    uint32_t arg0, uint32_t arg1, uint32_t arg2, uint32_t passthrough) {
    (void)arg0;
    (void)arg1;
    (void)arg2;
    volatile uint8_t *const state = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    audio_conversate_lv_object_delete_44d90e(word(state, 0x1cu));
    put_word(state, 0x1cu, 0u);
    state[0x98u] = 0u;
    put_word(state, 0x24u, 0u);
    put_word(state, 0x28u, 0u);
    put_word(state, 0x2cu, 0u);
    state[0x60u] = 0u;
    state[0x61u] = 0u;
    audio_uart_buffer_zero((void *)(uintptr_t)(state + 0x30u), 0x30u, 0u);
    (void)audio_uart_page_43dfa4(word(state, 0x7cu), 1u);
    return passthrough;
}
