/* SPDX-License-Identifier: MIT */
/* Recovered backup-image public protection callbacks. The query and set
 * engines are separate functions, still requiring source qualification. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern uint32_t open_cfw_gx8002_backup_flash_protection_query(void);
extern int open_cfw_gx8002_backup_flash_protection_set(uint32_t, uint32_t *);
int open_cfw_gx8002_flash_write_protect_status(uint32_t *length)
{
    *length = 0;
    uint32_t result = open_cfw_gx8002_backup_flash_protection_query();
    *length = result;
    return result == UINT32_MAX ? -1 : 0;
}
int open_cfw_gx8002_flash_write_protect_mode(void)
{
    volatile uint32_t *device = (volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    volatile uint32_t *profile = (volatile uint32_t *)(uintptr_t)device[4];
    return profile && profile[0] ? 1 : -1;
}
int open_cfw_gx8002_flash_write_protect_lock(uint32_t length)
{
    uint32_t actual;
    return open_cfw_gx8002_backup_flash_protection_set(length, &actual);
}
int open_cfw_gx8002_flash_write_protect_unlock(void)
{
    uint32_t actual;
    return open_cfw_gx8002_backup_flash_protection_set(0, &actual);
}
