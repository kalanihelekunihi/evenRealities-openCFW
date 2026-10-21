/* Apollo Main stock 0x449fda: UTC seconds -> 40-byte calendar record.
 * Native uses 2000-01-01 as its lower clamp and a 1461-day cycle. It
 * writes weekday and year/month/day/hour/minute/second fields. Three
 * other record words were not initialized in the native stack frame;
 * final equivalence for those bytes remains an explicit gate. */
#include <stdint.h>

extern uint8_t audio_uart_hand_record[0x30u]; /* native 0x200736d4 */

static const uint16_t leap_days[13] =
    {0u,31u,60u,91u,121u,152u,182u,213u,244u,274u,305u,335u,366u};
static const uint16_t normal_days[13] =
    {0u,31u,59u,90u,120u,151u,181u,212u,243u,273u,304u,334u,365u};

static void put32(uint8_t *out, uint32_t offset, uint32_t value)
{
    for (uint32_t i=0u; i<4u; ++i)
        out[offset+i] = (uint8_t)(value >> (8u*i));
}

void audio_time_epoch_to_calendar_449fda(uint32_t seconds, void *record)
{
    uint32_t days, subday;
    if (seconds >= 946684800u) {
        days = seconds / 86400u - 10957u;
        subday = seconds % 86400u;
    } else {
        days = 0u;
        subday = 0u;
    }
    uint32_t second = subday % 60u;
    uint32_t minute = (subday / 60u) % 60u;
    uint32_t hour = subday / 3600u;
    const volatile uint32_t *clock_mode =
        (const volatile uint32_t *)(const void *)(audio_uart_hand_record + 24u);
    if (*clock_mode == 1u) {
        hour %= 12u;
        if (hour == 0u) hour = 12u;
    }
    uint32_t weekday = (days + 6u) % 7u;
    uint32_t year = 2000u + 4u*(days / 1461u);
    uint32_t day_in_cycle = days % 1461u;
    const uint16_t *cumulative = day_in_cycle >= 366u ? normal_days : leap_days;
    if (day_in_cycle >= 366u) {
        year += (day_in_cycle-1u) / 365u;
        day_in_cycle = (day_in_cycle-1u) % 365u;
    }
    uint32_t month = day_in_cycle / 31u + 1u;
    if (day_in_cycle >= cumulative[month]) ++month;
    uint32_t day = day_in_cycle - cumulative[month-1u] + 1u;
    uint8_t *out = (uint8_t *)record;
    put32(out, 4u, weekday);
    put32(out, 12u, (uint32_t)(uint16_t)year - 2000u);
    put32(out, 16u, month);
    put32(out, 20u, day);
    put32(out, 24u, hour);
    put32(out, 28u, minute);
    put32(out, 32u, second);
}
