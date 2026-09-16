/* SPDX-License-Identifier: MIT */
/* Backup package 0x3f92c. Snapshot the identifier before waiting; reload
 * the profile afterward. The output can alias state, so preserve ordering. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_command_read(unsigned, uint8_t *, unsigned);
extern int backup_flash_status_write(const uint8_t *, unsigned, unsigned);
extern uint32_t open_cfw_gx8002_backup_flash_protection_query(void);
int open_cfw_gx8002_backup_flash_protection_set(uint32_t requested, uint32_t *actual)
{
    volatile uint32_t *device=(volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    volatile uint8_t command[2]={0,0};
    *actual=0;
    volatile uint32_t *profile=(volatile uint32_t *)(uintptr_t)device[4];
    if (!profile || !profile[0]) return requested ? -1 : 0;
    unsigned identifier=device[1];
    uint8_t status;
    do { open_cfw_gx8002_flash_command_read(5,&status,1); } while (status&1);
    device=(volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    profile=(volatile uint32_t *)(uintptr_t)device[4];
    unsigned count=profile[1];
    volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)profile[0];
    unsigned value1=0,value2=0,mask1=0,mask2=0;
    for (unsigned i=0;i!=count;++i,entry+=8) {
        uint32_t length=*(volatile uint32_t *)(entry+4);
        if (requested<length) break;
        value1=entry[0];
        value2=entry[2];
        mask1=entry[1];
        mask2=entry[3];
    }
    unsigned manufacturer=identifier>>16;
    if (manufacturer!=0x5e && manufacturer!=0x85) return -1;
    open_cfw_gx8002_flash_command_read(5,&status,1);
    command[0]=(uint8_t)((status&~mask1)|value1);
    open_cfw_gx8002_flash_command_read(0x35,&status,1);
    command[1]=(uint8_t)((status&~mask2)|value2);
    backup_flash_status_write((const uint8_t *)command,2,1);
    do { open_cfw_gx8002_flash_command_read(5,&status,1); } while (status&1);
    uint32_t observed=open_cfw_gx8002_backup_flash_protection_query();
    if (observed==UINT32_MAX) return -1;
    *actual=observed;
    return 0;
}
