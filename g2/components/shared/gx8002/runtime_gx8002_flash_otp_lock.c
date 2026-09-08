/* SPDX-License-Identifier: MIT */
/* Recovered package 0x16264. Snapshot region before waiting; reload device
 * afterward. The final status-register write is not followed by another wait. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_read_status(void);
extern int open_cfw_gx8002_flash_read_status2(void);
extern int open_cfw_gx8002_flash_write_enable(void);
extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
int open_cfw_gx8002_flash_otp_lock(void)
{
    uintptr_t device=open_cfw_gx8002_flash_state.selected_device;
    uintptr_t descriptor=*(volatile uint32_t *)(device+20);
    uint32_t flags=*(volatile uint32_t *)(descriptor+16);
    open_cfw_gx8002_flash_wait_ready();
    device=open_cfw_gx8002_flash_state.selected_device;
    int manufacturer=*(volatile int16_t *)(device+6);
    if (manufacturer!=0x5e && manufacturer!=0x85) return -1;
    uint8_t command[2];
    command[0]=(uint8_t)open_cfw_gx8002_flash_read_status();
    command[1]=(uint8_t)((unsigned)open_cfw_gx8002_flash_read_status2() |
                         (1u<<((flags&7)+3)));
    open_cfw_gx8002_flash_wait_ready();
    open_cfw_gx8002_flash_write_enable();
    open_cfw_gx8002_flash_command_write(1,command,2);
    return 0;
}
