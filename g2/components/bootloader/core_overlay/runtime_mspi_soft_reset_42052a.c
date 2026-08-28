/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the bounded G2 MX25U25643G soft reset. */

typedef __UINT32_TYPE__ open_cfw_soft_reset_u32;
typedef __UINTPTR_TYPE__ open_cfw_soft_reset_word;

enum {
    OPEN_CFW_SOFT_RESET_ENABLE_COMMAND = 0x66U,
    OPEN_CFW_SOFT_RESET_COMMAND = 0x99U,
    OPEN_CFW_SOFT_RESET_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_SOFT_RESET_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_SOFT_RESET_LOG_FILE = 0x00431540U,
    OPEN_CFW_SOFT_RESET_LOG_FUNCTION = 0x004334D0U,
    OPEN_CFW_SOFT_RESET_ENABLE_FORMAT = 0x004334ECU,
    OPEN_CFW_SOFT_RESET_FORMAT = 0x00432650U,
    OPEN_CFW_SOFT_RESET_ENABLE_LINE = 0x2C4U,
    OPEN_CFW_SOFT_RESET_LINE = 0x2C9U
};

typedef open_cfw_soft_reset_u32 (*open_cfw_soft_reset_command_fn)(
    open_cfw_soft_reset_u32, open_cfw_soft_reset_u32,
    open_cfw_soft_reset_u32, open_cfw_soft_reset_u32,
    open_cfw_soft_reset_u32);
typedef void (*open_cfw_soft_reset_log_fn)(
    open_cfw_soft_reset_u32, const void *, const void *, const void *,
    open_cfw_soft_reset_u32, const void *);

void open_cfw_bootloader_delay_milliseconds_41f9d8(open_cfw_soft_reset_u32);

#if defined(OPEN_CFW_MSPI_SOFT_RESET_HOST)
open_cfw_soft_reset_u32 open_cfw_soft_reset_host_command(
    open_cfw_soft_reset_u32);
void open_cfw_soft_reset_host_delay(open_cfw_soft_reset_u32);
void open_cfw_soft_reset_host_log(
    open_cfw_soft_reset_u32, open_cfw_soft_reset_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_soft_reset_u32
open_cfw_soft_reset_issue(open_cfw_soft_reset_u32 command)
{
#if defined(OPEN_CFW_MSPI_SOFT_RESET_HOST)
    return open_cfw_soft_reset_host_command(command);
#else
    return ((open_cfw_soft_reset_command_fn)(open_cfw_soft_reset_word)
        0x0042069FU)(command, 0U, 0U, 0U, 0U);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_soft_reset_delay(
    open_cfw_soft_reset_u32 duration)
{
#if defined(OPEN_CFW_MSPI_SOFT_RESET_HOST)
    open_cfw_soft_reset_host_delay(duration);
#else
    open_cfw_bootloader_delay_milliseconds_41f9d8(duration);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_soft_reset_log(
    open_cfw_soft_reset_u32 line, open_cfw_soft_reset_u32 format)
{
#if defined(OPEN_CFW_MSPI_SOFT_RESET_HOST)
    open_cfw_soft_reset_host_log(line, format);
#else
    ((open_cfw_soft_reset_log_fn)(open_cfw_soft_reset_word)
        OPEN_CFW_SOFT_RESET_LOG_THUMB)(1U,
            (const void *)(open_cfw_soft_reset_word)OPEN_CFW_SOFT_RESET_LOG_TAG,
            (const void *)(open_cfw_soft_reset_word)OPEN_CFW_SOFT_RESET_LOG_FILE,
            (const void *)(open_cfw_soft_reset_word)
                OPEN_CFW_SOFT_RESET_LOG_FUNCTION,
            line, (const void *)(open_cfw_soft_reset_word)format);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_soft_reset_42052a(void)
{
    if (open_cfw_soft_reset_issue(OPEN_CFW_SOFT_RESET_ENABLE_COMMAND) != 0U) {
        open_cfw_soft_reset_log(
            OPEN_CFW_SOFT_RESET_ENABLE_LINE, OPEN_CFW_SOFT_RESET_ENABLE_FORMAT);
    }
    open_cfw_soft_reset_delay(1U);
    if (open_cfw_soft_reset_issue(OPEN_CFW_SOFT_RESET_COMMAND) != 0U) {
        open_cfw_soft_reset_log(
            OPEN_CFW_SOFT_RESET_LINE, OPEN_CFW_SOFT_RESET_FORMAT);
    }
    open_cfw_soft_reset_delay(50U);
}
