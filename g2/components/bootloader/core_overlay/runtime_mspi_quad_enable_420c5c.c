/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G QE-bit service. */

typedef __UINT8_TYPE__ open_cfw_quad_u8;
typedef __UINT32_TYPE__ open_cfw_quad_u32;
typedef __UINTPTR_TYPE__ open_cfw_quad_word;

enum {
    OPEN_CFW_QUAD_READ_STATUS_2_COMMAND = 0x05U,
    OPEN_CFW_QUAD_WRITE_STATUS_2_COMMAND = 0x01U,
    OPEN_CFW_QUAD_QE_BIT = 0x40U,
    OPEN_CFW_QUAD_PROTECTION_BITS = 0x3CU,
    OPEN_CFW_QUAD_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_QUAD_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_QUAD_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_QUAD_LOG_FILE = 0x00431540U,
    OPEN_CFW_QUAD_LOG_FUNCTION = 0x00433844U,
    OPEN_CFW_QUAD_READ_FAIL_FORMAT = 0x00432D78U,
    OPEN_CFW_QUAD_UNCHANGED_FORMAT = 0x00432D9CU,
    OPEN_CFW_QUAD_ENABLE_FAIL_FORMAT = 0x00432A9CU,
    OPEN_CFW_QUAD_WRITE_FAIL_FORMAT = 0x00432DC0U,
    OPEN_CFW_QUAD_VERIFY_READ_FAIL_FORMAT = 0x0043355CU,
    OPEN_CFW_QUAD_VERIFY_FAIL_FORMAT = 0x0043385CU,
    OPEN_CFW_QUAD_SET_TEXT = 0x00420F6CU,
    OPEN_CFW_QUAD_CLEAR_TEXT = 0x00434034U,
    OPEN_CFW_QUAD_READ_FAIL_LINE = 0x521U,
    OPEN_CFW_QUAD_UNCHANGED_LINE = 0x52AU,
    OPEN_CFW_QUAD_ENABLE_FAIL_LINE = 0x531U,
    OPEN_CFW_QUAD_WRITE_FAIL_LINE = 0x540U,
    OPEN_CFW_QUAD_VERIFY_READ_FAIL_LINE = 0x54AU,
    OPEN_CFW_QUAD_VERIFY_FAIL_LINE = 0x550U
};

typedef open_cfw_quad_u32 (*open_cfw_quad_call_fn)(void);
typedef open_cfw_quad_u32 (*open_cfw_quad_read_fn)(open_cfw_quad_u32,
    open_cfw_quad_u32, open_cfw_quad_u32, open_cfw_quad_u8 *,
    open_cfw_quad_u32);
typedef open_cfw_quad_u32 (*open_cfw_quad_write_fn)(open_cfw_quad_u32,
    open_cfw_quad_u32, open_cfw_quad_u32, const open_cfw_quad_u8 *,
    open_cfw_quad_u32);
typedef void (*open_cfw_quad_log_fn)(open_cfw_quad_u32, const void *,
    const void *, const void *, open_cfw_quad_u32, const void *, ...);

#if defined(OPEN_CFW_MSPI_QUAD_ENABLE_HOST)
open_cfw_quad_word open_cfw_quad_host_handle(void);
open_cfw_quad_u32 open_cfw_quad_host_wait(void);
open_cfw_quad_u32 open_cfw_quad_host_read(open_cfw_quad_u32,
    open_cfw_quad_u8 *, open_cfw_quad_u32);
open_cfw_quad_u32 open_cfw_quad_host_enable(void);
open_cfw_quad_u32 open_cfw_quad_host_write(open_cfw_quad_u32,
    const open_cfw_quad_u8 *, open_cfw_quad_u32);
