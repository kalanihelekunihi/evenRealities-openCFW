/* Native RTC lifecycle and unsigned four-year breakdown contracts. */
#include <string.h>
#include "native_rtc_device.h"
#include "native_rtc_driver.h"
static uint32_t r1_rtc_tm[8] __attribute__((section(".r1.rtc.tm"),aligned(4)));
static const uint8_t r1_rtc_months[12] __attribute__((section(".r1.rtc.months")))={31,29,31,30,31,30,31,31,30,31,30,31};
uint32_t *r1_native_rtc_gmtime(const uint32_t *epoch) {
    uint32_t value=*epoch;
    r1_rtc_tm[0]=value%60;value/=60;
    r1_rtc_tm[1]=value%60;value/=60;
    r1_rtc_tm[2]=value%24;value/=24;
    r1_rtc_tm[6]=(value+4)%7;
    uint32_t cycle=value*4+2924;
    r1_rtc_tm[5]=cycle/1461+68;
    uint32_t days=(cycle%1461)/4;
    r1_rtc_tm[7]=days;
    if (days>=59 && (r1_rtc_tm[5]&3)) ++days;
    uint32_t month=0;
    while (r1_rtc_months[month]<=days) days-=r1_rtc_months[month++];
    r1_rtc_tm[4]=month;r1_rtc_tm[3]=days+1;
    return r1_rtc_tm;
}
__attribute__((noinline)) uint32_t r1_native_rtc_epoch_to_calendar(uint32_t epoch,rtc_device_calendar *out) {
    const uint32_t *tm=r1_native_rtc_gmtime(&epoch);
    out->year=tm[5]+1900;out->month=tm[4]+1;out->day=tm[3];
    out->hour=tm[2];out->minute=tm[1];out->second=tm[0];
    out->weekday=tm[6];out->year_day=tm[7]+1;
    return out->year_day;
}
/* Native 0x56274 exposes 48 calendar scratch bytes at caller SP minus 64.
 * Keep conversion out of line: inlining collapses the scratch into only the
 * fields used by the alarm checks. The recorded Clang profile owns an
 * eight-byte save area plus 56 local bytes, placing the first 48 at the
 * native address. The final eight local bytes are private compiler padding.
 */
__attribute__((used,noinline)) static uint32_t rtc_tick_body(void) {
    struct r1_tick_frame {
        rtc_device_calendar calendar;
        uint32_t scratch_tail;
        uint32_t frame_padding[2];
    } scratch;
    _Static_assert(sizeof(scratch)==56 &&
            offsetof(struct r1_tick_frame,frame_padding)==48,"C tick frame extent");
    volatile rtc_device_calendar *calendar=&scratch.calendar;
    volatile r1_rtc_counter_state *counter=&r1_rtc_counter;
    volatile r1_rtc_native_record *record=&r1_rtc_record;
    uint32_t divider=counter->divider;
    if (divider<7) {counter->divider=(uint16_t)(divider+1u);return divider+1u;}
    uint32_t epoch=counter->epoch+1u;
    counter->epoch=epoch;
    int32_t offset=counter->offset;
    uint32_t local=epoch+(uint32_t)(offset*60);
    (void)r1_native_rtc_epoch_to_calendar(local,
            (rtc_device_calendar *)(uintptr_t)calendar);
    uint32_t minute=calendar->minute;
    if (minute==record->calendar.minute) {
        uint32_t second=calendar->second;
        if (second==record->calendar.second) {
            rtc_device_alarm_callback callback=record->callback;
            if (callback)callback((uint8_t)calendar->hour);
        }
    }
    counter->divider=0;
    return 0;
}
__attribute__((noinline)) void r1_native_rtc_tick(nrfx_rtc_int_type_t ignored_event) {
    (void)ignored_event;
    (void)rtc_tick_body();
}
/* Native 0x5649c supplies 48 calendar scratch bytes at caller SP minus 72.
 * Clang owns 56 local bytes plus 16 saved bytes. GCC9 uses 48 local bytes,
 * four alignment bytes and 20 saved bytes. Private/save layouts differ.
 */
