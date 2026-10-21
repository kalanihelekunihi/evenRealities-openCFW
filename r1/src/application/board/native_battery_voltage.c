#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_device_context[];
extern uint32_t r1_advertising_configuration_byte_get(void);
extern uint32_t r1_battery_runtime_update_service(void);
/* Native0x31fcc is a four-byte NOP prefix falling into0x31fd0. Keep the
 * prefix/flow explicit, separate from the overlapping ownership span. */
__attribute__((noinline)) uint32_t r1_battery_runtime_service(void)
{
    __asm__ volatile("nop.w");
    return r1_battery_runtime_update_service();
}
uint32_t r1_battery_voltage_get(void)
{
    if (r1_advertising_configuration_byte_get()==0x55u)
        (void)r1_battery_runtime_service();
    return read16(r1_battery_device_context+42);
}
