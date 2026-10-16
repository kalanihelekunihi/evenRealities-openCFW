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

/* The stock return restores incoming R3, while updating the live timer row. */
#ifndef OPENCFW_TIMER_STOP_ONLY
__attribute__((naked)) uint32_t audio_even_ai_common_timer_start_4e2e62(
    uint32_t duration __attribute__((unused))) {
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "mov r4, r0\n"
        "bl audio_uart_device_role_get\n"
        "uxtb r0, r0\n"
        "cmp r0, #1\n"
        "bne 1f\n"
        "ldr r5, =audio_even_ai_common_timer_state_20074008\n"
        "bl g2_kernel_candidate_os_get_tick\n"
        "str r0, [r5]\n"
        "str r4, [r5, #4]\n"
        "movs r0, #1\n"
        "strb r0, [r5, #8]\n"
        "strb r0, [r5, #9]\n"
        "1:\n"
        "pop {r0, r4, r5, pc}\n");
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

/* Stock passes incoming R0 to the common timer, then 10000 to heartbeat. */
#ifndef OPENCFW_TIMER_STOP_ONLY
__attribute__((naked)) uint32_t audio_even_ai_timer_start_all_4e31a0(
    uint32_t duration __attribute__((unused))) {
    __asm__ volatile(
        "push {r7, lr}\n"
        "bl audio_even_ai_common_timer_start_4e2e62\n"
        "movw r0, #10000\n"
        "bl audio_even_ai_heartbeat_timer_start_4e304c\n"
        "pop {r0, pc}\n");
}
#endif
