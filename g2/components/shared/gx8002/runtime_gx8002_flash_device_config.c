/* SPDX-License-Identifier: MIT */
/* Device-specific configuration used for JEDEC 0x204016. Command transport
 * and readiness helpers are reconstructed separately; polling has no timeout. */
#include <stdint.h>
extern int open_cfw_gx8002_flash_command_read(unsigned int, uint8_t *, unsigned int);
extern int open_cfw_gx8002_flash_command_write(unsigned int, const uint8_t *, unsigned int);
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_write_enable(void);

int open_cfw_gx8002_flash_device_config(void)
{
    uint8_t status;
    open_cfw_gx8002_flash_command_read(0x15, &status, 1);
    if (!(status & 0x10)) {
        status |= 0x10;
        open_cfw_gx8002_flash_wait_ready();
        open_cfw_gx8002_flash_write_enable();
        open_cfw_gx8002_flash_command_write(0x11, &status, 1);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}
