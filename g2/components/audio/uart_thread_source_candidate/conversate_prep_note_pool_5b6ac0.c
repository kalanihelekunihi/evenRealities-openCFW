/* Apollo Main prep-note label pool 0x5b6ac0..0x5b6c47. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_prep_note_line_count_5b4770(void);
extern void audio_conversate_prep_note_line_text_5b4776(uint32_t, char *, uint32_t);
extern int32_t audio_conversate_prep_scroll_clamp_5b6a3a(int32_t);
extern int32_t audio_conversate_prep_scroll_max_5b6a06(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_49942e(uint32_t, const char *);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern int32_t audio_uart_lv_obj_height_43fdda(uint32_t);
extern int32_t audio_uart_lv_obj_content_width_43fe16(uint32_t);
extern int32_t audio_uart_lv_obj_y_43fce0(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);

static volatile uint8_t *ui_state(void) {
    return (volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
}

static uint32_t word(const volatile uint8_t *state, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(state + offset);
}

void audio_conversate_prep_note_pool_bind_5b6ac0(uint32_t first) {
    volatile uint8_t *const state = ui_state();
    const uint16_t count = (uint16_t)audio_conversate_prep_note_line_count_5b4770();
    for (uint32_t slot = 0; slot < 12u; ++slot) {
        const uint32_t label = word(state, 0x30u + slot * 4u);
        if (label == 0u) continue;
        const uint16_t line = (uint16_t)(first + slot);
        audio_uart_page_43f09a(label, 0u, (uint32_t)line * 28u);
        if (line < count) {
            char text[129];
            audio_uart_buffer_zero(text, 129u, 0u);
            audio_conversate_prep_note_line_text_5b4776(line, text, 129u);
            audio_uart_page_49942e(label, text);
            audio_uart_page_43dfa4(label, 1u);
        } else {
            audio_uart_page_49942e(label, "");
            audio_uart_page_43ded4(label, 1u);
        }
    }
    *(volatile uint16_t *)(void *)(state + 0x60u) = (uint16_t)first;
}

void audio_conversate_prep_note_pool_show_5b6b58(int32_t requested_scroll) {
    volatile uint8_t *const state = ui_state();
    if (word(state, 0x28u) == 0u) return;
    const int32_t scroll = audio_conversate_prep_scroll_clamp_5b6a3a(requested_scroll);
    const uint16_t count = (uint16_t)audio_conversate_prep_note_line_count_5b4770();
    uint16_t first = 0u;
    if (count > 12u) {
        const int32_t row = scroll / 28;
        if ((uint16_t)row >= 3u) first = (uint16_t)(row - 2);
        const uint16_t max_first = (uint16_t)(count - 12u);
        if (max_first < first) first = max_first;
    }
    if (first != *(const volatile uint16_t *)(const void *)(state + 0x60u))
        audio_conversate_prep_note_pool_bind_5b6ac0(first);
    const uint32_t note = word(state, 0x24u);
    const uint32_t thumb = word(state, 0x2cu);
    if (note == 0u || thumb == 0u) return;
    const int32_t full_height = (int32_t)((uint32_t)count * 28u);
    const int32_t view_height = audio_uart_lv_obj_height_43fdda(note);
    const int32_t maximum = audio_conversate_prep_scroll_max_5b6a06();
    if (view_height >= full_height || maximum <= 0) {
        audio_uart_page_43ded4(thumb, 1u);
        return;
    }
    int32_t thumb_height = (int32_t)((uint32_t)view_height * (uint32_t)view_height) / full_height;
    if (thumb_height < 28) thumb_height = 28;
    if (view_height < thumb_height) thumb_height = view_height;
    const int32_t x = audio_uart_lv_obj_content_width_43fe16(word(state, 0x1cu)) - 10;
    const int32_t y = (int32_t)((uint32_t)(view_height - thumb_height) * (uint32_t)scroll) / maximum +
                      audio_uart_lv_obj_y_43fce0(note);
    audio_uart_page_43f4c0(thumb, 2u, (uint32_t)thumb_height);
    audio_uart_page_43f09a(thumb, (uint32_t)x, (uint32_t)y);
    audio_uart_page_43dfa4(thumb, 1u);
}
