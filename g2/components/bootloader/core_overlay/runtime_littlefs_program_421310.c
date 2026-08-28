/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader LittleFS program callback. */

typedef __INT32_TYPE__ open_cfw_littlefs_program_i32;
typedef __UINT8_TYPE__ open_cfw_littlefs_program_u8;
typedef __UINT32_TYPE__ open_cfw_littlefs_program_u32;
typedef __UINTPTR_TYPE__ open_cfw_littlefs_program_word;

enum {
    OPEN_CFW_LITTLEFS_PROGRAM_BASE = 0x01400000U,
    OPEN_CFW_LITTLEFS_PROGRAM_BLOCK_SHIFT = 12,
    OPEN_CFW_LITTLEFS_PROGRAM_ERROR = -5
};

open_cfw_littlefs_program_u32 open_cfw_bootloader_mspi_program_420b0c(
    open_cfw_littlefs_program_u32 address,
    const open_cfw_littlefs_program_u8 *buffer,
    open_cfw_littlefs_program_u32 size);

unsigned int open_cfw_bootloader_log_dispatch(const char *format, ...);

__attribute__((used, noinline))
open_cfw_littlefs_program_i32 open_cfw_bootloader_littlefs_program_421310(
    const void *configuration, open_cfw_littlefs_program_u32 block,
    open_cfw_littlefs_program_u32 offset, const void *buffer,
    open_cfw_littlefs_program_u32 size)
{
    open_cfw_littlefs_program_u32 address = OPEN_CFW_LITTLEFS_PROGRAM_BASE
        + (block << OPEN_CFW_LITTLEFS_PROGRAM_BLOCK_SHIFT) + offset;
    open_cfw_littlefs_program_u32 status;

    (void)configuration;
    status = open_cfw_bootloader_mspi_program_420b0c(
        address, (const open_cfw_littlefs_program_u8 *)buffer, size);
    if (status != 0U) {
        (void)open_cfw_bootloader_log_dispatch(
            (const char *)(open_cfw_littlefs_program_word)0x0043180CU,
            block, offset, size, address, status);
        return OPEN_CFW_LITTLEFS_PROGRAM_ERROR;
    }
    return 0;
}
