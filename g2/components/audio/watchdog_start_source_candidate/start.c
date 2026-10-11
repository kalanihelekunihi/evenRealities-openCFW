#include <stdint.h>

/* Stock Main 0x0053c2be..0x0053c31a. The timer pointer cell is at
 * 0x20074a98 in the official image; its declaration and placement are
 * product data contracts, not reconstructed from the literal address. */
extern void *g2_audio_codec_check_timer;
extern int32_t osTimerStart(void *timer, uint32_t ticks);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "thread.audio";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_audio.c";
static const char function[] = "AUD_CodecAudioCheckTimerStart";
static const char failure[] = "codec audio check timer start failed";
static const char simple_failure[] =
    "[thread.audio]codec audio check timer start failed";

void audio_watchdog_start(void) {
    void *timer = g2_audio_codec_check_timer;
    if (timer == 0 || osTimerStart(timer, 2000u) == 0)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, file, function, 146u, failure);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x04000000u, simple_failure, simple_failure);
}