void open_cfw_quad_host_log(open_cfw_quad_u32, open_cfw_quad_u32,
    open_cfw_quad_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_quad_word
open_cfw_quad_handle(void)
{
#if defined(OPEN_CFW_MSPI_QUAD_ENABLE_HOST)
    return open_cfw_quad_host_handle();
#else
    return *(const volatile open_cfw_quad_u32 *)(open_cfw_quad_word)
        OPEN_CFW_QUAD_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_quad_u32
open_cfw_quad_wait(void)
{
#if defined(OPEN_CFW_MSPI_QUAD_ENABLE_HOST)
    return open_cfw_quad_host_wait();
#else
    return ((open_cfw_quad_call_fn)(open_cfw_quad_word)0x004207F5U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_quad_u32
open_cfw_quad_read(open_cfw_quad_u8 *value)
{
#if defined(OPEN_CFW_MSPI_QUAD_ENABLE_HOST)
    return open_cfw_quad_host_read(OPEN_CFW_QUAD_READ_STATUS_2_COMMAND,
        value, 1U);
#else
    return ((open_cfw_quad_read_fn)(open_cfw_quad_word)0x004205F5U)(
        OPEN_CFW_QUAD_READ_STATUS_2_COMMAND, 0U, 0U, value, 1U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_quad_u32
open_cfw_quad_enable_write(void)
{
#if defined(OPEN_CFW_MSPI_QUAD_ENABLE_HOST)
    return open_cfw_quad_host_enable();
#else
    return ((open_cfw_quad_call_fn)(open_cfw_quad_word)0x00420985U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_quad_u32
open_cfw_quad_write(const open_cfw_quad_u8 *value)
{
#if defined(OPEN_CFW_MSPI_QUAD_ENABLE_HOST)
    return open_cfw_quad_host_write(OPEN_CFW_QUAD_WRITE_STATUS_2_COMMAND,
        value, 1U);
#else
    return ((open_cfw_quad_write_fn)(open_cfw_quad_word)0x0042069FU)(
        OPEN_CFW_QUAD_WRITE_STATUS_2_COMMAND, 0U, 0U, value, 1U);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_quad_log(
    open_cfw_quad_u32 line, open_cfw_quad_u32 format,
    open_cfw_quad_u32 operation)
{
#if defined(OPEN_CFW_MSPI_QUAD_ENABLE_HOST)
    open_cfw_quad_host_log(line, format, operation);
#else
    const void *text = operation == 1U
        ? (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_SET_TEXT
        : (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_CLEAR_TEXT;
    ((open_cfw_quad_log_fn)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_THUMB)(2U,
        (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_TAG,
        (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_FILE,
        (const void *)(open_cfw_quad_word)OPEN_CFW_QUAD_LOG_FUNCTION,
        line, (const void *)(open_cfw_quad_word)format, text);
#endif
}

__attribute__((used, noinline))
open_cfw_quad_u32 open_cfw_bootloader_mspi_quad_enable_420c5c(
    open_cfw_quad_u32 requested_state)
{
    open_cfw_quad_u8 status_register;
    open_cfw_quad_u8 desired = (open_cfw_quad_u8)requested_state;
    open_cfw_quad_u32 status;

    if (open_cfw_quad_handle() == 0U) {
        return 2U;
    }

    /* The authenticated body deliberately ignores both readiness results. */
    (void)open_cfw_quad_wait();
    status = open_cfw_quad_read(&status_register);
    if (status != 0U) {
        open_cfw_quad_log(OPEN_CFW_QUAD_READ_FAIL_LINE,
            OPEN_CFW_QUAD_READ_FAIL_FORMAT, 0U);
        return status;
    }

    if (((open_cfw_quad_u8)((status_register >> 6) & 1U) == desired) &&
        ((status_register & OPEN_CFW_QUAD_PROTECTION_BITS) == 0U)) {
        open_cfw_quad_log(OPEN_CFW_QUAD_UNCHANGED_LINE,
            OPEN_CFW_QUAD_UNCHANGED_FORMAT, 0U);
        return 0U;
    }

    status = open_cfw_quad_enable_write();
    if (status != 0U) {
        open_cfw_quad_log(OPEN_CFW_QUAD_ENABLE_FAIL_LINE,
            OPEN_CFW_QUAD_ENABLE_FAIL_FORMAT, 0U);
        return status;
    }

    if (desired != 0U) {
        status_register |= OPEN_CFW_QUAD_QE_BIT;
    } else {
        status_register &= (open_cfw_quad_u8)~OPEN_CFW_QUAD_QE_BIT;
    }
    status_register &= (open_cfw_quad_u8)~OPEN_CFW_QUAD_PROTECTION_BITS;

    status = open_cfw_quad_write(&status_register);
    if (status != 0U) {
        open_cfw_quad_log(OPEN_CFW_QUAD_WRITE_FAIL_LINE,
            OPEN_CFW_QUAD_WRITE_FAIL_FORMAT, 0U);
        return status;
    }

    (void)open_cfw_quad_wait();
    status = open_cfw_quad_read(&status_register);
    if (status != 0U) {
        open_cfw_quad_log(OPEN_CFW_QUAD_VERIFY_READ_FAIL_LINE,
            OPEN_CFW_QUAD_VERIFY_READ_FAIL_FORMAT, 0U);
        return status;
    }
    if ((open_cfw_quad_u8)((status_register >> 6) & 1U) != desired) {
        open_cfw_quad_log(OPEN_CFW_QUAD_VERIFY_FAIL_LINE,
            OPEN_CFW_QUAD_VERIFY_FAIL_FORMAT, desired != 0U ? 1U : 2U);
        return 1U;
    }
    return 0U;
}
