/* Native snapshot/bind at 0x5a990/0x5a9b4. SRAM word views preserve aliases. */
#include "native_clock_bootstrap.h"
#include "native_battery_memory.h"
extern time_calendar_registration r1_time_registration;
_Static_assert(offsetof(time_calendar_registration,backend_registered)==12,"native snapshot flag");
_Static_assert(offsetof(time_calendar_registration,snapshot_backend)==16,"native snapshot pointer");
_Static_assert(offsetof(time_calendar_registration,context)==20,"native snapshot context");
uint32_t r1_clock_backend_snapshot(const r1_native_clock_ops **out,void **context)
{
    volatile uint8_t *record=(volatile uint8_t *)&r1_time_registration+12;
    uint32_t flag=record[0],snapshot=read32(record+4);
    if (((0u-flag)&snapshot)==0) return 0;
    if (out) write32((volatile uint8_t *)(uintptr_t)out,snapshot);
    if (context) write32((volatile uint8_t *)(uintptr_t)context,read32(record+8));
    return 1;
}
uint32_t r1_clock_backend_bind(const r1_native_clock_ops *ops,void *context)
{
    if (!ops || !read32((const volatile uint8_t *)(uintptr_t)ops+8)) return 0;
    volatile uint8_t *record=(volatile uint8_t *)&r1_time_registration+12;
    write32(record+4,(uint32_t)(uintptr_t)ops);
    write32(record+8,(uint32_t)(uintptr_t)context);
    record[0]=1;
    return 1;
}
