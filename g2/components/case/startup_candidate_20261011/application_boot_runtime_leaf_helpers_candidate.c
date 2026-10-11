/* SPDX-License-Identifier: MIT
 * Native CASE 0x080001e6 zero-fill, 0x080001ea preserving-fill wrapper,
 * and 0x0800a794/0xa7a2 delay leaves.
 */
#include <stdint.h>
extern void case_boot_task_fill(uint32_t,uint32_t,uint8_t); /* 0x01d8 */
void case_boot_zero_fill(uint32_t destination,uint32_t count)
{case_boot_task_fill(destination,count,0u);}
void *case_boot_memset_return_start(void *destination,uint32_t value,uint32_t count)
{
    case_boot_task_fill((uint32_t)(uintptr_t)destination,count,value);
    return destination;
}
void case_boot_short_delay_a794(uint32_t count)
{for(int32_t i=0;i<(int32_t)count;++i)__asm__ volatile("nop");}
void case_boot_short_delay_a7a2(uint32_t count)
{for(int32_t i=0;i<(int32_t)count;++i)__asm__ volatile("nop");}
