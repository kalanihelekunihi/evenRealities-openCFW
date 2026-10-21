#include "native_stacmd.h"
#include <stdint.h>
#include "native_battery_memory.h"
static uint32_t line_call(uint32_t offset)
{
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    uint32_t (*callback)(uint32_t)=(void *)(uintptr_t)read32(p+offset);
    return callback(read32(p+12));
}
uint32_t r1_stacmd_bus_recovery_native(void)
{
    (void)line_call(20);
    (void)line_call(24);
    (void)line_call(20);
    r1_stacmd_recovery_delay_native();
    /* Native loads the pin and low callback together at this point. */
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    uint32_t pin=read32(p+12);
    uint32_t (*low)(uint32_t)=(void *)(uintptr_t)read32(p+16);
    (void)low(pin);
    r1_stacmd_recovery_delay_native();
    r1_stacmd_recovery_delay_native();
    r1_stacmd_recovery_delay_native();
    r1_stacmd_recovery_delay_native();
    return line_call(20);
}
