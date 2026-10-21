/* Native conversate_action_app_resume 0x5b4d10..0x5b4db9. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_conversate_page_show_54f380(uint32_t);
extern void audio_conversate_page_hide_54f50e(uint32_t);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_app_resume";
static const char message[] = "conversate app resume";
static const char short_message[] = "[conversate]conversate app resume";
static const char null_message[] = "pData is NULL";
static const char null_short[] = "[conversate]pData is NULL";

uint32_t audio_conversate_action_5b4d10(void *context, const void *arg1, void *arg2) {
    (void)context;
    (void)arg2;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 182u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c000000u, short_message, short_message);
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 185u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    if (((const uint8_t *)arg1)[5] != 0u)
        audio_conversate_page_show_54f380(4u);
    else
        audio_conversate_page_hide_54f50e(4u);
    return 0u;
}
