/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G page-program service. */

typedef __UINT8_TYPE__ open_cfw_program_u8;
typedef __UINT32_TYPE__ open_cfw_program_u32;
typedef __UINTPTR_TYPE__ open_cfw_program_word;

enum {
    OPEN_CFW_PROGRAM_COMMAND = 0x02U,
    OPEN_CFW_PROGRAM_PAGE_SIZE = 0x100U,
    OPEN_CFW_PROGRAM_LIMIT = 0x02000000U,
    OPEN_CFW_PROGRAM_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_PROGRAM_PRINTF_THUMB = 0x00415FAFU,
    OPEN_CFW_PROGRAM_INVALID_FORMAT = 0x004326A8U,
    OPEN_CFW_PROGRAM_RANGE_FORMAT = 0x004326D4U,
    OPEN_CFW_PROGRAM_PREWAIT_FORMAT = 0x00431AF0U,
    OPEN_CFW_PROGRAM_ENABLE_FORMAT = 0x00431F0CU,
    OPEN_CFW_PROGRAM_TRANSFER_FORMAT = 0x00432208U,
    OPEN_CFW_PROGRAM_POSTWAIT_FORMAT = 0x00431B28U,
    OPEN_CFW_PROGRAM_DISABLE_FORMAT = 0x00431B60U
};

typedef open_cfw_program_u32 (*open_cfw_program_call_fn)(void);
typedef open_cfw_program_u32 (*open_cfw_program_wait_fn)(open_cfw_program_u32);
typedef open_cfw_program_u32 (*open_cfw_program_transfer_fn)(
    open_cfw_program_u32, open_cfw_program_u32, open_cfw_program_u32,
    const open_cfw_program_u8 *, open_cfw_program_u32);
typedef void (*open_cfw_program_printf2_fn)(const void *, open_cfw_program_u32,
    open_cfw_program_u32);
typedef void (*open_cfw_program_printf3_fn)(const void *, open_cfw_program_u32,
    open_cfw_program_word, open_cfw_program_u32);

#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
open_cfw_program_word open_cfw_program_host_handle(void);
void open_cfw_program_host_event(open_cfw_program_u32);
open_cfw_program_u32 open_cfw_program_host_wait_default(void);
open_cfw_program_u32 open_cfw_program_host_enable(void);
open_cfw_program_u32 open_cfw_program_host_transfer(open_cfw_program_u32,
    open_cfw_program_u32, open_cfw_program_u32,
    const open_cfw_program_u8 *, open_cfw_program_u32);
