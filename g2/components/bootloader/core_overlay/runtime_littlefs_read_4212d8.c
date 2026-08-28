/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader LittleFS read callback. */

typedef __INT32_TYPE__ open_cfw_littlefs_read_i32;
typedef __UINT32_TYPE__ open_cfw_littlefs_read_u32;
typedef __UINTPTR_TYPE__ open_cfw_littlefs_read_word;

enum {
    OPEN_CFW_LITTLEFS_READ_BASE = 0x01400000U,
    OPEN_CFW_LITTLEFS_READ_BLOCK_SHIFT = 12,
    OPEN_CFW_LITTLEFS_READ_ERROR = -5
};

open_cfw_littlefs_read_u32 open_cfw_bootloader_mspi_read_420f70(
    open_cfw_littlefs_read_u32 address, void *buffer,
    open_cfw_littlefs_read_u32 size);

unsigned int open_cfw_bootloader_log_dispatch(const char *format, ...);

__attribute__((used, noinline))
open_cfw_littlefs_read_i32 open_cfw_bootloader_littlefs_read_4212d8(
    const void *configuration, open_cfw_littlefs_read_u32 block,
    open_cfw_littlefs_read_u32 offset, void *buffer,
    open_cfw_littlefs_read_u32 size)
{
    open_cfw_littlefs_read_u32 address = OPEN_CFW_LITTLEFS_READ_BASE
        + (block << OPEN_CFW_LITTLEFS_READ_BLOCK_SHIFT) + offset;
    open_cfw_littlefs_read_u32 status;

    (void)configuration;
    status = open_cfw_bootloader_mspi_read_420f70(address, buffer, size);
    if (status != 0U) {
        (void)open_cfw_bootloader_log_dispatch(
            (const char *)(open_cfw_littlefs_read_word)0x004317CCU,
            block, offset, size, address, status);
        return OPEN_CFW_LITTLEFS_READ_ERROR;
    }
    return 0;
}
