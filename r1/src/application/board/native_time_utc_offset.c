/* Native 8adb4: one signed halfword load from the RTC/calendar state. */
#include "time_calendar/time_calendar.h"
extern time_calendar_state r1_time_state;
_Static_assert(offsetof(time_calendar_state, utc_offset_minutes) == 8,
               "native signed UTC offset cell");
int32_t r1_time_utc_offset_get(void) {
    return ((const volatile time_calendar_state *)&r1_time_state)->utc_offset_minutes;
}
