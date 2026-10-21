/* Native timer stop wrappers 0x5b37c8..0x5b37d7 and 0x5b383c..0x5b384b. */
#include <stdint.h>

extern uint8_t audio_conversate_timer_mgr_ram_20073a3c[];
extern void audio_conversate_timer_stop_5b35d0(void *, const char *);

static const char loading_timeout[] = "Loading timeout";
static const char select_timeout[] = "Select timeout";

void audio_conversate_timer_1_stop_5b37c8(void) {
    audio_conversate_timer_stop_5b35d0(audio_conversate_timer_mgr_ram_20073a3c,
                                        loading_timeout);
}

void audio_conversate_timer_2_stop_5b383c(void) {
    audio_conversate_timer_stop_5b35d0(audio_conversate_timer_mgr_ram_20073a3c + 8u,
                                        select_timeout);
}
