/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G address-mode reader. */

typedef __UINT8_TYPE__ open_cfw_4byte_mode_u8;
typedef __UINT32_TYPE__ open_cfw_4byte_mode_u32;
typedef __UINTPTR_TYPE__ open_cfw_4byte_mode_word;

enum {
    OPEN_CFW_4BYTE_MODE_COMMAND = 0x15U,
    OPEN_CFW_4BYTE_MODE_LENGTH = 1U,
    OPEN_CFW_4BYTE_MODE_BIT = 0x20U,
    OPEN_CFW_4BYTE_MODE_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_4BYTE_MODE_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_4BYTE_MODE_LOG_FILE = 0x00431540U,
    OPEN_CFW_4BYTE_MODE_LOG_FUNCTION = 0x00433524U,
    OPEN_CFW_4BYTE_MODE_READ_FAIL_FORMAT = 0x00433814U,
    OPEN_CFW_4BYTE_MODE_READ_FAIL_LINE = 0x3B0U,
    OPEN_CFW_4BYTE_MODE_THREE_BYTE_FORMAT = 0x00432D0CU,
    OPEN_CFW_4BYTE_MODE_THREE_BYTE_LINE = 0x3B8U
};

typedef open_cfw_4byte_mode_u32 (*open_cfw_4byte_mode_read_fn)(
    open_cfw_4byte_mode_u32, open_cfw_4byte_mode_u32,
    open_cfw_4byte_mode_u32, open_cfw_4byte_mode_u8 *,
    open_cfw_4byte_mode_u32);
typedef void (*open_cfw_4byte_mode_log_fn)(
    open_cfw_4byte_mode_u32, const void *, const void *, const void *,
    open_cfw_4byte_mode_u32, const void *);

#if defined(OPEN_CFW_MSPI_4BYTE_MODE_HOST)
open_cfw_4byte_mode_u32 open_cfw_4byte_mode_host_read(
    open_cfw_4byte_mode_u32, open_cfw_4byte_mode_u8 *,
    open_cfw_4byte_mode_u32);
void open_cfw_4byte_mode_host_log(
    open_cfw_4byte_mode_u32, open_cfw_4byte_mode_u32,
    open_cfw_4byte_mode_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_4byte_mode_u32
open_cfw_4byte_mode_read(open_cfw_4byte_mode_u8 *bytes)
{
#if defined(OPEN_CFW_MSPI_4BYTE_MODE_HOST)
    return open_cfw_4byte_mode_host_read(
        OPEN_CFW_4BYTE_MODE_COMMAND, bytes, OPEN_CFW_4BYTE_MODE_LENGTH);
#else
    return ((open_cfw_4byte_mode_read_fn)(open_cfw_4byte_mode_word)
        0x004205F5U)(OPEN_CFW_4BYTE_MODE_COMMAND, 0U, 0U, bytes,
            OPEN_CFW_4BYTE_MODE_LENGTH);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_4byte_mode_log(
    open_cfw_4byte_mode_u32 line, open_cfw_4byte_mode_u32 format)
{
#if defined(OPEN_CFW_MSPI_4BYTE_MODE_HOST)
    open_cfw_4byte_mode_host_log(
        line, format, OPEN_CFW_4BYTE_MODE_LOG_FUNCTION);
#else
    ((open_cfw_4byte_mode_log_fn)(open_cfw_4byte_mode_word)
        OPEN_CFW_4BYTE_MODE_LOG_THUMB)(2U,
            (const void *)(open_cfw_4byte_mode_word)OPEN_CFW_4BYTE_MODE_LOG_TAG,
            (const void *)(open_cfw_4byte_mode_word)OPEN_CFW_4BYTE_MODE_LOG_FILE,
            (const void *)(open_cfw_4byte_mode_word)
                OPEN_CFW_4BYTE_MODE_LOG_FUNCTION,
            line, (const void *)(open_cfw_4byte_mode_word)format);
#endif
}

__attribute__((used, noinline))
open_cfw_4byte_mode_u32 open_cfw_bootloader_mspi_4byte_mode_420800(void)
{
    open_cfw_4byte_mode_u8 bytes[5] = {0U, 0U, 0U, 0U, 0U};
    const open_cfw_4byte_mode_u32 status = open_cfw_4byte_mode_read(bytes);

    if (status != 0U) {
        open_cfw_4byte_mode_log(OPEN_CFW_4BYTE_MODE_READ_FAIL_LINE,
            OPEN_CFW_4BYTE_MODE_READ_FAIL_FORMAT);
        return status;
    }
    if ((bytes[0] & OPEN_CFW_4BYTE_MODE_BIT) != 0U) {
        return 1U;
    }
    open_cfw_4byte_mode_log(OPEN_CFW_4BYTE_MODE_THREE_BYTE_LINE,
        OPEN_CFW_4BYTE_MODE_THREE_BYTE_FORMAT);
    return 0U;
}
