/* Stock touch registry adapters 46f54..46fd0. Cached handle ownership stays
 * in native_peripheral_bindings.c: bus 200067fc, output 20006800, input 20006804. */
#include <stdint.h>
#include "../registry/stock_registry.h"
#include "native_touch_ready_state.h"
extern generic_device_registry_device *volatile r1_touch_bus_device;
extern generic_device_registry_device *volatile r1_touch_output_device;
extern void r1_shared_power_client_release(uint32_t);
uint32_t r1_touch_record_op_0c_b(void)
{
    return r1_stock_dispatch_0c(r1_touch_bus_device);
}
uint32_t r1_touch_record_op_08(void)
{
    return r1_stock_dispatch_08(r1_touch_bus_device);
}
uint32_t r1_touch_device_op_stop(void)
{
    (void)r1_stock_dispatch_0c(r1_touch_input_device);
    return r1_stock_dispatch_20(r1_touch_input_device, 1, 0);
}
void delayed_touch_release(uint32_t argument)
{
    (void)argument;
    return r1_shared_power_client_release(2);
}
uint32_t r1_touch_record_op_0c(void)
{
    return r1_stock_dispatch_0c(r1_touch_output_device);
}
uint32_t r1_touch_device_op_lock1(void)
{
    (void)r1_stock_dispatch_08(r1_touch_output_device);
    return r1_stock_dispatch_18(r1_touch_output_device, 1, 0);
}
uint32_t r1_touch_device_op_unlock(void)
{
    (void)r1_stock_dispatch_08(r1_touch_output_device);
    return r1_stock_dispatch_18(r1_touch_output_device, 0, 0);
}
