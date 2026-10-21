/* Native Conversate_ui_event_handler 0x5b06aa..0x5b08a1. */
#include <stdint.h>

extern uint8_t audio_conversate_machine_context_200e3aec[];
extern uint8_t audio_uart_registry_context_200004d8[];
extern uint32_t audio_conversate_ui_start_tick_20074390;
extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint32_t audio_conversate_enter_5b01ca(void);
extern void audio_conversate_leave_5b0284(void);
extern void audio_conversate_success_5b03c2(void);
extern void audio_conversate_reply_list_clear_5b43d4(void);
extern void audio_conversate_prep_note_reset_5b473a(void);
extern void audio_conversate_transcribe_reset_5b430e(void);
extern uint32_t g2_flashdb_candidate_tick(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void audio_tracepoint_reset_pull_478110(uint8_t);
extern void audio_conversate_ui_start_5b14ce(uint32_t);
extern void audio_conversate_ui_action_5b1724(uint32_t, uint32_t);
extern void audio_conversate_ui_stop_5b03d8(void);
extern void audio_conversate_ui_cancel_5b23ae(void);
extern void audio_conversate_ui_cleanup_5b3d62(void);
extern void audio_conversate_ui_exit_child_59624e(void);
extern void audio_conversate_ui_exit_finalize_5b156c(void);
extern uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t);
extern void audio_ble_param_reset_delayed_event(uint32_t);
extern uint32_t audio_conversate_ui_close_notify_5b1d2a(const void *);
extern uint8_t audio_uart_device_role_get(void);
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t, uint32_t,
                                                 uint32_t, uint32_t);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t, uint32_t,
                                                  const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "Conversate_ui_event_handler";
static const char startup[] = "Conversate display startup";
static const char startup_short[] = "[conversate]Conversate display startup";
static const char exiting[] = "Conversate display exit";
static const char exiting_short[] = "[conversate]Conversate display exit";
static const char notify[] = "notify app to close";
static const char notify_short[] = "[conversate]notify app to close";

static void log_event(uint32_t line, const char *message, const char *short_message) {
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c000000u, short_message, short_message);
}

void audio_uart_registry_callback_5b06aa(uint32_t event, const void *input,
                                           uint32_t unused, uint32_t extra) {
    (void)unused;
    uint8_t local[8];
    audio_uart_buffer_zero(local, 8u, 0u);
    (void)audio_conversate_enter_5b01ca();
    if (event == 2u) {
        log_event(266u, startup, startup_short);
        audio_conversate_ui_start_tick_20074390 = g2_flashdb_candidate_tick();
        local[0] = audio_conversate_machine_context_200e3aec[0] ? 3u : 1u;
        audio_tracepoint_reset_pull_478110(0u);
        audio_conversate_success_5b03c2();
        audio_conversate_ui_start_5b14ce(extra);
        audio_conversate_ui_action_5b1724(local[0], 0u);
        *(uint32_t *)(void *)(audio_uart_registry_context_200004d8 + 4u) =
            audio_conversate_ui_app_id_200743a0;
    } else if (event == 3u) {
        (void)audio_queue_copy_bytes(local, input, 8u);
        uint32_t word = (uint32_t)local[4] | ((uint32_t)local[5] << 8) |
                        ((uint32_t)local[6] << 16) | ((uint32_t)local[7] << 24);
        audio_conversate_ui_action_5b1724(local[0], word);
    } else if (event == 4u) {
        audio_conversate_ui_stop_5b03d8();
        audio_conversate_ui_cancel_5b23ae();
        audio_conversate_ui_cleanup_5b3d62();
    } else if (event == 5u) {
        log_event(290u, exiting, exiting_short);
        audio_conversate_reply_list_clear_5b43d4();
        audio_conversate_prep_note_reset_5b473a();
        audio_conversate_transcribe_reset_5b430e();
        audio_conversate_ui_exit_child_59624e();
        audio_conversate_ui_exit_finalize_5b156c();
        (void)audio_terminal_reset_mode_notice_54f50e(4u);
        audio_ble_param_reset_delayed_event(10000u);
        if (audio_conversate_machine_context_200e3aec[0] == 1u) {
            log_event(300u, notify, notify_short);
            uint8_t close[2];
            audio_uart_buffer_zero(close, 2u, 0u);
            close[0] = 2u;
            close[1] = 0u;
            (void)audio_conversate_ui_close_notify_5b1d2a(close);
        }
        audio_uart_buffer_zero(audio_conversate_machine_context_200e3aec, 6u, 0u);
        uint32_t elapsed = g2_flashdb_candidate_tick() -
                           audio_conversate_ui_start_tick_20074390;
        uint64_t scaled = (uint64_t)elapsed * 1000u;
        uint32_t duration = (uint32_t)audio_uart_ring_u64_div_47cc60(
            (uint32_t)scaled, (uint32_t)(scaled >> 32), 1000u, 0u);
        if (audio_uart_device_role_get() == 1u) {
            uint32_t descriptor[2] = {1u, duration};
            audio_uart_ring_wear_persist_48eb32(0x40103u, 2u, descriptor);
        }
    }
    audio_conversate_leave_5b0284();
}
