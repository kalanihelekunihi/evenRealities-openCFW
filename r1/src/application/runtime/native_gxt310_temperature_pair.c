/* Stock 0x51260 writes channel 0 then channel 2 as raw halfwords.
 * Keep that order for overlapping output pointers, then release the bus. */
#include <stdint.h>
#include "../board/native_battery_memory.h"
extern void r1_gxt310_bus_acquire(void),r1_gxt310_bus_release(void);
extern uint32_t r1_gxt310_enable_pair_native(void);
extern void r1_gxt310_disable_pair_native(void);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_gxt310_temperature_channel0(void),r1_gxt310_temperature_channel2(void);
__attribute__((noinline)) void r1_gxt310_temp_pair_read(volatile void *out0,
                                                     volatile void *out2)
{
    uintptr_t second=(uintptr_t)out2,first=(uintptr_t)out0;
    r1_gxt310_bus_acquire();
    (void)r1_gxt310_enable_pair_native();
    (void)osDelay(80);
    write16((volatile uint8_t *)first,r1_gxt310_temperature_channel0());

    write16((volatile uint8_t *)second,r1_gxt310_temperature_channel2());
    r1_gxt310_disable_pair_native();
    r1_gxt310_bus_release();
}
