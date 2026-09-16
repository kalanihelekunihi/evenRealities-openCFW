/* SPDX-License-Identifier: MIT */
/* Backup whole-device erase helper and callback, package 0x408a4/0x408b8. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_erase(unsigned,unsigned);
__attribute__((noinline)) int open_cfw_gx8002_backup_erase_all(void)
{
    return open_cfw_gx8002_flash_erase(0,open_cfw_gx8002_flash_state.usable_bytes);
}
int open_cfw_gx8002_flash_chip_erase(void)
{
    return open_cfw_gx8002_backup_erase_all();
}
