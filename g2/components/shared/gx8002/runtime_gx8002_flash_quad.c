/* SPDX-License-Identifier: MIT */
/* Recovered image-A quad-enable sequences. Device selection is performed
 * by the flash initializer. All callees have separate C reconstructions. */
#include <stdint.h>
extern unsigned int open_cfw_gx8002_flash_read_status(void);
extern unsigned int open_cfw_gx8002_flash_read_status2(void);
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_write_enable(void);
extern int open_cfw_gx8002_flash_command_write(unsigned int, const uint8_t *, unsigned int);

int open_cfw_gx8002_flash_quad_enable(void)
{
    unsigned int value = open_cfw_gx8002_flash_read_status2();
    if (!(value & 2u)) {
        uint8_t status = value | 2u;
        open_cfw_gx8002_flash_wait_ready();
        open_cfw_gx8002_flash_write_enable();
        open_cfw_gx8002_flash_command_write(0x31, &status, 1);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}

int open_cfw_gx8002_flash_quad_enable_pair(void)
{
    uint8_t status[2];
    status[0] = open_cfw_gx8002_flash_read_status();
    unsigned int value = open_cfw_gx8002_flash_read_status2();
    if (!(value & 2u)) {
        status[1] = value | 2u;
        open_cfw_gx8002_flash_wait_ready();
        open_cfw_gx8002_flash_write_enable();
        open_cfw_gx8002_flash_command_write(1, status, 2);
        open_cfw_gx8002_flash_wait_ready();
    }
    return 0;
}
