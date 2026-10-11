/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ca6c scheduler counter reader.
 */
#include <stdint.h>
uint32_t case_boot_scheduler_counter_read(void)
{return *(volatile uint32_t *)(uintptr_t)0x20000134u;}
