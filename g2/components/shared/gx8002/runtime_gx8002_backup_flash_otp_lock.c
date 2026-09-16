/* SPDX-License-Identifier: MIT */
/* Recovered backup package 0x3fa9c. Snapshot region before waiting, but reload the
 * selected device afterward. Unsupported manufacturers return before any status write. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_command_read(unsigned, uint8_t *, unsigned);
extern int backup_flash_status_write(const uint8_t *,unsigned,unsigned);
int open_cfw_gx8002_flash_otp_lock(void)
{
    uintptr_t device=open_cfw_gx8002_flash_state.selected_device;
    uintptr_t descriptor=*(volatile uint32_t *)(device+20);
    uint32_t flags=*(volatile uint32_t *)(descriptor+16);
    open_cfw_gx8002_flash_wait_ready();
    device=open_cfw_gx8002_flash_state.selected_device;
    int manufacturer=*(volatile int16_t *)(device+6);
    if (manufacturer!=0x5e && manufacturer!=0x85) return -1;
    uint8_t command[2],status2;
    open_cfw_gx8002_flash_command_read(5,command,1);
    open_cfw_gx8002_flash_command_read(0x35,&status2,1);
    command[1]=(uint8_t)(status2 | (1u<<((flags&7)+3)));
    backup_flash_status_write(command,2,1);
    return 0;
}
