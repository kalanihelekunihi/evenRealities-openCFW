/* Native RTC request ABI: 0x50df0/0x50de0/0x51494 and backend wrappers.
 * Device errors are deliberately propagated only by the underlying requests. */
#include <string.h>
#include "native_clock_bootstrap.h"
#include "../registry/stock_registry.h"
extern generic_device_registry_device *r1_structured_rtc_device;
uint32_t r1_clock_rtc_write(uint32_t epoch,int32_t offset) {
    generic_device_registry_time_block request={0};
    request.epoch_seconds=epoch;
    request.utc_offset_minutes=(uint16_t)offset;
    return r1_stock_dispatch_14(r1_structured_rtc_device,0,(uintptr_t)&request,0);
}
uint32_t r1_clock_rtc_bind(r1_clock_tick_fn callback) {
    return r1_stock_dispatch_20(r1_structured_rtc_device,0,(uintptr_t)callback);
}
uint64_t r1_clock_backend_slot12(void) {
    generic_device_registry_time_block request={0};
    uint64_t result;
    (void)r1_stock_dispatch_10(r1_structured_rtc_device,0,(uintptr_t)&request,0);
    memcpy(&result,(const unsigned char *)&request+56,sizeof(result));
    return result;
}
int32_t r1_clock_backend_update(uint32_t epoch,int32_t offset,void *context) {
    (void)context;
    (void)r1_clock_rtc_write(epoch,offset);
    return 1;
}
uint32_t r1_clock_backend_bind_tick(uint32_t a,uint32_t b,uint32_t c,r1_clock_tick_fn callback) {
    (void)a;(void)b;(void)c;
    (void)r1_clock_rtc_bind(callback);
    return 1;
}
