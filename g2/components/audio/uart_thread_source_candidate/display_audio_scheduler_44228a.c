/* Apollo display registration dispatch, stock 0x44228a..0x442452. */
#include <stdint.h>

extern volatile uint32_t audio_uart_user_registry_count; /* RAM 0x200744d4 */
extern uint8_t audio_uart_user_registry_rows[];          /* RAM 0x20066230 */
extern uint32_t audio_uart_display_audio_handle;        /* RAM 0x200744d0 */
extern uint32_t audio_uart_display_mode;                /* RAM 0x200744dc */
extern uint32_t audio_uart_display_background;          /* RAM 0x200744e0 */
extern uint32_t audio_uart_display_audio_terminal_mode_45bbf4(void);
extern uint32_t audio_uart_display_audio_enqueue_45f3c8(void *, void *);
extern uint32_t audio_uart_display_audio_route_45f876(void *, uint32_t);
extern uint32_t audio_uart_display_audio_set_mode_45fe32(uint32_t, uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char log_module[] = "display_thread";
static const char log_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c";
static const char log_function[] = "call_ui_event_callback_by_id";
static const char mode_message[] = "set %d animation mode to alt";
static const char mode_compact[] = "[display_thread]set %d animation mode to alt";
static const char missing_message[] = "No callback found for applicationID: %d";
static const char missing_compact[] =
    "[display_thread]No callback found for applicationID: %d";

static void log_mode(uint32_t id) {
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(4u, log_module, log_path, log_function,
                           0x6cu, mode_message, id);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, mode_compact, mode_compact, id);
}

static void log_missing(uint32_t id) {
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(2u, log_module, log_path, log_function,
                           0x7au, missing_message, id);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x08400000u, missing_compact,
                                    missing_compact, id);
}

static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

typedef void (*registry_callback)(uint32_t, uint32_t, uint32_t, uint32_t);

void audio_uart_display_audio_schedule_44228a(uint32_t id, uint32_t operation,
                                               uint32_t arg0, uint32_t arg1) {
    for (uint32_t i = 0; i < audio_uart_user_registry_count; ++i) {
        uint8_t *row = audio_uart_user_registry_rows + i * 16u;
        if (load32(row) != id) continue;
        uint32_t callback = load32(row + 8u);
        if (callback == 0u) continue;
        uint8_t *config = (uint8_t *)(uintptr_t)load32(row + 12u);
        uint8_t *current = (uint8_t *)(uintptr_t)audio_uart_display_audio_handle;
        if (config[11] == 0u) {
            if (audio_uart_display_audio_terminal_mode_45bbf4() != 0u &&
                load32(config) != 0x30u) return;
            ((registry_callback)(uintptr_t)callback)(operation, arg0, arg1,
                                                     load32(current + 28u));
            if (operation == 2u) {
                audio_uart_display_mode = 1u;
                (void)audio_uart_display_audio_enqueue_45f3c8(current, config);
            }
            return;
        }
        if (config[11] != 1u ||
            audio_uart_display_audio_terminal_mode_45bbf4() != 0u) return;
        ((registry_callback)(uintptr_t)callback)(operation, arg0, arg1,
                                                 load32(current + 32u));
        if (operation == 2u) {
            audio_uart_display_mode = 2u;
            audio_uart_display_background = load32(row);
            (void)audio_uart_display_audio_enqueue_45f3c8(current, config);
            if (audio_uart_display_background == 7u ||
                audio_uart_display_background == 4u) {
                log_mode(audio_uart_display_background);
                (void)audio_uart_display_audio_set_mode_45fe32(
                    audio_uart_display_background, 1u);
            }
            (void)audio_uart_display_audio_route_45f876(current, load32(config));
        }
        return;
    }
    log_missing(id);
}

/* The display-thread source calls the same stock entry with a pointer-shaped
 * third argument. Keep that source-level interface explicit. */
void audio_uart_display_notify(uint32_t id, uint32_t operation,
                               const void *payload, uint32_t length) {
    audio_uart_display_audio_schedule_44228a(
        id, operation, (uint32_t)(uintptr_t)payload, length);
}
