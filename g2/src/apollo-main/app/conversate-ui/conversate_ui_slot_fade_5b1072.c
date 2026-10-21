/* Native Conversate list-button style setter 0x5b1072..0x5b114f. */
#include <stdint.h>

extern uint32_t audio_terminal_ui_object_valid_43e2ea(uint32_t);
extern void audio_terminal_session_row_show_5897ee(uint32_t);
extern void audio_terminal_session_row_hide_589892(uint32_t);
extern void audio_uart_page_44130c(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *,
                                      const char *, ...);

static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_list_button_set";
static const char invalid[] =
    "Set list button style skipped: button is invalid";
static const char invalid_short[] =
    "[conversate.ui]Set list button style skipped: button is invalid";
static const char unknown[] = "Unknown select mode: %d";
static const char unknown_short[] =
    "[conversate.ui]Unknown select mode: %d";

void audio_conversate_ui_slot_fade_5b1072(uint32_t object, uint32_t mode) {
    if (object == 0u || audio_terminal_ui_object_valid_43e2ea(object) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, source, function, 0x122u,
                               invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u, invalid_short,
                                        invalid_short);
        return;
    }
    if ((uint8_t)mode == 1u) {
        audio_terminal_session_row_show_5897ee(object);
        audio_uart_page_44130c(object, 0xffu, 0u);
        return;
    }
    if ((uint8_t)mode == 0u) {
        audio_terminal_session_row_hide_589892(object);
        audio_uart_page_44130c(object, 0u, 0u);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, source, function, 0x132u,
                           unknown, (uint8_t)mode);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x08400000u, unknown_short,
                                    unknown_short, (uint8_t)mode);
}
