/* Stock Terminal type-two helpers at 0x597350 and 0x5eab8e. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* stock 0x2010fd20 */
extern uint32_t audio_td_ring_index_wrap(uint8_t *ring, uint16_t index);
extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_uart_compiler_move_439710(void *dst, const void *src, uint32_t size);
extern uint32_t audio_terminal_item_59737c(uint32_t index);
extern uint32_t audio_terminal_item_height_5ea67a(uint32_t item);
extern void audio_terminal_recompute_offsets_5ea6da(uint32_t first);

uint32_t audio_terminal_last_record_597350(void) {
    uint8_t *ring = audio_td_state + 0x1054u;
    uint16_t count = *(const uint16_t *)(const void *)(ring + 0x8500u);
    if (count == 0u)
        return 0u;
    uint32_t index = audio_td_ring_index_wrap(ring, (uint16_t)(count - 1u));
    return (uint32_t)(uintptr_t)(ring + (uint16_t)index * 0x214u);
}

void audio_terminal_list_rollover_5eab8e(void) {
    uint8_t *state = audio_terminal_ui_state_base;
    audio_uart_compiler_move_439710(state + 0x3cu, state + 0x3eu, 0x7eu);
    *(uint16_t *)(void *)(state + 0xbau) = 0u;
    uint32_t item = audio_terminal_item_59737c(0x3fu);
    *(uint16_t *)(void *)(state + 0xbau) = item != 0u
        ? (uint16_t)audio_terminal_item_height_5ea67a(item) : 0x1cu;
    audio_terminal_recompute_offsets_5ea6da(0u);
    state[0x1c2u] = 0u;
}
