/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_backup_bss_start[];
extern uint32_t open_cfw_gx8002_backup_bss_end[];
/* Invoked only on the startup path that requests initialization of BSS. */
void open_cfw_gx8002_backup_clear_bss(void)
{
    uintptr_t cursor = (uintptr_t)open_cfw_gx8002_backup_bss_start;
    uintptr_t end = (uintptr_t)open_cfw_gx8002_backup_bss_end;
    while (cursor < end) {
        *(volatile uint32_t *)cursor = 0;
        cursor += sizeof(uint32_t);
    }
}

/* Preserve the original bound-literal slots as source-defined pointers. */
__attribute__((section(".backup_bss_bounds"), used))
uint32_t * const open_cfw_gx8002_backup_bss_bounds[2] = {
    open_cfw_gx8002_backup_bss_end,
    open_cfw_gx8002_backup_bss_start
};
