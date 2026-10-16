/* Stock EvenAI display start, refresh and stop dispatcher, 0x4e1fd2. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint8_t audio_even_ai_service_state_2006ed10[0x218];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t,
                                                    uint32_t, uint32_t);
extern uint32_t audio_log_wake_allowed(void);
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t);
extern void audio_uart_master_display_start(uint32_t, const void *, uint16_t,
                                             uint32_t);
extern void audio_uart_master_display_refresh(uint32_t, const void *, uint16_t,
                                               uint32_t);
extern void audio_uart_master_display_stop(uint32_t, const void *, uint16_t,
                                            uint32_t);

static const char module[] = "even_ai.page";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai.c";
static const char function[] = "even_ai_display_ctrl";
static const char start_message[] = "try to start evenai";
static const char start_short[] = "[even_ai.page]try to start evenai";
static const char stop_message[] = "try to stop evenai, enable = %d";
static const char stop_short[] =
    "[even_ai.page]try to stop evenai, enable = %d";

void audio_even_ai_display_ctrl_4e1fd2(uint32_t action, const void *payload,
                                         uint32_t length) {
    if (audio_uart_device_role_get() != 1u)
        return;
    switch ((uint8_t)action) {
    case 0u: {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 0x67u,
                               start_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c000000u, start_short, start_short);
        uint32_t state = *(const uint32_t *)(audio_even_ai_service_state_2006ed10 + 4u);
        if (state)
            (void)audio_system_alert_command_45a8ee(7u, 0u, 0u, state);
        else
            audio_uart_master_display_start(7u, payload, (uint16_t)length, 0u);
        return;
    }
    case 1u:
        if (audio_log_wake_allowed() == 1u &&
            audio_quicklist_refresh_enabled_4434d0(7u) == 1u)
            audio_uart_master_display_refresh(7u, payload, (uint16_t)length, 0u);
        return;
    case 2u: {
        uint8_t enabled = audio_even_ai_service_state_2006ed10[0u];
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0x7au,
                               stop_message, enabled);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10400000u, stop_short,
                                        stop_short, enabled);
        if (enabled == 1u)
            audio_uart_master_display_stop(7u, payload, (uint16_t)length, 0u);
        return;
    }
    default:
        return;
    }
}
