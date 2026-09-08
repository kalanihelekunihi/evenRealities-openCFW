/* SPDX-License-Identifier: MIT */
/* Recovered package0x15bec. Unsupported manufacturers return success without
 * work. Descriptor values are snapshotted before helpers can mutate state. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_write_enable(void);
extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
extern void open_cfw_gx8002_flash_encode_address(const volatile uint32_t *,unsigned,uint8_t *);
int open_cfw_gx8002_flash_otp_erase(void)
{
    uintptr_t device=open_cfw_gx8002_flash_state.selected_device;
    int manufacturer=*(volatile int16_t *)(device+6);
    if (manufacturer==0x5e || manufacturer==0x85) {
        uintptr_t descriptor=*(volatile uint32_t *)(device+20);
        uint32_t flags=*(volatile uint32_t *)(descriptor+16);
        uint32_t base=*(volatile uint32_t *)(descriptor+0);
        uint32_t stride=*(volatile uint32_t *)(descriptor+4);
        open_cfw_gx8002_flash_state.command[0]=0x44;
        open_cfw_gx8002_flash_wait_ready();
        open_cfw_gx8002_flash_write_enable();
        open_cfw_gx8002_flash_encode_address(&open_cfw_gx8002_flash_state.address_bytes,
            base+(flags&7)*stride,(uint8_t *)open_cfw_gx8002_flash_state.command);
        open_cfw_gx8002_flash_command_write(open_cfw_gx8002_flash_state.command[0],
            (const uint8_t *)open_cfw_gx8002_flash_state.command+1,3);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}
