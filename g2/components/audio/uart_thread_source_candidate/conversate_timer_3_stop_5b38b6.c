/* Native auto-extend timer stop 0x5b38b6..0x5b38cb. */
#include <stdint.h>

extern uint8_t audio_conversate_timer_mgr_ram_20073a3c[];
extern void audio_conversate_timer_stop_5b35d0(void *, const char *);

static const char auto_extend[] = "Auto extend";

void audio_conversate_timer_3_stop_5b38b6(void) {
    *(uint32_t *)(void *)(audio_conversate_timer_mgr_ram_20073a3c + 0x18u) = 0u;
    audio_conversate_timer_stop_5b35d0(
        audio_conversate_timer_mgr_ram_20073a3c + 0x10u, auto_extend);
}
