#include <stdint.h>
#include "time_calendar/time_calendar.h"
#include "../runtime/integer_eabi.h"
extern time_calendar_state r1_time_state;
extern uint32_t r1_time_backend_timestamp(void);
struct __attribute__((packed,may_alias)) log_calendar_word { uint32_t value; };
struct __attribute__((packed,may_alias)) log_calendar_half { uint16_t value; };
static uint32_t word(const volatile void *p) {return ((const volatile struct log_calendar_word *)p)->value;}
static void put(volatile void *p,uint32_t v) {((volatile struct log_calendar_word *)p)->value=v;}
static uint16_t half(const volatile void *p) {return ((const volatile struct log_calendar_half *)p)->value;}
static void put_half(volatile void *p,uint16_t v) {((volatile struct log_calendar_half *)p)->value=v;}

uint32_t r1_log_local_datetime_fill(uint8_t *out)
{
    if (!out) return 0;
    volatile time_calendar_state *state=&r1_time_state;
    if (!state->registered) return 0;
    uint32_t epoch=r1_time_backend_timestamp();
    int32_t minutes=state->utc_offset_minutes;
    int32_t seconds_offset=minutes*60;
    int64_t local=(int64_t)epoch+seconds_offset;
    uint64_t remainder;
    (void)r1_runtime_sdivmod((uint64_t)local,86400u,&remainder);
    uint32_t day_start=(uint32_t)((uint64_t)local-remainder)-(uint32_t)seconds_offset;
    if (!state->cache_valid || state->cached_day_start!=day_start) {
        uint32_t adjusted_epoch=epoch+(uint32_t)seconds_offset;
        time_calendar_broken_down broken={0};
        const volatile uint8_t *filled=(const volatile uint8_t *)time_calendar_unix_to_broken_down(
            &adjusted_epoch,&broken);
        if (filled) {
            /* Native narrow loads and sequential stores preserve aliases. */
            put_half(&state->cached_year,(uint16_t)(half(filled+20)+1900u));
            state->cached_month=(uint8_t)(filled[16]+1u);
            state->cached_day=filled[12];
            state->cached_weekday=filled[24];
            state->cached_day_start=day_start;
            state->cache_valid=1;
        }
    }
    uint32_t seconds=(uint32_t)remainder;
    state->cached_hour=(uint8_t)(seconds/3600u);
    state->cached_minute=(uint8_t)((seconds%3600u)/60u);
    uint32_t second=seconds%60u;
    state->cached_second=(uint8_t)second;
    put(out,word(&state->cached_year));
    put(out+4,word(&state->cached_hour));
    return second;
}
