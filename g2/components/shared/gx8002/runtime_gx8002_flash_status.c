/* SPDX-License-Identifier: MIT */
/* Recovered from image-A 0x15748..0x1579c. The command transport is
 * source-built separately. Polling intentionally has no timeout. */
#include <stdint.h>
extern int open_cfw_gx8002_flash_command_read(unsigned int, uint8_t *, unsigned int);
extern int open_cfw_gx8002_flash_command_write(unsigned int, const uint8_t *, unsigned int);

__attribute__((noinline)) unsigned int open_cfw_gx8002_flash_read_status(void)
{
    uint8_t status;
    open_cfw_gx8002_flash_command_read(5, &status, 1);
    return status;
}

int open_cfw_gx8002_flash_write_enable(void)
{
    open_cfw_gx8002_flash_command_write(6, 0, 0);
    return 0;
}

int open_cfw_gx8002_flash_wait_ready(void)
{
    while (open_cfw_gx8002_flash_read_status() & 1u) {}
    return 1;
}

unsigned int open_cfw_gx8002_flash_read_status2(void)
{
    uint8_t status;
    open_cfw_gx8002_flash_command_read(0x35, &status, 1);
    return status;
}
