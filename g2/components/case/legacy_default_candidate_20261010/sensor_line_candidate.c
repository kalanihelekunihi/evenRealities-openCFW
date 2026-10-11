/* SPDX-License-Identifier: MIT
 * Stock line selectors 0x0800a550/0x0800a574, to 0x08004e9e.
 * Runtime byte 0x20000114 chooses which of pins 8/16 is clock/data.
 * The selected GPIO writer is source-owned; pin timing/electrical state is not.
 */
#include <stdint.h>
extern void case_control_write(uint32_t base,uint32_t mask,uint32_t enable);

void case_binary_sensor_line_a(uint32_t level)
{
    uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x20000114u ? 16u : 8u;
    case_control_write(0x50000400u,mask,level);
}
void case_binary_sensor_line_b(uint32_t level)
{
    uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x20000114u ? 8u : 16u;
    case_control_write(0x50000400u,mask,level);
}
