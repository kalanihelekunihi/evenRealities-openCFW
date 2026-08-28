/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 MX25U25643G JEDEC-ID reader.
 */

typedef __UINT8_TYPE__ open_cfw_read_id_u8;
typedef __UINT32_TYPE__ open_cfw_read_id_u32;
typedef __UINTPTR_TYPE__ open_cfw_read_id_word;

enum {
    OPEN_CFW_READ_ID_COMMAND = 0x9FU,
    OPEN_CFW_READ_ID_LENGTH = 3U,
    OPEN_CFW_READ_ID_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_READ_ID_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_READ_ID_LOG_FILE = 0x00431540U,
    OPEN_CFW_READ_ID_LOG_FUNCTION = 0x004337FCU,
    OPEN_CFW_READ_ID_FAIL_FORMAT = 0x00433AECU,
    OPEN_CFW_READ_ID_FAIL_LINE = 0x2D8U
};

typedef open_cfw_read_id_u32 (*open_cfw_read_id_command_fn)(
    open_cfw_read_id_u32, open_cfw_read_id_u32,
    open_cfw_read_id_u32, open_cfw_read_id_u8 *,
    open_cfw_read_id_u32);
typedef void (*open_cfw_read_id_log_fn)(
    open_cfw_read_id_u32, const void *, const void *, const void *,
    open_cfw_read_id_u32, const void *);

#if defined(OPEN_CFW_MSPI_READ_ID_HOST)
open_cfw_read_id_u32 open_cfw_read_id_host_command(
    open_cfw_read_id_u32, open_cfw_read_id_u8 *, open_cfw_read_id_u32);
void open_cfw_read_id_host_log(
    open_cfw_read_id_u32, open_cfw_read_id_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_read_id_u32
open_cfw_read_id_issue(open_cfw_read_id_u8 *bytes)
{
#if defined(OPEN_CFW_MSPI_READ_ID_HOST)
    return open_cfw_read_id_host_command(
        OPEN_CFW_READ_ID_COMMAND, bytes, OPEN_CFW_READ_ID_LENGTH);
#else
    return ((open_cfw_read_id_command_fn)(open_cfw_read_id_word)
        0x004205F5U)(OPEN_CFW_READ_ID_COMMAND, 0U, 0U, bytes,
            OPEN_CFW_READ_ID_LENGTH);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_read_id_log(void)
{
#if defined(OPEN_CFW_MSPI_READ_ID_HOST)
    open_cfw_read_id_host_log(
        OPEN_CFW_READ_ID_FAIL_LINE, OPEN_CFW_READ_ID_FAIL_FORMAT);
#else
    ((open_cfw_read_id_log_fn)(open_cfw_read_id_word)
        OPEN_CFW_READ_ID_LOG_THUMB)(1U,
            (const void *)(open_cfw_read_id_word)OPEN_CFW_READ_ID_LOG_TAG,
            (const void *)(open_cfw_read_id_word)OPEN_CFW_READ_ID_LOG_FILE,
            (const void *)(open_cfw_read_id_word)OPEN_CFW_READ_ID_LOG_FUNCTION,
            OPEN_CFW_READ_ID_FAIL_LINE,
            (const void *)(open_cfw_read_id_word)OPEN_CFW_READ_ID_FAIL_FORMAT);
#endif
}

__attribute__((used, noinline))
open_cfw_read_id_u32 open_cfw_bootloader_mspi_read_id_42059e(
    open_cfw_read_id_u32 *identifier)
{
    open_cfw_read_id_u8 bytes[OPEN_CFW_READ_ID_LENGTH];
    const open_cfw_read_id_u32 status = open_cfw_read_id_issue(bytes);

    if (status != 0U) {
        open_cfw_read_id_log();
        return status;
    }
    *identifier = ((open_cfw_read_id_u32)bytes[0] << 16) |
        ((open_cfw_read_id_u32)bytes[1] << 8) |
        (open_cfw_read_id_u32)bytes[2];
    return 0U;
}
