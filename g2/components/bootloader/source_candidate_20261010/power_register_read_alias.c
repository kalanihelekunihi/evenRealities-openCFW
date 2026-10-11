/* Historical startup clockmux caller of stock Thumb 0x41d90e. */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_power_register_read(uint32_t register_id,
                                                            uint32_t *value_out)
{
    __asm__ volatile("b.w opencfw_bl_power_register_read");
}
