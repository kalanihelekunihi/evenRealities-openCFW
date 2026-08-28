/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G busy-status reader. */

typedef __UINT8_TYPE__ open_cfw_busy_status_u8;
typedef __UINT32_TYPE__ open_cfw_busy_status_u32;
typedef __UINTPTR_TYPE__ open_cfw_busy_status_word;

enum {
    OPEN_CFW_BUSY_STATUS_COMMAND = 0x05U,
    OPEN_CFW_BUSY_STATUS_LENGTH = 1U,
    OPEN_CFW_BUSY_STATUS_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_BUSY_STATUS_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_BUSY_STATUS_LOG_FILE = 0x00431540U,
    OPEN_CFW_BUSY_STATUS_LOG_FUNCTION = 0x00433B00U,
    OPEN_CFW_BUSY_STATUS_FAIL_FORMAT = 0x00433508U,
    OPEN_CFW_BUSY_STATUS_FAIL_LINE = 0x376U
};

typedef open_cfw_busy_status_u32 (*open_cfw_busy_status_read_fn)(
    open_cfw_busy_status_u32, open_cfw_busy_status_u32,
    open_cfw_busy_status_u32, open_cfw_busy_status_u8 *,
    open_cfw_busy_status_u32);
typedef void (*open_cfw_busy_status_log_fn)(
    open_cfw_busy_status_u32, const void *, const void *, const void *,
    open_cfw_busy_status_u32, const void *);

#if defined(OPEN_CFW_MSPI_BUSY_STATUS_HOST)
open_cfw_busy_status_u32 open_cfw_busy_status_host_read(
    open_cfw_busy_status_u32, open_cfw_busy_status_u8 *,
    open_cfw_busy_status_u32);
void open_cfw_busy_status_host_log(
    open_cfw_busy_status_u32, open_cfw_busy_status_u32,
    open_cfw_busy_status_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_busy_status_u32
open_cfw_busy_status_read(open_cfw_busy_status_u8 *bytes)
{
#if defined(OPEN_CFW_MSPI_BUSY_STATUS_HOST)
    return open_cfw_busy_status_host_read(
        OPEN_CFW_BUSY_STATUS_COMMAND, bytes,
        OPEN_CFW_BUSY_STATUS_LENGTH);
#else
    return ((open_cfw_busy_status_read_fn)(open_cfw_busy_status_word)
        0x004205F5U)(OPEN_CFW_BUSY_STATUS_COMMAND, 0U, 0U, bytes,
            OPEN_CFW_BUSY_STATUS_LENGTH);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_busy_status_log(void)
{
#if defined(OPEN_CFW_MSPI_BUSY_STATUS_HOST)
    open_cfw_busy_status_host_log(
        OPEN_CFW_BUSY_STATUS_FAIL_LINE,
        OPEN_CFW_BUSY_STATUS_FAIL_FORMAT,
        OPEN_CFW_BUSY_STATUS_LOG_FUNCTION);
#else
    ((open_cfw_busy_status_log_fn)(open_cfw_busy_status_word)
        OPEN_CFW_BUSY_STATUS_LOG_THUMB)(2U,
            (const void *)(open_cfw_busy_status_word)
                OPEN_CFW_BUSY_STATUS_LOG_TAG,
            (const void *)(open_cfw_busy_status_word)
                OPEN_CFW_BUSY_STATUS_LOG_FILE,
            (const void *)(open_cfw_busy_status_word)
                OPEN_CFW_BUSY_STATUS_LOG_FUNCTION,
            OPEN_CFW_BUSY_STATUS_FAIL_LINE,
            (const void *)(open_cfw_busy_status_word)
                OPEN_CFW_BUSY_STATUS_FAIL_FORMAT);
#endif
}

__attribute__((used, noinline))
open_cfw_busy_status_u32 open_cfw_bootloader_mspi_busy_status_42074e(void)
{
    open_cfw_busy_status_u8 bytes[5] = {0U, 0U, 0U, 0U, 0U};
    const open_cfw_busy_status_u32 status = open_cfw_busy_status_read(bytes);

    if (status != 0U) {
        open_cfw_busy_status_log();
        return status;
    }
    return (open_cfw_busy_status_u32)((bytes[0] >> 7) & 1U);
}
