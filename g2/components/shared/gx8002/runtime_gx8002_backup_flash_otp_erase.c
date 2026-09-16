/* SPDX-License-Identifier: MIT */
/* Recovered backup package 0x3fb7c. Unsupported manufacturers return success without
 * work. Descriptor values are snapshotted before helpers can mutate state. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);

extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
static inline uint8_t address_byte(unsigned address, unsigned width, unsigned index)
{
    unsigned shift=((width-index)*8u)&63u;
    return shift<32u ? (uint8_t)(address>>shift) : 0;
}
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
        open_cfw_gx8002_flash_command_write(6,0,0);
        unsigned width=open_cfw_gx8002_flash_state.address_bytes;
        unsigned address=base+(flags&7)*stride;
        for (unsigned i=1;i<=3;++i)
            open_cfw_gx8002_flash_state.command[i]=address_byte(address,width,i);
        unsigned opcode=open_cfw_gx8002_flash_state.command[0];
        open_cfw_gx8002_flash_state.command[4]=address_byte(address,width,4);
        open_cfw_gx8002_flash_command_write(opcode,
            (const uint8_t *)open_cfw_gx8002_flash_state.command+1,3);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}
