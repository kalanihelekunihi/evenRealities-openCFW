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
    /* Native publishes the captured epoch before sampling the live divider. */
    const volatile r1_rtc_counter_state *counter=&r1_rtc_counter;
    volatile rtc_device_time_block *snapshot=out;
    uint32_t epoch=counter->epoch;
    snapshot->epoch_seconds=epoch;
    uint32_t milliseconds=epoch*1000u+counter->divider;
    snapshot->millisecond_value=milliseconds;
    return 0;
}
/* Stock alarm configuration reads the caller name before the record name. */
static int rtc_name_compare(const char *const *name) {
    const char *device_name=*(const char *const volatile *)name;
    const char *record_name=((volatile r1_rtc_native_record *)&r1_rtc_record)->name;
    return strcmp(record_name,device_name);
}
uint32_t r1_native_rtc_calendar_write(const char *const *name,const void *calendar) {
    if (rtc_name_compare(name)) return 2;
    (void)r1_native_memory_move(&r1_rtc_record.calendar,calendar,44);
    return 0;
}
uint32_t r1_native_rtc_callback_bind(const char *const *name,uintptr_t argument,rtc_device_alarm_callback callback) {
    (void)argument;
    if (rtc_name_compare(name)) return 2;
    ((volatile r1_rtc_native_record *)&r1_rtc_record)->callback=callback;
    return 0;
}