open_cfw_program_u32 open_cfw_program_host_wait(open_cfw_program_u32);
open_cfw_program_u32 open_cfw_program_host_disable(void);
void open_cfw_program_host_diag(open_cfw_program_u32, open_cfw_program_u32,
    open_cfw_program_word, open_cfw_program_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_program_word
open_cfw_program_handle(void)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    return open_cfw_program_host_handle();
#else
    return *(const volatile open_cfw_program_u32 *)(open_cfw_program_word)
        OPEN_CFW_PROGRAM_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void open_cfw_program_event(
    open_cfw_program_u32 event, open_cfw_program_word target)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    (void)target;
    open_cfw_program_host_event(event);
#else
    (void)event;
    ((void (*)(void))target)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_program_u32
open_cfw_program_wait_default(void)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    return open_cfw_program_host_wait_default();
#else
    return ((open_cfw_program_call_fn)(open_cfw_program_word)0x004207F5U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_program_u32
open_cfw_program_enable(void)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    return open_cfw_program_host_enable();
#else
    return ((open_cfw_program_call_fn)(open_cfw_program_word)0x00420985U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_program_u32
open_cfw_program_transfer(open_cfw_program_u32 address,
    const open_cfw_program_u8 *buffer, open_cfw_program_u32 length)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    return open_cfw_program_host_transfer(OPEN_CFW_PROGRAM_COMMAND, address,
        1U, buffer, length);
#else
    return ((open_cfw_program_transfer_fn)(open_cfw_program_word)
        0x0042069FU)(OPEN_CFW_PROGRAM_COMMAND, address, 1U, buffer, length);
#endif
}

static __attribute__((always_inline)) inline open_cfw_program_u32
open_cfw_program_wait(void)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    return open_cfw_program_host_wait(10U);
#else
    return ((open_cfw_program_wait_fn)(open_cfw_program_word)0x004207A3U)(10U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_program_u32
open_cfw_program_disable(void)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    return open_cfw_program_host_disable();
#else
    return ((open_cfw_program_call_fn)(open_cfw_program_word)0x004209C5U)();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_program_diag(
    open_cfw_program_u32 format, open_cfw_program_u32 first,
    open_cfw_program_word second, open_cfw_program_u32 third)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    open_cfw_program_host_diag(format, first, second, third);
#else
    ((open_cfw_program_printf3_fn)(open_cfw_program_word)
        OPEN_CFW_PROGRAM_PRINTF_THUMB)(
            (const void *)(open_cfw_program_word)format,
            first, second, third);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_program_diag2(
    open_cfw_program_u32 format, open_cfw_program_u32 first,
    open_cfw_program_u32 second)
{
#if defined(OPEN_CFW_MSPI_PROGRAM_HOST)
    open_cfw_program_host_diag(format, first,
        (open_cfw_program_word)second, 0U);
#else
    ((open_cfw_program_printf2_fn)(open_cfw_program_word)
        OPEN_CFW_PROGRAM_PRINTF_THUMB)(
            (const void *)(open_cfw_program_word)format, first, second);
#endif
}

__attribute__((used, noinline))
open_cfw_program_u32 open_cfw_bootloader_mspi_program_420b0c(
    open_cfw_program_u32 address, const open_cfw_program_u8 *buffer,
    open_cfw_program_u32 length)
{
    open_cfw_program_word handle = open_cfw_program_handle();
    open_cfw_program_u32 status = 0U;
    open_cfw_program_u32 page_offset;

    if (handle == 0U || buffer == (const open_cfw_program_u8 *)0 ||
        length == 0U) {
        open_cfw_program_diag(OPEN_CFW_PROGRAM_INVALID_FORMAT,
            (open_cfw_program_u32)handle, (open_cfw_program_word)buffer,
            length);
        return 6U;
    }
    if (address >= OPEN_CFW_PROGRAM_LIMIT) {
        open_cfw_program_diag2(OPEN_CFW_PROGRAM_RANGE_FORMAT, address,
            OPEN_CFW_PROGRAM_LIMIT);
        return 5U;
    }

    open_cfw_program_event(1U, 0x0041FF09U);
    open_cfw_program_event(2U, 0x00420F11U);
    page_offset = address & 0xFFU;

    while (length != 0U) {
        open_cfw_program_u32 chunk = OPEN_CFW_PROGRAM_PAGE_SIZE - page_offset;
        if (chunk >= length) {
            chunk = length;
        }

        if (open_cfw_program_wait_default() != 0U) {
            open_cfw_program_diag2(OPEN_CFW_PROGRAM_PREWAIT_FORMAT,
                address, chunk);
            status = 4U;
            break;
        }
        status = open_cfw_program_enable();
        if (status != 0U) {
            open_cfw_program_diag(OPEN_CFW_PROGRAM_ENABLE_FORMAT,
                address, (open_cfw_program_word)chunk, status);
            break;
        }
        status = open_cfw_program_transfer(address, buffer, chunk);
        if (status != 0U) {
            open_cfw_program_diag(OPEN_CFW_PROGRAM_TRANSFER_FORMAT,
                address, (open_cfw_program_word)chunk, status);
            break;
        }
        if (open_cfw_program_wait() != 0U) {
            open_cfw_program_diag2(OPEN_CFW_PROGRAM_POSTWAIT_FORMAT,
                address, chunk);
            status = 4U;
            break;
        }
        status = open_cfw_program_disable();
        if (status != 0U) {
            open_cfw_program_diag(OPEN_CFW_PROGRAM_DISABLE_FORMAT,
                address, (open_cfw_program_word)chunk, status);
            break;
        }

        address += chunk;
        buffer += chunk;
        length -= chunk;
        page_offset = 0U;
    }

    open_cfw_program_event(3U, 0x00420E8DU);
    open_cfw_program_event(4U, 0x0041FF1FU);
    return status;
}
