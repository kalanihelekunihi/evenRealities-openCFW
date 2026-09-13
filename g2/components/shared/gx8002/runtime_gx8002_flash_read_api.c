/* SPDX-License-Identifier: MIT */
/* Recovered gx_spi_flash_readdata at package 0x167cc. */
#include "runtime_gx8002_flash_interface_table.h"
int open_cfw_gx8002_flash_read_api(const struct open_cfw_gx8002_flash_interface_table *device,
                                 unsigned address, void *buffer, unsigned length)
{
    return device->readdata ? device->readdata(address, buffer, length) : -1;
}
