/* Native RTC lifecycle and unsigned four-year breakdown contracts. */
#include <string.h>
#include "native_rtc_device.h"
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
uint32_t r1_native_rtc_epoch_to_calendar(uint32_t epoch,rtc_device_calendar *out) {
    const uint32_t *tm=r1_native_rtc_gmtime(&epoch);
    out->year=tm[5]+1900;out->month=tm[4]+1;out->day=tm[3];
    out->hour=tm[2];out->minute=tm[1];out->second=tm[0];
    out->weekday=tm[6];out->year_day=tm[7]+1;
    return out->year_day;
}
void r1_native_rtc_tick(uint32_t ignored_event) {
    (void)ignored_event;
    if (r1_rtc_counter.divider<7) {++r1_rtc_counter.divider;return;}
    ++r1_rtc_counter.epoch;
    uint32_t local=r1_rtc_counter.epoch+(uint32_t)((int32_t)r1_rtc_counter.offset*60);
    rtc_device_calendar calendar;
    (void)r1_native_rtc_epoch_to_calendar(local,&calendar);
    if (calendar.minute==r1_rtc_record.calendar.minute && calendar.second==r1_rtc_record.calendar.second && r1_rtc_record.callback)
        r1_rtc_record.callback((uint8_t)calendar.hour);
    r1_rtc_counter.divider=0;
}
uint32_t r1_native_rtc_epoch_initialize(const char *const *name,uintptr_t argument,const rtc_device_time_block *block) {
    (void)argument;
    if (!block) return 4;
    r1_rtc_counter.offset=block->utc_offset_minutes;
    if (strcmp(r1_rtc_record.name,*name) || !r1_rtc_record.opened) return 17;
    r1_rtc_counter.epoch=block->epoch_seconds;
    rtc_device_calendar discarded;
    (void)r1_native_rtc_epoch_to_calendar(block->epoch_seconds,&discarded);
    return 0;
}
/* These fixed-width bridge ABIs keep the native instance/configuration explicit;
 * SDK implementations and the error path remain providers until admitted. */
typedef struct {uint16_t prescaler;uint8_t priority,tick_latency,reliable,padding[3];} r1_rtc_boot_config;
const r1_rtc_boot_config r1_rtc_boot_defaults __attribute__((section(".r1.rtc.defaults")))={0,6,65,0,{0,0,0}};
#include "native_rtc_driver.h"
uint32_t r1_native_rtc_open(const char *const *name) {
    if (strcmp(r1_rtc_record.name,*name)) return 17;
    if (r1_rtc_record.opened) return 0;
    r1_rtc_boot_config config=r1_rtc_boot_defaults;config.prescaler=4095;
    uint32_t status=r1_rtc_driver_initialize(&r1_rtc_record.rtc,&config,r1_native_rtc_tick);
    if (status) r1_rtc_driver_error(status);
    r1_rtc_driver_tick_enable(&r1_rtc_record.rtc,1);
    r1_rtc_driver_enable(&r1_rtc_record.rtc);
    r1_rtc_record.opened=1;
    return 0;
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
