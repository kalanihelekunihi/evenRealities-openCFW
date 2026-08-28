/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader LittleFS erase callback. */

typedef __INT32_TYPE__ open_cfw_littlefs_erase_i32;
typedef __UINT32_TYPE__ open_cfw_littlefs_erase_u32;
typedef __UINTPTR_TYPE__ open_cfw_littlefs_erase_word;

enum {
    OPEN_CFW_LITTLEFS_ERASE_BASE = 0x01400000U,
    OPEN_CFW_LITTLEFS_ERASE_BLOCK_SHIFT = 12,
    OPEN_CFW_LITTLEFS_ERASE_ERROR = -5
};

open_cfw_littlefs_erase_u32 open_cfw_bootloader_mspi_sector_erase_420a08(
    open_cfw_littlefs_erase_u32 address);

unsigned int open_cfw_bootloader_log_dispatch(const char *format, ...);

__attribute__((used, noinline))
open_cfw_littlefs_erase_i32 open_cfw_bootloader_littlefs_erase_421348(
    const void *configuration, open_cfw_littlefs_erase_u32 block)
{
    open_cfw_littlefs_erase_u32 address = OPEN_CFW_LITTLEFS_ERASE_BASE
        + (block << OPEN_CFW_LITTLEFS_ERASE_BLOCK_SHIFT);
    open_cfw_littlefs_erase_u32 status;

    (void)configuration;
    status = open_cfw_bootloader_mspi_sector_erase_420a08(address);
    if (status != 0U) {
        (void)open_cfw_bootloader_log_dispatch(
            (const char *)(open_cfw_littlefs_erase_word)0x00432568U,
            block, address, status);
        return OPEN_CFW_LITTLEFS_ERASE_ERROR;
    }
    return 0;
}
