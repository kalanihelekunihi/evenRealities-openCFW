/* Stock Terminal FSM actions 0x5e5a7e and 0x5e5a94. */
#include <stdint.h>

extern const uint8_t *audio_td_state_ptr(void);
extern void audio_terminal_ui_notification_restore_5ebfae(uint32_t record);
extern uint8_t audio_terminal_ui_timer_state_20073c38[0x18]; /* RAM 0x20073c38 */
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_timer.c";
static const char function[] = "terminal_timer_asr_result_timeout_start";
static const char message[] = "asr result timeout start, due in %d ms";
static const char short_message[] =
    "[terminal.timer]asr result timeout start, due in %d ms";

void audio_terminal_asr_timeout_start_5e7f6e(void) {
    uint8_t *timer = audio_terminal_ui_timer_state_20073c38 + 8u;
    timer[0] = 1u;
    uint32_t deadline = g2_flashdb_candidate_tick() + 20000u;
    *(uint32_t *)(void *)(timer + 4u) = deadline;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x46u,
                           message, 20000u);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c400000u, short_message,
                                    short_message, 20000u);
}

int32_t audio_terminal_ui_action_5e5a7e(uint32_t old_state, uint32_t event_payload) {
    (void)event_payload;
    (void)old_state;
    const uint8_t *state = audio_td_state_ptr();
    if (*(const uint16_t *)(const void *)(state + 0x802u) != 0u)
        audio_terminal_ui_notification_restore_5ebfae((uint32_t)(uintptr_t)state);
    return 0;
}

int32_t audio_terminal_ui_action_5e5a94(uint32_t old_state, uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_asr_timeout_start_5e7f6e();
    return audio_terminal_ui_action_5e5a7e(old_state, event_payload);
}
