#include "stock_registry.h"
#include "native_watchdog.h"
generic_device_registry_device *volatile r1_native_watchdog_device
 __attribute__((section(".r1.watchdog.device"),aligned(4)));
uint32_t r1_native_watchdog_hw_open_feed(void)
{
    r1_stock_dispatch_00(r1_native_watchdog_device);
    return r1_stock_dispatch_18(r1_native_watchdog_device,0,0);
}
uint32_t r1_native_watchdog_hw_handle_init(void)
{
    if (!r1_native_watchdog_device)
        r1_native_watchdog_device=r1_stock_registry_find("watchdog");
    return r1_native_watchdog_hw_open_feed();
}
uint32_t r1_native_watchdog_hw_close(void)
{ return r1_stock_dispatch_0c(r1_native_watchdog_device); }
uint32_t r1_native_watchdog_hw_feed(void)
{ return r1_stock_dispatch_18(r1_native_watchdog_device,0,0); }

uint32_t r1_native_watchdog_hw_feed_thunk(void)
{ return r1_native_watchdog_hw_feed(); }
