/* Stock 0x510d8 publishes count 2 before reading either chip ID, then
 * disables the pair and releases the bus after both ordered byte stores. */
#include <stdint.h>
extern void r1_gxt310_bus_acquire(void),r1_gxt310_bus_release(void);
extern uint32_t r1_gxt310_enable_pair_native(void);
extern void r1_gxt310_disable_pair_native(void);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_gxt310_chip_id_channel0(void),r1_gxt310_chip_id_channel2(void);
__attribute__((noinline)) void r1_gxt310_id_pair_read(volatile uint8_t *buffer)
{
    volatile uint8_t *out=buffer;
    r1_gxt310_bus_acquire();
    (void)r1_gxt310_enable_pair_native();
    (void)osDelay(80);
    out[0]=2;
    out[1]=(uint8_t)r1_gxt310_chip_id_channel0();

    out[2]=(uint8_t)r1_gxt310_chip_id_channel2();
    r1_gxt310_disable_pair_native();
    r1_gxt310_bus_release();
}
