/* Native sys-rtc device ABI. Owner-authorized reconstruction, not vendor source.
 * The native loop tail exits after record zero; no full-table normalization. */
#include <string.h>
#include "native_rtc_device.h"
extern void *r1_native_memory_move(void *,const void *,size_t);
r1_rtc_counter_state r1_rtc_counter __attribute__((section(".r1.rtc.counter"),aligned(4)));
const char r1_rtc_device_name[] __attribute__((section(".r1.rtc.name")))="sys rtc";
r1_rtc_native_record r1_rtc_record __attribute__((section(".r1.rtc.record"),aligned(4)))={
    .name=r1_rtc_device_name,.rtc={.registers=0x40024000,.irq=36,.instance_id=0,.channels=4}
};
_Static_assert(sizeof(r1_rtc_counter_state)==8,"native counter prefix");
_Static_assert(sizeof(r1_rtc_native_record)==88,"native single record");
_Static_assert(offsetof(r1_rtc_native_record,rtc)==52 && offsetof(r1_rtc_native_record,callback)==60 && offsetof(r1_rtc_native_record,registry)==64,"native record fields");
uint32_t r1_native_rtc_snapshot(uintptr_t device,uintptr_t argument,rtc_device_time_block *out,uintptr_t unused) {
    (void)device;(void)argument;(void)unused;
    if (!out) return 4;
    out->epoch_seconds=r1_rtc_counter.epoch;
    out->millisecond_value=(uint32_t)(r1_rtc_counter.epoch*1000u+r1_rtc_counter.divider);
    return 0;
}
uint32_t r1_native_rtc_calendar_write(const char *const *name,const void *calendar) {
    if (strcmp(r1_rtc_record.name,*name)) return 2;
    (void)r1_native_memory_move(&r1_rtc_record.calendar,calendar,44);
    return 0;
}
uint32_t r1_native_rtc_callback_bind(const char *const *name,uintptr_t argument,rtc_device_alarm_callback callback) {
    (void)argument;
    if (strcmp(r1_rtc_record.name,*name)) return 2;
    r1_rtc_record.callback=callback;
    return 0;
}
