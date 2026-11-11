#include <stdint.h>
#include "native_battery_context.h"
#include "native_battery_memory.h"
extern uint32_t r1_advertising_configuration_byte_get(void);
extern uint32_t r1_battery_runtime_update_service(void);
/* Stock 0x31fcc falls through a NOP prefix into the runtime update.
 * The C wrapper expresses the call without instruction-layout padding. */
__attribute__((noinline)) uint32_t r1_battery_runtime_service(void)
{
    return r1_battery_runtime_update_service();
}
uint32_t r1_battery_voltage_get(void)
{
    if (r1_advertising_configuration_byte_get()==0x55u)
        (void)r1_battery_runtime_service();
    return read16(r1_battery_device_context+42);
}
