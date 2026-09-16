/* SPDX-License-Identifier: MIT */
/* Backup program helper 0x3fd6c and wrapper 0x3fe00. Unsigned sums wrap. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
__attribute__((noinline)) int open_cfw_gx8002_backup_program_pages(unsigned address,const void *buffer,unsigned length)
{
    open_cfw_gx8002_flash_wait_ready();
    unsigned offset=address&255u;
    open_cfw_gx8002_flash_command_write(6,0,0);
    int (*program)(unsigned,const uint32_t *,unsigned)=open_cfw_gx8002_flash_state.program_words;
    if (length+offset<=256u) {
        program(address,(const uint32_t *)buffer,length);
        return 0;
    }
    unsigned done=256u-offset;
    program(address,(const uint32_t *)buffer,done);
    while (done<length) {
        unsigned chunk=length-done;
        if (chunk>256u) chunk=256u;
        open_cfw_gx8002_flash_command_write(6,0,0);
        open_cfw_gx8002_flash_state.program_words(address+done,
            (const uint32_t *)((uintptr_t)buffer+done),chunk);
        done+=chunk;
    }
    return 0;
}

int open_cfw_gx8002_flash_page_program(unsigned address,const void *buffer,unsigned length)
{
    if (!length) return 0;
    if (address+length>open_cfw_gx8002_flash_state.usable_bytes) return -22;
    return open_cfw_gx8002_backup_program_pages(address,buffer,length);
}
