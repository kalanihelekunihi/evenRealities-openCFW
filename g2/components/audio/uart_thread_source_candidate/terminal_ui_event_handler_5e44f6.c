/* Stock terminal UI registry callback 0x5e44f6, row 0x30. */
#include <stdint.h>

extern uint32_t audio_registry_ring_connect_enter_5e438e(uint32_t);
extern void audio_registry_ring_connect_leave_5e43be(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_tracepoint_reset_pull_478110(uint8_t);
extern void audio_ble_status_register_callback(void (*)(uint32_t, const void *));
extern void audio_terminal_runtime_event_callback_1(uint32_t, const void *);
extern void audio_terminal_ui_start_5e716c(uint32_t);
extern void audio_terminal_ui_status_5e7b74(uint32_t, uint32_t);
extern void audio_terminal_ui_tick_5e8008(void);
extern void audio_terminal_ui_stop_5e720c(void);
extern void audio_terminal_ui_exit_sync_5e42ec(void);
extern void audio_uart_page_58c238(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_terminal_display_queue_handle;
extern uint8_t audio_uart_registry_context_20003e50[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal.c";
static const char function[] = "Terminal_ui_event_handler";
static const char startup[] = "terminal display startup";
static const char startup_short[] = "[terminal]terminal display startup";
static const char shutdown[] = "terminal display exit";
static const char shutdown_short[] = "[terminal]terminal display exit";

uint32_t audio_uart_registry_callback_5e44f6(uint32_t event,
                                                const void *payload,
                                                uint32_t length,
                                                uint32_t context) {
    uint8_t incoming[8];
    audio_uart_buffer_zero(incoming, 8u, 0u);
    (void)audio_registry_ring_connect_enter_5e438e(0u);
    if (event == 2u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 0xb0u, startup);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c000000u, startup_short, startup_short);
        audio_tracepoint_reset_pull_478110(0u);
        audio_ble_status_register_callback(audio_terminal_runtime_event_callback_1);
        audio_terminal_ui_start_5e716c(context);
        audio_terminal_ui_status_5e7b74(1u, 0u);
        *(uint32_t *)(void *)(audio_uart_registry_context_20003e50 + 4u) =
            audio_terminal_display_queue_handle;
        audio_uart_page_58c238(audio_terminal_display_queue_handle, 250u, 0u);
        audio_terminal_ui_exit_sync_5e42ec();
    } else if (event == 3u) {
        if (payload != 0 && length >= 8u) {
            audio_uart_checksum_copy(incoming, payload, 8u);
            uint32_t word = (uint32_t)incoming[4] |
                            ((uint32_t)incoming[5] << 8u) |
                            ((uint32_t)incoming[6] << 16u) |
                            ((uint32_t)incoming[7] << 24u);
            audio_terminal_ui_status_5e7b74(incoming[0], word);
        }
    } else if (event == 4u) {
        audio_terminal_ui_tick_5e8008();
    } else if (event == 5u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 0xc3u, shutdown);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c000000u, shutdown_short, shutdown_short);
        audio_terminal_ui_exit_sync_5e42ec();
        audio_terminal_ui_stop_5e720c();
    }
    audio_registry_ring_connect_leave_5e43be();
    return 0u;
}
