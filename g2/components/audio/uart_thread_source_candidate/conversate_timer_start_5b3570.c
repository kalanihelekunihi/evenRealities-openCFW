/* Native conversate_deadline_timer_start 0x5b3570..0x5b35cf. */
#include <stdint.h>

extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.timer";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c";
static const char function[] = "conversate_deadline_timer_start";
static const char message[] = "%s timer start";
static const char short_message[] = "[conversate.timer]%s timer start";

void audio_conversate_timer_start_5b3570(void *timer, uint32_t duration,
                                          const char *name) {
    if (timer == 0)
        return;
    uint8_t *const bytes = timer;
    bytes[0] = 1u;
    *(uint32_t *)(void *)(bytes + 4u) = duration + g2_flashdb_candidate_tick();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 102u, message, name);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10400000u, short_message, short_message, name);
}
