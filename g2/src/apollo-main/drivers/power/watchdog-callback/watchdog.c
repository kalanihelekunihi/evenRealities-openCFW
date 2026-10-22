#include "watchdog.h"
extern void stock_audio_submit(const audio_watchdog_message *);
extern uint32_t stock_audio_log_mask(void);
/* Stock 0x53C2A4 (aud codec audio-check timer callback) */
void audio_watchdog_tick(void *unused){
 (void)unused;audio_watchdog_message message={6,0,0};stock_audio_submit(&message);
}
void audio_watchdog_emit_type0(uint32_t value){
 audio_watchdog_message message={0,1,(uint8_t)value};stock_audio_submit(&message);
}
