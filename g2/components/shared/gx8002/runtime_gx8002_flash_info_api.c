/* SPDX-License-Identifier: MIT */
/* Recovered gx_spi_flash_getinfo at package 0x167f4. */
#include "runtime_gx8002_flash_interface_table.h"
int open_cfw_gx8002_flash_info_api(const struct open_cfw_gx8002_flash_interface_table *device,
                                unsigned selector)
{
    return device->getinfo ? device->getinfo(selector) : -1;
}
