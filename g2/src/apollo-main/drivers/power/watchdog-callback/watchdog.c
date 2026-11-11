#include "watchdog.h"
extern void stock_audio_submit(const audio_watchdog_message *);
extern uint32_t stock_audio_log_mask(void);
/* Stock 0x53C2A4 (aud codec audio-check timer callback) */
void audio_watchdog_tick(void *unused){
 (void)unused;audio_watchdog_message message={6,0,0};stock_audio_submit(&message);
}
/* audio_watchdog_emit_type0 (stock 0x53ca10, aud_send_message_type0) is an alias of
 * audio_app_stream_enable_53ca10 in audio/audio-app/audio_app_setup_children_20261016.c. */
