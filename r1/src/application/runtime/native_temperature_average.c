#include <stdint.h>
extern void r1_gxt310_bus_acquire(void),r1_gxt310_bus_release(void);
extern uint32_t r1_gxt310_enable_pair_native(void);
extern void r1_gxt310_disable_pair_native(void);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_gxt310_temperature_channel0(void),r1_gxt310_temperature_channel2(void);

/* Stock 0x50e1c: unsigned addition wraps before signed division truncates
 * toward zero. Multiplication wraps as a raw 32-bit return word. */
__attribute__((noinline)) uint32_t r1_gxt310_temp_average_read(void)
{
    uint32_t sum;
    r1_gxt310_bus_acquire();
    (void)r1_gxt310_enable_pair_native();
    (void)osDelay(80);
    sum = r1_gxt310_temperature_channel0();
    
    sum += r1_gxt310_temperature_channel2();
    r1_gxt310_disable_pair_native();
    r1_gxt310_bus_release();
    uint32_t average = (uint32_t)((int32_t)sum / 2);
    return average * 100u;
}
