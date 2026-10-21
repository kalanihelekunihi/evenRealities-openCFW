/* Native default backend calendar ports 0x50d64 / 0x50d8a. */
#include "time_calendar/time_calendar.h"
extern time_calendar_state r1_time_state;
extern uint32_t r1_structured_log_timestamp_adapter(void);
extern uint32_t r1_clock_rtc_write(uint32_t,int32_t);
uint32_t r1_clock_backend_slot20(time_calendar_datetime *out) {
    if (!out) return 0;
    return time_calendar_utc_to_calendar((int32_t)r1_structured_log_timestamp_adapter(),0,out);
}
uint32_t r1_clock_backend_slot24(const time_calendar_datetime *in) {
    if (!in) return 0;
    uint32_t epoch=(uint32_t)time_calendar_to_utc(in,(int32_t)r1_time_state.utc_offset_minutes);
    (void)r1_clock_rtc_write(epoch,0);
    return 1;
}
