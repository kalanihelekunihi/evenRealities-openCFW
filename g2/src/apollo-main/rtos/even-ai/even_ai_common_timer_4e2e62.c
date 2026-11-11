/* Native EvenAI common timer start/stop and timer-start wrapper. */
#include <stdint.h>

#ifdef OPENCFW_TIMER_STOP_ONLY
extern uint8_t audio_even_ai_common_timer_state_20074008[10];
#else
uint8_t audio_even_ai_common_timer_state_20074008[10]
    __attribute__((section(".bss.opencfw.evenai.common.timer"), aligned(4), used));
#endif

#ifndef OPENCFW_TIMER_STOP_ONLY
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t g2_kernel_candidate_os_get_tick(void);
extern void audio_even_ai_heartbeat_timer_start_4e304c(uint32_t);
#endif
#ifndef OPENCFW_TIMER_START_ONLY
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "even_ai.timer";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai_timer.c";
static const char function[] = "even_ai_common_timer_mgr_stop";
static const char short_message[] = "[even_ai.timer]even_ai_common_timer_mgr_stop";
#endif

/* Stock 0x4E2E62 (even_ai_common_timer_mgr_start). Only the glasses role 1
 * arms the row: start tick, duration, then the two active flags. The stock
 * epilogue popped the caller's R3 into R0; every caller discards the result
 * (even_ai_timer.c, ui_even_ai_stream.c and the wrapper below), so 0. */
#ifndef OPENCFW_TIMER_STOP_ONLY
uint32_t audio_even_ai_common_timer_start_4e2e62(uint32_t duration) {
    if (audio_uart_device_role_get() == 1u) {
        uint8_t *const row = audio_even_ai_common_timer_state_20074008;
        const uint32_t now = g2_kernel_candidate_os_get_tick();
        __builtin_memcpy(row, &now, 4u);
        __builtin_memcpy(row + 4u, &duration, 4u);
        row[8] = 1u;
        row[9] = 1u;
    }
    return 0u;
}
#endif

#ifndef OPENCFW_TIMER_START_ONLY
void audio_even_ai_common_timer_stop_4e2e86(void) {
    audio_even_ai_common_timer_state_20074008[9] = 0u;
    audio_even_ai_common_timer_state_20074008[8] = 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x39u, function);
    uint32_t flags = audio_log_flags();
    if ((flags & 1u) || (!(flags & 1u) && (audio_log_flags() & 4u)))
        (void)compressed_log_output(0x10000000u, short_message, short_message);
}
#endif

/* Stock 0x4E31A0 (even_ai_timer_start_all): the common timer with the
 * caller's duration, then the 10 s heartbeat. The stock epilogue popped the
 * caller's R7 into R0; every caller discards the result, so 0. */
#ifndef OPENCFW_TIMER_STOP_ONLY
uint32_t audio_even_ai_timer_start_all_4e31a0(uint32_t duration) {
    (void)audio_even_ai_common_timer_start_4e2e62(duration);
    audio_even_ai_heartbeat_timer_start_4e304c(10000u);
    return 0u;
}
#endif
