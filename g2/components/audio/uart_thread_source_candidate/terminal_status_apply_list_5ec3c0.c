/* Stock Terminal interrupt-confirm list style and indicator layout. */
#include <stdint.h>

extern uint32_t audio_uart_ring_secondary_head_cell; /* stock 0x200746e0 */
extern uint32_t audio_lv_child_44dce2(uint32_t parent, uint32_t index);
extern uint32_t audio_uart_page_44104c(uint32_t rgb);
extern void audio_uart_page_44140e(uint32_t object, uint32_t color,
                                    uint32_t selector);
extern int32_t audio_uart_lv_obj_x_43fc70(void *object);
extern int32_t audio_uart_lv_obj_y_43fce0(void *object);
extern void audio_lv_object_position_43f09a(uint32_t object,
                                            uint32_t x, uint32_t y);
extern void audio_uart_page_43dfa4(uint32_t object, uint32_t flag);

static uint32_t word(const uint8_t *state, uint32_t offset) {
    return *(const uint32_t *)(const void *)(state + offset);
}

void audio_terminal_status_apply_list_position_5ec34e(uint32_t state) {
    if (state == 0u)
        return;
    const uint8_t *ui = (const uint8_t *)(uintptr_t)state;
    uint32_t indicator = word(ui, 0x23cu);
    uint32_t anchor = word(ui, 0x238u);
    if (indicator == 0u || anchor == 0u)
        return;
    const uint8_t *font = (const uint8_t *)(uintptr_t)
        audio_uart_ring_secondary_head_cell;
    int32_t height = *(const int32_t *)(const void *)(font + 12u);
    int32_t y = 8;
    if (height >= 17)
        y += (height - 16) / 2;
    if (ui[0x278u] == 1u)
        y += height + 2;
    int32_t x = audio_uart_lv_obj_x_43fc70((void *)(uintptr_t)anchor) - 20;
    y += audio_uart_lv_obj_y_43fce0((void *)(uintptr_t)anchor);
    audio_lv_object_position_43f09a(indicator, (uint32_t)x, (uint32_t)y);
    audio_uart_page_43dfa4(indicator, 1u);
}

void audio_terminal_status_apply_list_5ec3c0(uint32_t state) {
    if (state == 0u)
        return;
    const uint8_t *ui = (const uint8_t *)(uintptr_t)state;
    uint32_t anchor = word(ui, 0x238u);
    if (anchor == 0u)
        return;
    uint32_t first = audio_lv_child_44dce2(anchor, 0u);
    uint32_t second = audio_lv_child_44dce2(anchor, 1u);
    if (first == 0u || second == 0u)
        return;
    uint8_t selected = ui[0x278u] == 1u;
    uint32_t color = audio_uart_page_44104c(
        selected ? 0x00333333u : 0x00ffffffu);
    audio_uart_page_44140e(first, color, 0u);
    color = audio_uart_page_44104c(
        selected ? 0x00ffffffu : 0x00333333u);
    audio_uart_page_44140e(second, color, 0u);
    audio_terminal_status_apply_list_position_5ec34e(state);
}
