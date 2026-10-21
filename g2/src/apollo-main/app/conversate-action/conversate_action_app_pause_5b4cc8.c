/* Native conversate_action_app_pause 0x5b4cc8..0x5b4d0f. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_app_pause";
static const char message[] = "conversate app pause";
static const char short_message[] = "[conversate]conversate app pause";

uint32_t audio_conversate_action_5b4cc8(void *context, void *arg1, void *arg2) {
    (void)context;
    (void)arg1;
    (void)arg2;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 176u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c000000u, short_message, short_message);
    return 0u;
}
