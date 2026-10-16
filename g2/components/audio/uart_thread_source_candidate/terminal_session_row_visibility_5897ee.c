/* Stock list-animation row show/hide walkers, 0x5897ee and 0x589892. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_uart_lv_child_count_44ddea(uint32_t);
extern uint32_t audio_uart_lv_child_get_44dce2(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_class_is_43e2d4(uint32_t, const void *);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4413ce(uint32_t, uint32_t, uint32_t);
extern const uint8_t audio_uart_page_class_7561bc[];
extern const uint8_t audio_uart_image_class_756108[];

static const char module[] = "list_anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\list_anim.c";
static const char invalid[] = "obj is NULL";
static const char invalid_short[] = "[list_anim]obj is NULL";

static void log_null(const char *function, uint32_t line) {
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, path, function, line, invalid);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x08000000u, invalid_short,
                                    invalid_short);
}

static void set_row(uint32_t object, uint32_t show) {
    if (object == 0u) {
        log_null(show ? "list_anim_set_bright" : "list_anim_set_dim",
                 show ? 0x11eu : 0x13eu);
        return;
    }
    const uint32_t count = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t index = 0; index < count; ++index) {
        const uint32_t child = audio_uart_lv_child_get_44dce2(object, index);
        if (child == 0u)
            continue;
        if (audio_uart_lv_class_is_43e2d4(child,
                                          audio_uart_image_class_756108)) {
            audio_uart_page_4413ce(child, show ? 0xffu : 0x33u, 0u);
        } else if (audio_uart_lv_class_is_43e2d4(
                       child, audio_uart_page_class_7561bc)) {
            const uint32_t color =
                audio_uart_page_44104c(show ? 0x00ffffffu : 0x00444444u);
            audio_uart_page_44140e(child, color, 0u);
        } else {
            set_row(child, show);
        }
    }
}

void audio_terminal_session_row_show_5897ee(uint32_t object) {
    set_row(object, 1u);
}

void audio_terminal_session_row_hide_589892(uint32_t object) {
    set_row(object, 0u);
}
