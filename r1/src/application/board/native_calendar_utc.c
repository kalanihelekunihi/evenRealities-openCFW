#include "time_calendar/time_calendar.h"
/* Native 0x8af40: forty-byte C scratch frame, epoch at +36, packed-copy
 * access widths/order and output aliases. Recorded Clang/GCC9 providers
 * retain native SP-48 with active R4 holding the output pointer. */
__attribute__((noinline)) uint32_t time_calendar_utc_to_calendar(
        int32_t epoch_seconds, int32_t utc_offset_minutes,
        time_calendar_datetime *out) {
    volatile struct {time_calendar_broken_down calendar;uint32_t epoch;} frame;
    _Static_assert(sizeof(frame)==40,"native UTC adapter scratch extent");
    volatile time_calendar_datetime *destination=out;
    if (out == 0) return 0;
    frame.epoch = (uint32_t)epoch_seconds + (uint32_t)utc_offset_minutes * 60u;
    const time_calendar_broken_down *filled = time_calendar_unix_to_broken_down(
        (const uint32_t *)(uintptr_t)&frame.epoch,
        (time_calendar_broken_down *)(uintptr_t)&frame.calendar);
    if (filled == 0) return 0;
    const volatile uint8_t *bytes = (const volatile uint8_t *)filled;
    uint16_t year = *(const volatile uint16_t *)(const volatile void *)(bytes + 20);
    destination->year = (uint16_t)(year + 1900u);
    destination->month = (uint8_t)(bytes[16] + 1u);
    destination->day = bytes[12];
    destination->hour = bytes[8];
    destination->minute = bytes[4];
    destination->second = bytes[0];
    destination->weekday = bytes[24];
    return 1;
}
