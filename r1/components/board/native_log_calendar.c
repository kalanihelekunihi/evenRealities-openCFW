/* Native0x8ac28 ABI/cache semantics; Gregorian converter is recovered C. */
#include <stdint.h>
#include <string.h>
#include "time_calendar/time_calendar.h"
extern time_calendar_state r1_time_state;
extern uint32_t r1_time_backend_timestamp(void);
void r1_log_local_datetime_fill(uint8_t out[8])
{
    time_calendar_state *state=&r1_time_state;
    if (!out || !state->registered) return;
    uint32_t epoch=r1_time_backend_timestamp();
    int32_t offset=(int32_t)state->utc_offset_minutes*60;
    int64_t local=(int64_t)epoch+offset;
    int64_t quotient=local/86400;
    uint32_t day_start=(uint32_t)(quotient*86400)-(uint32_t)offset;
    if (!state->cache_valid || state->cached_day_start!=day_start) {
        time_calendar_broken_down broken;
        time_calendar_broken_down *filled=time_calendar_unix_to_broken_down(epoch+(uint32_t)offset,&broken);
        if (filled) {
            state->cached_year=(uint16_t)(filled->year+1900);
            state->cached_month=(uint8_t)(filled->month+1);
            state->cached_day=(uint8_t)filled->day;
            state->cached_weekday=(uint8_t)filled->weekday;
            state->cached_day_start=day_start;
            state->cache_valid=1;
        }
    }
    uint32_t seconds=(uint32_t)(local%86400);
    state->cached_hour=(uint8_t)(seconds/3600);
    state->cached_minute=(uint8_t)((seconds%3600)/60);
    state->cached_second=(uint8_t)(seconds-(seconds/60)*60);
    memcpy(out,&state->cached_year,8);
}
