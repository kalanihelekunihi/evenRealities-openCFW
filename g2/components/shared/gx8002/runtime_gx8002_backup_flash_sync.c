/* SPDX-License-Identifier: MIT */
/* Backup sync at package 0x3fa58. The public SDK callback is void; keep
 * observed final transport r0 here for low-level differential comparison. */
#include <stdint.h>
extern int open_cfw_gx8002_flash_command_read(unsigned,uint8_t *,unsigned);
int open_cfw_gx8002_flash_sync(void)
{
    uint8_t status;
    int result;
    do { result=open_cfw_gx8002_flash_command_read(5,&status,1); }
    while (status&1u);
    return result;
}
