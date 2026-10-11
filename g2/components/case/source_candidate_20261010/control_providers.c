#include <stdint.h>

/* Stock 0x08004e9e: write one selected control register. */
void case_control_write(uint32_t base, uint32_t mask, uint32_t enable)
{
    volatile uint32_t *const registers = (volatile uint32_t *)(uintptr_t)base;
    if (enable != 0u) {
        registers[0x18u / 4u] = mask;
    } else {
        registers[0x28u / 4u] = mask;
    }
}

/* Stock 0x08006b80 and 0x08006b98. */
void case_control_a(uint32_t enable)
{
    case_control_write(0x50000000u, 0x40u, enable != 0u);
}

void case_control_b(uint32_t enable)
{
    case_control_write(0x50000000u, 0x80u, enable != 0u);
}
