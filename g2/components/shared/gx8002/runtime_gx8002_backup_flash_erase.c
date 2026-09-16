/* SPDX-License-Identifier: MIT */
/* Backup range erase at package 0x3ff8c. Candidate awaiting decoded comparison. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);

extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
static inline __attribute__((always_inline)) void encode(unsigned address)
{
    unsigned width=open_cfw_gx8002_flash_state.address_bytes;
    for (unsigned i=1;i<=4;++i) {
        unsigned shift=((width-i)*8u)&63u;
        open_cfw_gx8002_flash_state.command[i]=shift<32u ? (uint8_t)(address>>shift) : 0;
    }
}
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
        open_cfw_gx8002_flash_command_write(6,0,0);
        encode(address);
        open_cfw_gx8002_flash_command_write(0xd8,
            (const uint8_t *)open_cfw_gx8002_flash_state.command+1,3);
        open_cfw_gx8002_flash_wait_ready();
        address+=65536u;
        remaining=rounded-65536u;
        } else {
        open_cfw_gx8002_flash_wait_ready();
        open_cfw_gx8002_flash_command_write(6,0,0);
        encode(address);
        open_cfw_gx8002_flash_command_write(0x20,
            (const uint8_t *)open_cfw_gx8002_flash_state.command+1,3);
        open_cfw_gx8002_flash_wait_ready();
        address+=4096u;
        remaining=rounded-4096u;
        }
    }
    return 0;
}