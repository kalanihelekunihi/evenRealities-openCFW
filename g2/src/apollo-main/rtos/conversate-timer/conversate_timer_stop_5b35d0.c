/* Native conversate_deadline_timer_stop 0x5b35d0..0x5b3627. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_deadline_timer_stop";
static const char message[] = "%s timer stop";
static const char short_message[] = "[conversate.timer]%s timer stop";

void audio_conversate_timer_stop_5b35d0(void *timer, const char *name) {
    if (timer == 0)
        return;
    uint8_t *const bytes = timer;
    bytes[0] = 0u;
    *(uint32_t *)(void *)(bytes + 4u) = 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 112u, message, name);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10400000u, short_message, short_message, name);
}
