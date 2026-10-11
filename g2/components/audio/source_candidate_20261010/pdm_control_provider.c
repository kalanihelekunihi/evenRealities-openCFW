#include "../watchdog_callback_offline/watchdog.h"

extern void stock_audio_submit(const audio_watchdog_message *);

/* Apollo MAIN 0x53ca32: publish type-1, mode-1, low-byte control value. */
void audio_pdm_control(uint32_t value) {
    audio_watchdog_message message = {1u, 1u, (uint8_t)value};
    stock_audio_submit(&message);
}
