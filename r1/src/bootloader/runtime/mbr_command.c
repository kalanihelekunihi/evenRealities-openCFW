/* Checked C call into the independently linked first-page MBR command
 * entry. INIT_SD also records the validated lower Cordio descriptor in the
 * bootloader, so that command remains on this side of the boundary. */
#include <stdint.h>
#include "nrf_error.h"
#include "nrf_mbr.h"
#include "../../mbr/copy_record.h"
#include "cordio_region_init.h"

#if defined(SVCALL_AS_NORMAL_FUNCTION)
uint32_t sd_mbr_command(sd_mbr_command_t *command)
{
    if (command == 0) return NRF_ERROR_NULL;
    if (command->command == SD_MBR_COMMAND_INIT_SD)
        return r1_bootloader_cordio_region_init();
    if (*(volatile const uint32_t *)R1_MBR_COMMAND_TAG_ADDRESS !=
        R1_MBR_COMMAND_TAG)
        return NRF_ERROR_NOT_SUPPORTED;
    uint32_t (*entry)(sd_mbr_command_t *) =
        (uint32_t (*)(sd_mbr_command_t *))(uintptr_t)R1_MBR_COMMAND_ENTRY;
    return entry(command);
}
#endif
