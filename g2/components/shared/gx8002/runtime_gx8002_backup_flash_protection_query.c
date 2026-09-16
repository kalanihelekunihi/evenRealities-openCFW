/* SPDX-License-Identifier: MIT */
/* Backup package 0x3f844: protection length query. Reload the device after
 * readiness and reload its profile after both status reads. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_command_read(unsigned, uint8_t *, unsigned);
uint32_t open_cfw_gx8002_backup_flash_protection_query(void)
{
    volatile uint32_t *device=(volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    volatile uint32_t *profile=(volatile uint32_t *)(uintptr_t)device[4];
    if (!profile || !profile[0]) return UINT32_MAX;
    uint8_t status;
    do { open_cfw_gx8002_flash_command_read(5,&status,1); } while (status&1);
    device=(volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    unsigned manufacturer=*(volatile uint16_t *)((uintptr_t)device+6);
    if (manufacturer!=0x5e && manufacturer!=0x85) return UINT32_MAX;
    open_cfw_gx8002_flash_command_read(5,&status,1);
    unsigned first=status;
    open_cfw_gx8002_flash_command_read(0x35,&status,1);
    unsigned second=status;
    device=(volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    profile=(volatile uint32_t *)(uintptr_t)device[4];
    unsigned count=profile[1];
    if (!count) return UINT32_MAX;
    volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)profile[0];
    for (unsigned i=0;i!=count;++i,entry+=8) {
        unsigned mask1=entry[1];
        unsigned expected1=entry[0];
        unsigned expected2=entry[2];
        unsigned mask2=entry[3];
        uint32_t length=*(volatile uint32_t *)(entry+4);
        if ((first&mask1)==expected1 && (second&mask2)==expected2) return length;
    }
    return UINT32_MAX;
}
