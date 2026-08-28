/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G four-byte-mode entry. */

typedef __UINT8_TYPE__ open_cfw_enter_4byte_u8;
typedef __UINT32_TYPE__ open_cfw_enter_4byte_u32;
typedef __UINTPTR_TYPE__ open_cfw_enter_4byte_word;

enum {
    OPEN_CFW_ENTER_4BYTE_COMMAND = 0xB7U,
    OPEN_CFW_ENTER_4BYTE_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_ENTER_4BYTE_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_ENTER_4BYTE_LOG_FILE = 0x00431540U,
    OPEN_CFW_ENTER_4BYTE_LOG_FUNCTION = 0x004331C0U,
    OPEN_CFW_ENTER_4BYTE_BUSY_FORMAT = 0x00433CE8U,
    OPEN_CFW_ENTER_4BYTE_BUSY_LINE = 0x3C8U,
    OPEN_CFW_ENTER_4BYTE_ENABLE_FORMAT = 0x00431ED8U,
    OPEN_CFW_ENTER_4BYTE_ENABLE_LINE = 0x3CFU,
    OPEN_CFW_ENTER_4BYTE_COMMAND_FORMAT = 0x004331E0U,
    OPEN_CFW_ENTER_4BYTE_COMMAND_LINE = 0x3D6U,
    OPEN_CFW_ENTER_4BYTE_VERIFY_FORMAT = 0x00433200U,
    OPEN_CFW_ENTER_4BYTE_VERIFY_LINE = 0x3DEU,
    OPEN_CFW_ENTER_4BYTE_DISABLE_FORMAT = 0x0043382CU,
    OPEN_CFW_ENTER_4BYTE_DISABLE_LINE = 0x3E4U
};

typedef open_cfw_enter_4byte_u32 (*open_cfw_enter_4byte_call_fn)(void);
typedef open_cfw_enter_4byte_u32 (*open_cfw_enter_4byte_write_fn)(
    open_cfw_enter_4byte_u32, open_cfw_enter_4byte_u32,
    open_cfw_enter_4byte_u32, const open_cfw_enter_4byte_u8 *,
    open_cfw_enter_4byte_u32);
typedef void (*open_cfw_enter_4byte_log_fn)(
    open_cfw_enter_4byte_u32, const void *, const void *, const void *,
    open_cfw_enter_4byte_u32, const void *);

#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_available(void);
open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_wait_ready(void);
open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_write_enable(void);
open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_write(
    open_cfw_enter_4byte_u32, open_cfw_enter_4byte_u32,
    open_cfw_enter_4byte_u32, const open_cfw_enter_4byte_u8 *,
    open_cfw_enter_4byte_u32);
