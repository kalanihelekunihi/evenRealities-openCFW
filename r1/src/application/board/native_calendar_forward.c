/* Native 5a7bc, including the pointer ABI and late epoch reread. */
#include "time_calendar/time_calendar.h"
const uint8_t month_days_forward[24]
    __attribute__((section(".r1.calendar.month.forward"))) = {
    31,28,31,30,31,30,31,31,30,31,30,31,
    31,29,31,30,31,30,31,31,30,31,30,31
};
time_calendar_broken_down unix_to_broken_down_fallback
    __attribute__((section(".r1.calendar.forward.fallback"), aligned(4)));
static bool leap(uint32_t year) {
    return ((year & 3u) == 0 && year % 100u != 0) || year % 400u == 0;
}
__attribute__((noinline)) time_calendar_broken_down *time_calendar_unix_to_broken_down(
        const uint32_t *epoch_seconds, time_calendar_broken_down *out) {
    if (out == 0) out = &unix_to_broken_down_fallback;
    volatile time_calendar_broken_down *result = out;
    const volatile uint32_t *epoch = epoch_seconds;
    uint32_t initial = *epoch;
    uint32_t days = initial / 86400u, seconds = initial % 86400u;
    result->hour = seconds / 3600u;
    result->minute = (seconds % 3600u) / 60u;
    result->second = seconds % 60u;
    uint32_t year = 1970;
    while (days > 364u) {
        if (leap(year)) {
            if (days < 366u) break;
            days -= 366u;
        } else {
            days -= 365u;
        }
        ++year;
    }
    result->year = year - 1900u;
    const volatile uint8_t *table = month_days_forward + (leap(year) ? 12 : 0);
    uint32_t remainder = days;
    uint8_t month = 0;
    for (;;) {
        uint32_t length = table[month];
        if (length > remainder) break;
        remainder -= length;
        month = (uint8_t)(month + 1u);
    }
    result->year_day = days;
    result->day = remainder + 1u;
    result->month = month;
    /* Input may alias a word just stored above. Stock reads it again here. */
    result->weekday = (*epoch / 86400u + 4u) % 7u;
    result->zero_tail = 0;
    return out;
}

