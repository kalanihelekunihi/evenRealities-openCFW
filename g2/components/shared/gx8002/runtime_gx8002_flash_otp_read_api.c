/* SPDX-License-Identifier: MIT */
/* Recovered gx_spi_flash_otp_read at package 0x16808. */
#include "runtime_gx8002_flash_interface_table.h"
int open_cfw_gx8002_flash_otp_read_api(const struct open_cfw_gx8002_flash_interface_table *device,
                                 unsigned address, uint8_t *buffer, unsigned length)
{
    return device->otp_read ? device->otp_read(address, buffer, length) : -1;
}
