/* Stock Terminal timer processing callback at 0x5e8008. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_timer_state_20073c38[0x18];
extern uint8_t audio_terminal_ui_mode; /* stock base+0x275 */
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t audio_terminal_timer_expired_5e7ea4(const uint8_t *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_terminal_encode_voice_input_5cec72(const uint8_t *);
extern uint32_t audio_terminal_request_display(uint8_t, uint32_t);
extern uint32_t audio_td_counter_b_get(void);
extern uint32_t audio_td_record_elapsed_get_59769c(uint32_t, uint32_t *);

static const char module[] = "terminal.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_timer.c";
static const char function[] = "terminal_timer_process_auto_reflash";
static const char voice_message[] = "voice recording 60s timeout";
static const char voice_short[] = "[terminal.timer]voice recording 60s timeout";
static const char asr_message[] = "asr result wait 20s timeout, back to idle";
static const char asr_short[] =
    "[terminal.timer]asr result wait 20s timeout, back to idle";

static uint32_t load32(const uint8_t *p) {
    return *(const uint32_t *)(const void *)p;
}

static void store32(uint8_t *p, uint32_t value) {
    *(uint32_t *)(void *)p = value;
}

void audio_terminal_ui_tick_5e8008(void) {
    if (audio_uart_device_role_get() != 1u)
        return;
    uint8_t *const timers = audio_terminal_ui_timer_state_20073c38;
    uint32_t tick = g2_flashdb_candidate_tick();
    if (audio_terminal_timer_expired_5e7ea4(timers, tick) != 0u) {
        timers[0] = 0u;
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 0x62u, voice_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c000000u, voice_short, voice_short);
        uint8_t command;
        audio_uart_buffer_zero(&command, 1u, 0u);
        command = 3u;
        (void)audio_terminal_encode_voice_input_5cec72(&command);
        (void)audio_terminal_request_display(9u, 1u);
    }
    if (audio_terminal_timer_expired_5e7ea4(timers + 8u, tick) != 0u) {
        timers[8] = 0u;
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x6du, asr_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u, asr_short, asr_short);
        (void)audio_terminal_request_display(0x0cu, 0u);
    }
    if (audio_terminal_ui_mode == 7u) {
        uint32_t session = audio_td_counter_b_get();
        uint32_t elapsed = 0u;
        if (audio_td_record_elapsed_get_59769c(session, &elapsed) == 0u) {
            store32(timers + 0x10u, 0u);
            store32(timers + 0x14u, 0u);
        } else if (load32(timers + 0x10u) != session ||
                   load32(timers + 0x14u) != elapsed) {
            store32(timers + 0x10u, session);
            store32(timers + 0x14u, elapsed);
            (void)audio_terminal_request_display(0x14u, elapsed);
        }
    } else {
        store32(timers + 0x10u, 0u);
        store32(timers + 0x14u, 0u);
    }
}
