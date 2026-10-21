/* Native Conversate current-button visible-position getter, 0x5b0b58..0x5b0c17. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] =
    "conversate_ui_get_current_button_dispaly_position";
static const char null_button[] = "Current button is NULL";
static const char null_button_short[] =
    "[conversate.ui]Current button is NULL";
static const char position[] =
    "Current button index: %d, visible position: %d";
static const char position_short[] =
    "[conversate.ui]Current button index: %d, visible position: %d";

static uint32_t word(const volatile uint8_t *p, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(p + offset);
}

int32_t audio_conversate_tag_visible_index_5b0b58(void) {
    const volatile uint8_t *const ui = (const volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    if (word(ui, 0x80u) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, source, function, 0x41u,
                               null_button);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, null_button_short,
                                        null_button_short);
        return -2;
    }
    const int32_t scroll = audio_uart_lv_obj_y_44e498(
        (void *)(uintptr_t)word(ui, 0x64u));
    const uint32_t index = word(ui, 0x84u);
    const int32_t visible = (int32_t)(index - (uint32_t)(scroll / 0x28));
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, source, function, 0x48u,
                           position, index, visible);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10800000u, position_short,
                                    position_short, index, visible);
    return visible;
}
