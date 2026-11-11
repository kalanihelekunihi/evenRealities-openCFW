#include <stdint.h>

extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
#include "../../vendor/time_calendar/time_calendar.h"
extern int32_t r1_time_utc_offset_get(void);
#include "native_hourly_state.h"
struct __attribute__((packed,may_alias)) average_word { uint32_t value; };
struct __attribute__((packed,may_alias)) average_half { uint16_t value; };
static uint32_t word(const volatile void *p) {return ((const volatile struct average_word *)p)->value;}
static void put_word(volatile void *p,uint32_t v) {((volatile struct average_word *)p)->value=v;}
static uint32_t half(const volatile void *p) {return ((const volatile struct average_half *)p)->value;}
static void put_half(volatile void *p,uint32_t v) {((volatile struct average_half *)p)->value=(uint16_t)v;}

/* Stock 0x5aca6: only the returned hour is public. The seven direct
 * callers consume R0 and do not depend on restored caller-scratch R2/R3. */
__attribute__((noinline,section(".text.r1_health_storage_hour_index"))) uint32_t
r1_health_storage_hour_index(uint32_t timestamp)
{
    volatile time_calendar_datetime calendar={0};
    _Static_assert(sizeof(calendar)==8 && offsetof(time_calendar_datetime,hour)==4,"native calendar layout");
    int32_t offset=r1_time_utc_offset_get();
    (void)time_calendar_utc_to_calendar((int32_t)timestamp,offset,(time_calendar_datetime *)(uintptr_t)&calendar);
    return calendar.hour;
}

__attribute__((section(".text.r1_health_storage_average"))) uint32_t
r1_health_storage_average(uint32_t type,uint32_t sample,uint32_t timestamp)
{
    if (type>5) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x04400000,"[RING]not support type:%d","[RING]not support type:%d",type);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,"not support type:%d",type);
        return 0;
    }
    uint32_t hour=r1_health_storage_hour_index(timestamp);
    volatile uint8_t *row=(volatile uint8_t *)(uintptr_t)
        ((uint32_t)(uintptr_t)&r1_health_hourly_stress_storage+(type<<3));
    if (!half(row+2) || row[0]!=hour) {
        put_word(row,0);put_word(row+4,0);row[0]=(uint8_t)hour;
    }
    put_half(row+2,half(row+2)+1u);
    uint32_t sum=word(row+4)+sample;
    put_word(row+4,sum);
    uint32_t count=half(row+2);
    float numerator=(float)sum;
    float denominator=(float)count;
    float result=numerator/denominator;
    /* This target profile emits the native VCVT.U32.F32 for the cast;
     * verify the emitted instruction when changing compiler or flags. */
    return (uint16_t)(uint32_t)result;
}
