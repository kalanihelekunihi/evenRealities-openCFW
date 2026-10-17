/* Apollo Main prep-note line count and scroll bounds, 0x5b4770 and 0x5b6a06..0x5b6a51. */
#include <stdint.h>

extern uint8_t audio_conversate_prep_note_ram_200d7630[];
extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern int32_t audio_uart_lv_obj_height_43fdda(uint32_t);

static uint32_t word(const volatile uint8_t *bytes, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(bytes + offset);
}

uint32_t audio_conversate_prep_note_line_count_5b4770(void) {
    const uint8_t *const state = audio_conversate_prep_note_ram_200d7630;
    return (uint32_t)state[0x109au] | ((uint32_t)state[0x109bu] << 8u);
}

int32_t audio_conversate_prep_scroll_max_5b6a06(void) {
    const volatile uint8_t *const ui = (const volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t note = word(ui, 0x24u);
    if (note == 0u) return 0;
    const int32_t height = audio_uart_lv_obj_height_43fdda(note);
    const int32_t extent = (int32_t)(audio_conversate_prep_note_line_count_5b4770() * 28u);
    return height < extent ? (int32_t)((uint32_t)extent - (uint32_t)height) : 0;
}

int32_t audio_conversate_prep_scroll_clamp_5b6a3a(int32_t requested) {
    const int32_t maximum = audio_conversate_prep_scroll_max_5b6a06();
    if (requested < 0) return 0;
    return requested <= maximum ? requested : maximum;
}
