/* SPDX-License-Identifier: MIT
 * Native CASE 0x080067b0 write one console control field.
 */
#include <stdint.h>
void case_boot_console_write_field(uint32_t base,uint32_t selector,uint32_t value)
{
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)(base+20u);
    uint32_t shift=selector&4u;
    *reg=(*reg&~(7u<<shift))|(value<<shift);
}
