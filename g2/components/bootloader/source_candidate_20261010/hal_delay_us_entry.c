/* Original deep-sleep BL 0x41a88c / 0x41aa8e targets stock 0x41d1c0. */
#include <stdint.h>
__attribute__((naked)) void opencfw_hal_delay_us(uint32_t microseconds)
{
    __asm__ volatile("b.w opencfw_boot_delay_us_math");
}