__attribute__((noinline)) uint32_t r1_native_rtc_epoch_initialize(
        const char *const *name,uintptr_t argument,const rtc_device_time_block *block) {
    struct r1_epoch_frame {
        rtc_device_calendar calendar;
        uint32_t scratch_tail;
#if defined(__clang__)
        uint32_t frame_padding[2];
#endif
    } scratch;
    _Static_assert(offsetof(struct r1_epoch_frame,scratch_tail)==44,
            "native epoch calendar prefix");
#if defined(__clang__)
    _Static_assert(sizeof(scratch)==56,"Clang epoch local extent");
#else
    _Static_assert(sizeof(scratch)==48,"GCC epoch local extent");
#endif
    rtc_device_calendar *calendar=&scratch.calendar;
    (void)argument;
    if (!block) return 4;
    const volatile rtc_device_time_block *live=block;
    volatile r1_rtc_counter_state *counter=&r1_rtc_counter;
    volatile r1_rtc_native_record *record=&r1_rtc_record;
    counter->offset=live->utc_offset_minutes;
    const char *device_name=*(const char *const volatile *)name;
    const char *record_name=record->name;
    if (strcmp(record_name,device_name) || !record->opened) return 17;
    uint32_t epoch=live->epoch_seconds;
    counter->epoch=epoch;
    (void)r1_native_rtc_epoch_to_calendar(epoch,calendar);
    return 0;
}
/* These fixed-width bridge ABIs keep the native instance/configuration explicit;
 * SDK implementations and the error path remain providers until admitted. */
typedef struct {uint16_t prescaler;uint8_t priority,tick_latency,reliable,padding[3];} r1_rtc_boot_config;
const r1_rtc_boot_config r1_rtc_boot_defaults __attribute__((section(".r1.rtc.defaults")))={0,6,65,0,{0,0,0}};
/* Device open has one C status return. R2/R3 are caller-clobbered scratch;
 * the typed registry dispatcher consumes only R0. Keep the configuration
 * buffer live for provider writes, without compiler register bindings. */
__attribute__((noinline)) uint32_t r1_native_rtc_open(const char *const *name) {
    volatile union {
        r1_rtc_boot_config config;
        uint32_t words[2];
#if !defined(__clang__)
        uint32_t compiler_extent[4];
#endif
    } frame;
    _Static_assert(sizeof(frame.config)==8,"native RTC configuration");
#if defined(__clang__)
    _Static_assert(sizeof(frame)==8,"Clang RTC open local extent");
#else
    _Static_assert(sizeof(frame)==16,"GCC RTC open local extent");
#endif
    const char *device_name=*(const char *const volatile *)name;
    volatile r1_rtc_native_record *record=&r1_rtc_record;
    const char *record_name=record->name;
    uint32_t result=17;
    if (!strcmp(record_name,device_name)) {
        result=0;
        if (!record->opened) {
            frame.config=r1_rtc_boot_defaults;frame.config.prescaler=4095;
            uint32_t status=r1_rtc_driver_initialize(&r1_rtc_record.rtc,
                    (const void *)(uintptr_t)&frame.config,r1_native_rtc_tick);
            if (status) r1_adc_error(status);
            r1_rtc_driver_tick_enable(&r1_rtc_record.rtc,1);
            r1_rtc_driver_enable(&r1_rtc_record.rtc);
            record->opened=1;
        }
    }
    return result;
}


extern uint32_t r1_native_rtc_snapshot(uintptr_t,uintptr_t,rtc_device_time_block *,uintptr_t);
extern uint32_t r1_native_rtc_calendar_write(const char *const *,const void *);
extern uint32_t r1_native_rtc_callback_bind(const char *const *,uintptr_t,rtc_device_alarm_callback);
const uintptr_t r1_rtc_device_ops[9] __attribute__((section(".r1.rtc.ops")))={
    0,0,(uintptr_t)r1_native_rtc_open,0,(uintptr_t)r1_native_rtc_snapshot,
    (uintptr_t)r1_native_rtc_epoch_initialize,0,(uintptr_t)r1_native_rtc_calendar_write,(uintptr_t)r1_native_rtc_callback_bind
};
uint32_t r1_native_rtc_register(void) {
    r1_rtc_record.registry.name=r1_rtc_record.name;
    r1_rtc_record.registry.ops=(const void *)r1_rtc_device_ops;
    return r1_stock_registry_register(&r1_rtc_record.registry);
}
