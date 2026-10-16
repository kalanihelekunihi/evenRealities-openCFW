/* Terminal FSM query-notification show action, stock 0x5e6548..0x5e65f7. */
#include <stdint.h>
extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern void audio_uart_page_43ded4(void *, uint32_t);
extern void audio_terminal_query_visibility_5ec82a(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_action_query_notification_show";
static const char message[] = "query notification shown: session=%lu return_state=%d";
static const char short_message[] =
    "[terminal.ui]query notification shown: session=%lu return_state=%d";
uint32_t audio_terminal_ui_action_5e6548(uint32_t state, uint32_t session,
                                           uint32_t unused, uint32_t unused4) {
    (void)unused;
    (void)unused4;
    uint8_t *s = audio_terminal_ui_state_base;
    if (session == 0u)
        session = *(uint32_t *)(void *)(s + 0x288u);
    if (session == 0u)
        session = audio_terminal_counter_b_get_5973dc();
    *(uint32_t *)(void *)(s + 0x288u) = session;
    if ((uint8_t)state == 1u)
        state = 0u;
    s[0x277u] = (uint8_t)state;
    s[0x27fu] = 0u;
    uint32_t object = *(uint32_t *)(void *)s;
    if (s[0x277u] == 0u && object != 0u)
        audio_uart_page_43ded4((void *)(uintptr_t)object, 1u);
    audio_terminal_query_visibility_5ec82a();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x5d9u,
                           message, session, s[0x277u]);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, short_message,
                                    short_message, session, s[0x277u]);
    return 0u;
}
