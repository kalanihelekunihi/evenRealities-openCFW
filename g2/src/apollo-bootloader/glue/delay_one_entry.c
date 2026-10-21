/* Deep-sleep's delay_one(1) uses original stock delay target 0x41d1c0. */
#include <stdint.h>
__attribute__((naked)) void delay_one(uint32_t microseconds)
{
    __asm__ volatile("b.w opencfw_boot_delay_us_math");
}
