/* SPDX-License-Identifier: MIT */
/* Backup status polling and device-specific configuration at 0x3fc90..3fd6c. */
#include <stdint.h>
extern int open_cfw_gx8002_flash_command_read(unsigned, uint8_t *, unsigned);
extern int backup_flash_status_write(const uint8_t *, unsigned, unsigned);
int open_cfw_gx8002_flash_wait_ready(void)
{
    uint8_t status;
    int result;
    do { result = open_cfw_gx8002_flash_command_read(5, &status, 1); }
    while (status & 1u);
    return result;
}
int open_cfw_gx8002_flash_quad_enable_pair(void)
{
    uint8_t status[2], value;
    open_cfw_gx8002_flash_command_read(5, &status[0], 1);
    open_cfw_gx8002_flash_command_read(0x35, &value, 1);
    if (!(value & 2u)) {
        status[1] = value | 2u;
        backup_flash_status_write(status, 2, 1);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}
int open_cfw_gx8002_flash_quad_enable(void)
{
    uint8_t value;
    open_cfw_gx8002_flash_command_read(0x35, &value, 1);
    if (!(value & 2u)) {
        value |= 2u;
        backup_flash_status_write(&value, 1, 2);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}
int open_cfw_gx8002_flash_device_config(void)
{
    uint8_t value;
    open_cfw_gx8002_flash_command_read(0x15, &value, 1);
    if (!(value & 16u)) {
        value |= 16u;
        backup_flash_status_write(&value, 1, 3);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}
