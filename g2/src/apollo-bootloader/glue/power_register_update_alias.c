/* Historical startup alternative caller of stock Thumb 0x41d92c. */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_boot_power_register_update(uint32_t register_id,
                                                                    uint32_t value)
{
    __asm__ volatile("b.w opencfw_bl_power_register_update");
}
