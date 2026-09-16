/* SPDX-License-Identifier: MIT */
/* Recovered package 0x3f674. Register selectors 1/2/3 use commands
 * 0x01/0x31/0x11. Invalid lengths/selectors return before touching the bus.
 * The caller owns the final completion wait. */
#include <stdint.h>
extern int open_cfw_gx8002_flash_command_read(unsigned, uint8_t *, unsigned);
extern int open_cfw_gx8002_flash_command_write(unsigned, const uint8_t *, unsigned);
int backup_flash_status_write(const uint8_t *data, unsigned length, unsigned reg)
{
    unsigned command;
    uint8_t status;
    if (length > 2) return -1;
    if (reg == 2) command = 0x31;
    else if (reg == 3) command = 0x11;
    else if (reg == 1) command = 1;
    else return -1;
    do { open_cfw_gx8002_flash_command_read(5, &status, 1); }
    while (status & 1u);
    open_cfw_gx8002_flash_command_write(6, 0, 0);
    open_cfw_gx8002_flash_command_write(command, data, length);
    return 0;
}
