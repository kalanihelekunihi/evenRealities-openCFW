/* Apollo Main register_all_foreground_ui_pages, 0x442456..0x442521. */
#include <stdint.h>

extern uint8_t audio_uart_user_registry_rows[128][16];
extern volatile uint32_t audio_uart_user_registry_count;
extern uint32_t audio_uart_display_audio_handle;
extern uint32_t audio_uart_display_audio_terminal_mode_45bbf4(void);
extern void *audio_uart_display_audio_enqueue_45f3c8(void *, void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "display_thread";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c";
static const char function[] = "register_all_foreground_ui_pages";
static const char terminal_message[] =
    "terminal mode,drop it,startup foreground app id = %d";
static const char terminal_short[] =
    "[display_thread]terminal mode,drop it,startup foreground app id = %d";

static uint32_t word(const uint8_t *row, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(row + offset);
}

/* Stock 0x442456 (register_all_foreground_ui_pages) */
int32_t audio_uart_display_current_set(uint32_t type, uint32_t app_id)
{
    if (type != 2u) return -1;
    if (audio_uart_display_audio_terminal_mode_45bbf4() == 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, source, function, 0x80u,
                               terminal_message, app_id);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c400000u, terminal_short,
                                        terminal_short, app_id);
        return -1;
    }

    for (int32_t index = 0; index < (int32_t)audio_uart_user_registry_count;
         ++index) {
        uint8_t *const row = audio_uart_user_registry_rows[index];
        uint8_t *const configuration = (uint8_t *)(uintptr_t)word(row, 12u);
        if (configuration[11] != 1u || word(row, 8u) == 0u ||
            *(const uint32_t *)(const void *)configuration == app_id)
            continue;
        uint8_t *const state = (uint8_t *)(uintptr_t)audio_uart_display_audio_handle;
        const uint32_t context = *(const uint32_t *)(const void *)(state + 0x20u);
        void (*const callback)(uint32_t, uint32_t, uint32_t, uint32_t) =
            (void (*)(uint32_t, uint32_t, uint32_t, uint32_t))
                (uintptr_t)word(row, 8u);
        callback(type, 0u, 0u, context);
        (void)audio_uart_display_audio_enqueue_45f3c8(state, configuration);
    }
    return 0;
}
