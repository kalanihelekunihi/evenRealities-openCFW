/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G write-latch commands. */

typedef __UINT8_TYPE__ open_cfw_write_latch_u8;
typedef __UINT32_TYPE__ open_cfw_write_latch_u32;
typedef __UINTPTR_TYPE__ open_cfw_write_latch_word;

enum {
    OPEN_CFW_WRITE_ENABLE_COMMAND = 0x06U,
    OPEN_CFW_WRITE_DISABLE_COMMAND = 0x04U,
    OPEN_CFW_WRITE_LATCH_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_WRITE_LATCH_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_WRITE_LATCH_LOG_FILE = 0x00431540U,
    OPEN_CFW_WRITE_LATCH_LOG_FORMAT = 0x00432650U,
    OPEN_CFW_WRITE_ENABLE_LOG_FUNCTION = 0x00433220U,
    OPEN_CFW_WRITE_DISABLE_LOG_FUNCTION = 0x00432D30U,
    OPEN_CFW_WRITE_ENABLE_LOG_LINE = 0x3F2U,
    OPEN_CFW_WRITE_DISABLE_LOG_LINE = 0x3FEU
};

typedef open_cfw_write_latch_u32 (*open_cfw_write_latch_transfer_fn)(
    open_cfw_write_latch_u32, open_cfw_write_latch_u32,
    open_cfw_write_latch_u32, const open_cfw_write_latch_u8 *,
    open_cfw_write_latch_u32);
typedef void (*open_cfw_write_latch_log_fn)(
    open_cfw_write_latch_u32, const void *, const void *, const void *,
    open_cfw_write_latch_u32, const void *);

#if defined(OPEN_CFW_MSPI_WRITE_LATCH_HOST)
open_cfw_write_latch_u32 open_cfw_write_latch_host_transfer(
    open_cfw_write_latch_u32, open_cfw_write_latch_u32,
    open_cfw_write_latch_u32, const open_cfw_write_latch_u8 *,
    open_cfw_write_latch_u32);
void open_cfw_write_latch_host_log(
    open_cfw_write_latch_u32, open_cfw_write_latch_u32,
    open_cfw_write_latch_u32, open_cfw_write_latch_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_write_latch_u32
open_cfw_write_latch_transfer(open_cfw_write_latch_u32 command)
{
#if defined(OPEN_CFW_MSPI_WRITE_LATCH_HOST)
    return open_cfw_write_latch_host_transfer(
        command, 0U, 0U, (const open_cfw_write_latch_u8 *)0, 0U);
#else
    return ((open_cfw_write_latch_transfer_fn)(open_cfw_write_latch_word)
        0x0042069FU)(command, 0U, 0U,
            (const open_cfw_write_latch_u8 *)0, 0U);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_write_latch_log(
    open_cfw_write_latch_u32 level, open_cfw_write_latch_u32 line,
    open_cfw_write_latch_u32 function)
{
#if defined(OPEN_CFW_MSPI_WRITE_LATCH_HOST)
    open_cfw_write_latch_host_log(
        level, line, OPEN_CFW_WRITE_LATCH_LOG_FORMAT, function);
#else
    ((open_cfw_write_latch_log_fn)(open_cfw_write_latch_word)
        OPEN_CFW_WRITE_LATCH_LOG_THUMB)(level,
            (const void *)(open_cfw_write_latch_word)
                OPEN_CFW_WRITE_LATCH_LOG_TAG,
            (const void *)(open_cfw_write_latch_word)
                OPEN_CFW_WRITE_LATCH_LOG_FILE,
            (const void *)(open_cfw_write_latch_word)function,
            line,
            (const void *)(open_cfw_write_latch_word)
                OPEN_CFW_WRITE_LATCH_LOG_FORMAT);
#endif
}

__attribute__((used, noinline))
open_cfw_write_latch_u32 open_cfw_bootloader_mspi_write_enable_420984(void)
{
    open_cfw_write_latch_u32 status =
        open_cfw_write_latch_transfer(OPEN_CFW_WRITE_ENABLE_COMMAND);
    if (status != 0U) {
        open_cfw_write_latch_log(1U, OPEN_CFW_WRITE_ENABLE_LOG_LINE,
            OPEN_CFW_WRITE_ENABLE_LOG_FUNCTION);
    }
    return status;
}

__attribute__((used, noinline))
open_cfw_write_latch_u32 open_cfw_bootloader_mspi_write_disable_4209c4(void)
{
    open_cfw_write_latch_u32 status =
        open_cfw_write_latch_transfer(OPEN_CFW_WRITE_DISABLE_COMMAND);
    if (status != 0U) {
        open_cfw_write_latch_log(2U, OPEN_CFW_WRITE_DISABLE_LOG_LINE,
            OPEN_CFW_WRITE_DISABLE_LOG_FUNCTION);
    }
    return status;
}
