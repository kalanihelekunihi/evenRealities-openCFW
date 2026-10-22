/* Native service_time_rtc_refresh at 0x44a1ea: calendar snapshot
 * (0x47ef10 -> selected 0x4d3c0a) followed by epoch conversion (0x44a108).
 * The calendar buffer has the native 40-byte stack extent. */
#include <stdint.h>
extern uint32_t audio_rtc_read_calendar(uint8_t out[40]);
extern uint32_t audio_time_epoch_seconds(const uint8_t in[40]);
/* Stock 0x0044A1EA (service_time_rtc_refresh) */
uint32_t audio_uart_ring_rtc_refresh(void) {
    uint8_t calendar[40];
    (void)audio_rtc_read_calendar(calendar);
    return audio_time_epoch_seconds(calendar);
}
