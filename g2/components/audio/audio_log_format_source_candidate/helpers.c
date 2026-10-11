/* Exact selected lower aliases for stock 0x43d0da, 0x4490cc and 0x44a43c. */
#include <stdint.h>
extern volatile uint8_t audio_log_policy_byte; /* literal 0x43d140 */
extern uint32_t g2_flashdb_candidate_tick(void); /* stock 0x4490cc */
extern uint32_t g2_log_module_length(const char *); /* stock 0x44a43c */
uint32_t audio_log_level(void) { return audio_log_policy_byte; }
uint32_t audio_log_tick(void) { return g2_flashdb_candidate_tick(); }
uint32_t audio_string_length(const char *p) { return g2_log_module_length(p); }
/* RTC latch calls the same native delay body 0x4807a0 already selected. */
extern void audio_delay_us(uint32_t);
void audio_rtc_delay(uint32_t microseconds) { audio_delay_us(microseconds); }
