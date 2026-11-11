/* Native RTC request ABI: 0x50df0/0x50de0/0x51494 and backend wrappers.
 * Device errors are deliberately propagated only by the underlying requests. */
#include <string.h>
#include "native_clock_bootstrap.h"
#include "../registry/stock_registry.h"
extern generic_device_registry_device *r1_structured_rtc_device;
__attribute__((noinline)) uint32_t r1_clock_rtc_write(uint32_t epoch,int32_t offset) {
    generic_device_registry_time_block request;
    /* The returned pointer avoids carrying the request in R6 across clear
     * and dispatch. Recorded Clang then retains native active R4/R5 inputs
     * and incoming R6-R11 at the 80-byte provider boundary. */
    generic_device_registry_time_block *zeroed=memset(&request,0,sizeof(request));
    zeroed->epoch_seconds=epoch;
    zeroed->utc_offset_minutes=(uint16_t)offset;
    return r1_stock_dispatch_14(r1_structured_rtc_device,0,(uintptr_t)zeroed,0);
}
__attribute__((noinline)) uint32_t r1_clock_rtc_bind(r1_clock_tick_fn callback) {
    return r1_stock_dispatch_20(r1_structured_rtc_device,0,(uintptr_t)callback);
}
uint64_t r1_clock_backend_slot12(void) {
    /* The union permits a direct 64-bit result load without a copy temporary.
     * The memset result avoids retaining a request pointer in R4. Recorded
     * Clang then preserves incoming R4-R11 at native provider SP minus 72. */
    union {generic_device_registry_time_block request;uint64_t words[8];} frame;
    _Static_assert(sizeof(frame)==64,"native RTC read request extent");
    void *zeroed=memset(&frame,0,sizeof(frame));
    (void)r1_stock_dispatch_10(r1_structured_rtc_device,0,(uintptr_t)zeroed,0);
    return frame.words[7];
}
/* Backends use the ordinary C ABI and return success after dispatch.
 * Request calls remain out of line; private provider frames are compiler-owned. */
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
