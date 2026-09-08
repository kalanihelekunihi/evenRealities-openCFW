/* SPDX-License-Identifier: MIT */
/* Candidate recovered from package0x15d6c..0x15e28. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_write_enable(void);
extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
extern void open_cfw_gx8002_flash_encode_address(const volatile uint32_t *,unsigned,uint8_t *);
int open_cfw_gx8002_flash_erase(unsigned address,unsigned length)
{
    unsigned size=open_cfw_gx8002_flash_state.usable_bytes;
    if (address>=size) return -22;
    unsigned end=address+length; /* Preserve target unsigned wrap. */
    if (end>size) end=size;
    address&=~4095u;
    unsigned remaining=end-address;
    while (remaining) {
        unsigned rounded=remaining<4096u ? 4096u : remaining;
        if (!(address&65535u) && rounded>=65536u) {
        open_cfw_gx8002_flash_wait_ready();
        open_cfw_gx8002_flash_write_enable();
        open_cfw_gx8002_flash_encode_address(&open_cfw_gx8002_flash_state.address_bytes,
            address,(uint8_t *)open_cfw_gx8002_flash_state.command);
        open_cfw_gx8002_flash_command_write(0xd8,
            (const uint8_t *)open_cfw_gx8002_flash_state.command+1,3);
        open_cfw_gx8002_flash_wait_ready();
        address+=65536u;
        remaining=rounded-65536u;
        } else {
        open_cfw_gx8002_flash_wait_ready();
        open_cfw_gx8002_flash_write_enable();
        open_cfw_gx8002_flash_encode_address(&open_cfw_gx8002_flash_state.address_bytes,
            address,(uint8_t *)open_cfw_gx8002_flash_state.command);
        open_cfw_gx8002_flash_command_write(0x20,
            (const uint8_t *)open_cfw_gx8002_flash_state.command+1,3);
        open_cfw_gx8002_flash_wait_ready();
        address+=4096u;
        remaining=rounded-4096u;
        }
    }
    return 0;
}
int open_cfw_gx8002_flash_chip_erase(void)
{
    return open_cfw_gx8002_flash_erase(0,open_cfw_gx8002_flash_state.usable_bytes);
}
