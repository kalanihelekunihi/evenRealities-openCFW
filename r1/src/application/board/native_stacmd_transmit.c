#include "native_stacmd.h"
#include <stdint.h>
#include "native_battery_memory.h"
/* GPIO callbacks have void C semantics. The historical helper name is kept
 * for existing references; no caller consumes a callback return word. */
__attribute__((noinline,used)) void r1_stacmd_gpio_result(
 uint32_t pin,void (*callback)(uint32_t))
{
    callback(pin);
}
static void line_call(uint32_t offset)
{
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    void (*callback)(uint32_t)=(void *)(uintptr_t)read32(p+offset);
    r1_stacmd_gpio_result(read32(p+12),callback);
}
static void select_output_low(void)
{
    (void)line_call(20);(void)line_call(24);(void)line_call(20);
    volatile uint8_t *p=(volatile uint8_t *)&r1_stacmd;
    uint32_t pin=read32(p+12);
    void (*low)(uint32_t)=(void *)(uintptr_t)read32(p+16);
    low(pin);
}
void r1_stacmd_drive_bit_native(uint32_t bit)
{
    select_output_low();
    for (uint32_t i=0;i<(bit ? 52u : 13u);i++) {
        __builtin_arm_nop();
        __builtin_arm_nop();
        __builtin_arm_nop();
        __builtin_arm_nop();
    }
    line_call(20);
}
void r1_stacmd_write_bits_native(uint32_t value,uint32_t header)
{
    for (int32_t bit=header==1 ? 6 : 7;bit>=0;bit--)
        r1_stacmd_drive_bit_native((value>>bit)&1u);
}
void r1_stacmd_idle_native(void)
{
    select_output_low();r1_stacmd_recovery_delay_native();line_call(20);
}
uint32_t r1_stacmd_parity_native(uint32_t value)
{
    uint32_t parity=0;
    for (uint32_t bit=0;bit<8;bit++) parity^=(value>>bit)&1u;
    return parity;
}
