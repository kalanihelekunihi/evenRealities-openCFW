#include "watchdog.h"
extern void stock_audio_submit(const audio_watchdog_message *);
extern uint32_t stock_audio_log_mask(void);
void audio_watchdog_tick(void *unused){
 (void)unused;audio_watchdog_message message={6,0,0};stock_audio_submit(&message);
}
void audio_watchdog_emit_type0(uint32_t value){
 audio_watchdog_message message={0,1,(uint8_t)value};stock_audio_submit(&message);
}
void audio_watchdog_type6_log_disabled(const audio_watchdog_message *unused){
 (void)unused;
 if(!*(volatile uint8_t *)0x2007502eu)return;
 uint32_t prior=*(volatile uint32_t *)0x20074a9cu;
 *(volatile uint32_t *)0x20074a9cu=0;
 /* These three reads execute the real getter, rather than assuming its result.
  * All must be0 under this explicitly selected no-logging contract. */
 (void)stock_audio_log_mask();(void)stock_audio_log_mask();(void)stock_audio_log_mask();
 if(prior<20)audio_watchdog_emit_type0(2);
}
