/* SPDX-License-Identifier: MIT */
/* Recovered gx_spi_flash_gettype at package 0x167e8. */
#include "runtime_gx8002_flash_interface_table.h"
char *open_cfw_gx8002_flash_type_api(const struct open_cfw_gx8002_flash_interface_table *device)
{
    return device->gettype ? device->gettype() : 0;
}
