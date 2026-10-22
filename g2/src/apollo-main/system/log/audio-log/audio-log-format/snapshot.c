/* Stock 0x47ef10..0x47ef17: RTC calendar snapshot forwarding wrapper. */
#include <stdint.h>
extern uint32_t audio_rtc_read_calendar(uint8_t out[40]); /* stock 0x4d3c0a */
/* Stock 0x47EF10 (RTC calendar snapshot wrapper) */
void audio_time_snapshot(uint8_t out[40]) { (void)audio_rtc_read_calendar(out); }
