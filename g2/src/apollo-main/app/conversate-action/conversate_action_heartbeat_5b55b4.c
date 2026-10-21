/* Native conversate_action_heartbeat 0x5b55b4..0x5b562f. */
#include <stdint.h>

extern uint32_t audio_conversate_ui_state_get_5b16d0(void);
extern const char *audio_conversate_ui_state_name_5b16dc(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_heartbeat";
static const char message[] =
    "recv heartbeat, conversate ui state is invalid: [%d:%s]";
static const char short_message[] =
    "[conversate]recv heartbeat, conversate ui state is invalid: [%d:%s]";

uint32_t audio_conversate_action_5b55b4(void *context, void *arg1, void *arg2) {
    (void)context;
    (void)arg1;
    (void)arg2;
    const uint8_t state = (uint8_t)audio_conversate_ui_state_get_5b16d0();
    if (state != 0u && state != 6u)
        return 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, path, function, 408u, message,
                           state, audio_conversate_ui_state_name_5b16dc(state));
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x08800000u, short_message, short_message,
                         state, audio_conversate_ui_state_name_5b16dc(state));
    return UINT32_MAX;
}
