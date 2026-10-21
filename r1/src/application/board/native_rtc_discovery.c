/* Native lazy cached lookup 0x50dc0; no refresh after a non-null result. */
#include "../registry/stock_registry.h"
extern generic_device_registry_device *r1_structured_rtc_device;
const char r1_rtc_lookup_name[] __attribute__((section(".r1.rtc.lookup.name")))="sys rtc";
generic_device_registry_device *r1_native_rtc_cached_device(void) {
    if (!r1_structured_rtc_device)
        r1_structured_rtc_device=r1_stock_registry_find(r1_rtc_lookup_name);
    return r1_structured_rtc_device;
}