open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_is_4byte(void);
open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_write_disable(void);
void open_cfw_enter_4byte_host_log(
    open_cfw_enter_4byte_u32, open_cfw_enter_4byte_u32,
    open_cfw_enter_4byte_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_enter_4byte_u32
open_cfw_enter_4byte_available(void)
{
#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
    return open_cfw_enter_4byte_host_available();
#else
    return *(const volatile open_cfw_enter_4byte_u32 *)(open_cfw_enter_4byte_word)
        0x200270DCU != 0U;
#endif
}

static __attribute__((always_inline)) inline open_cfw_enter_4byte_u32
open_cfw_enter_4byte_wait_ready(void)
{
#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
    return open_cfw_enter_4byte_host_wait_ready();
#else
    return ((open_cfw_enter_4byte_call_fn)(open_cfw_enter_4byte_word)
        0x004207F5U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_enter_4byte_u32
open_cfw_enter_4byte_write_enable(void)
{
#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
    return open_cfw_enter_4byte_host_write_enable();
#else
    return ((open_cfw_enter_4byte_call_fn)(open_cfw_enter_4byte_word)
        0x00420985U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_enter_4byte_u32
open_cfw_enter_4byte_write_command(void)
{
#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
    return open_cfw_enter_4byte_host_write(
        OPEN_CFW_ENTER_4BYTE_COMMAND, 0U, 0U, (const open_cfw_enter_4byte_u8 *)0,
        0U);
#else
    return ((open_cfw_enter_4byte_write_fn)(open_cfw_enter_4byte_word)
        0x0042069FU)(OPEN_CFW_ENTER_4BYTE_COMMAND, 0U, 0U,
            (const open_cfw_enter_4byte_u8 *)0, 0U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_enter_4byte_u32
open_cfw_enter_4byte_is_4byte(void)
{
#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
    return open_cfw_enter_4byte_host_is_4byte();
#else
    return ((open_cfw_enter_4byte_call_fn)(open_cfw_enter_4byte_word)
        0x00420801U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_enter_4byte_u32
open_cfw_enter_4byte_write_disable(void)
{
#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
    return open_cfw_enter_4byte_host_write_disable();
#else
    return ((open_cfw_enter_4byte_call_fn)(open_cfw_enter_4byte_word)
        0x004209C5U)();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_enter_4byte_log(
    open_cfw_enter_4byte_u32 line, open_cfw_enter_4byte_u32 format)
{
#if defined(OPEN_CFW_MSPI_ENTER_4BYTE_HOST)
    open_cfw_enter_4byte_host_log(
        line, format, OPEN_CFW_ENTER_4BYTE_LOG_FUNCTION);
#else
    ((open_cfw_enter_4byte_log_fn)(open_cfw_enter_4byte_word)
        OPEN_CFW_ENTER_4BYTE_LOG_THUMB)(2U,
            (const void *)(open_cfw_enter_4byte_word)OPEN_CFW_ENTER_4BYTE_LOG_TAG,
            (const void *)(open_cfw_enter_4byte_word)OPEN_CFW_ENTER_4BYTE_LOG_FILE,
            (const void *)(open_cfw_enter_4byte_word)
                OPEN_CFW_ENTER_4BYTE_LOG_FUNCTION,
            line, (const void *)(open_cfw_enter_4byte_word)format);
#endif
}

__attribute__((used, noinline))
open_cfw_enter_4byte_u32 open_cfw_bootloader_mspi_enter_4byte_mode_420890(void)
{
    open_cfw_enter_4byte_u32 status;

    if (open_cfw_enter_4byte_available() == 0U) {
        return 2U;
    }
    if (open_cfw_enter_4byte_wait_ready() != 0U) {
        open_cfw_enter_4byte_log(
            OPEN_CFW_ENTER_4BYTE_BUSY_LINE, OPEN_CFW_ENTER_4BYTE_BUSY_FORMAT);
        return 3U;
    }
    status = open_cfw_enter_4byte_write_enable();
    if (status != 0U) {
        open_cfw_enter_4byte_log(
            OPEN_CFW_ENTER_4BYTE_ENABLE_LINE, OPEN_CFW_ENTER_4BYTE_ENABLE_FORMAT);
        return status;
    }
    status = open_cfw_enter_4byte_write_command();
    if (status != 0U) {
        open_cfw_enter_4byte_log(
            OPEN_CFW_ENTER_4BYTE_COMMAND_LINE, OPEN_CFW_ENTER_4BYTE_COMMAND_FORMAT);
        return status;
    }
    (void)open_cfw_enter_4byte_wait_ready();
    if (open_cfw_enter_4byte_is_4byte() == 0U) {
        open_cfw_enter_4byte_log(
            OPEN_CFW_ENTER_4BYTE_VERIFY_LINE, OPEN_CFW_ENTER_4BYTE_VERIFY_FORMAT);
        return 1U;
    }
    status = open_cfw_enter_4byte_write_disable();
    if (status != 0U) {
        open_cfw_enter_4byte_log(
            OPEN_CFW_ENTER_4BYTE_DISABLE_LINE,
            OPEN_CFW_ENTER_4BYTE_DISABLE_FORMAT);
        return status;
    }
    return 0U;
}
