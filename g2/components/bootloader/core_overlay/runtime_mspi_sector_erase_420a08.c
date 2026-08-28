/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G sector erase service. */

typedef __UINT8_TYPE__ open_cfw_sector_erase_u8;
typedef __UINT32_TYPE__ open_cfw_sector_erase_u32;
typedef __UINTPTR_TYPE__ open_cfw_sector_erase_word;

enum {
    OPEN_CFW_SECTOR_ERASE_COMMAND = 0x20U,
    OPEN_CFW_SECTOR_ERASE_LIMIT = 0x02000000U,
    OPEN_CFW_SECTOR_ERASE_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_SECTOR_ERASE_PRINTF_THUMB = 0x00415FAFU,
    OPEN_CFW_SECTOR_ERASE_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_SECTOR_ERASE_LOG_FILE = 0x00431540U,
    OPEN_CFW_SECTOR_ERASE_LOG_FUNCTION = 0x00433540U,
    OPEN_CFW_SECTOR_ERASE_ALIGN_FORMAT = 0x00432D54U,
    OPEN_CFW_SECTOR_ERASE_ALIGN_LINE = 0x40EU,
    OPEN_CFW_SECTOR_ERASE_PREWAIT_FORMAT = 0x00432148U,
    OPEN_CFW_SECTOR_ERASE_ENABLE_FORMAT = 0x0043267CU,
    OPEN_CFW_SECTOR_ERASE_COMMAND_FORMAT = 0x00432178U,
    OPEN_CFW_SECTOR_ERASE_POSTWAIT_FORMAT = 0x004321A8U,
    OPEN_CFW_SECTOR_ERASE_DISABLE_FORMAT = 0x004321D8U
};

typedef open_cfw_sector_erase_u32 (*open_cfw_sector_erase_call_fn)(void);
typedef open_cfw_sector_erase_u32 (*open_cfw_sector_erase_transfer_fn)(
    open_cfw_sector_erase_u32, open_cfw_sector_erase_u32,
    open_cfw_sector_erase_u32, const open_cfw_sector_erase_u8 *,
    open_cfw_sector_erase_u32);
typedef void (*open_cfw_sector_erase_log_fn)(
    open_cfw_sector_erase_u32, const void *, const void *, const void *,
    open_cfw_sector_erase_u32, const void *);
typedef void (*open_cfw_sector_erase_printf1_fn)(const void *,
    open_cfw_sector_erase_u32);
typedef void (*open_cfw_sector_erase_printf2_fn)(const void *,
    open_cfw_sector_erase_u32, open_cfw_sector_erase_u32);

#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_available(void);
void open_cfw_sector_erase_host_event(open_cfw_sector_erase_u32);
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_wait(void);
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_enable(void);
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_transfer(
    open_cfw_sector_erase_u32, open_cfw_sector_erase_u32,
    open_cfw_sector_erase_u32, const open_cfw_sector_erase_u8 *,
    open_cfw_sector_erase_u32);
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_disable(void);
void open_cfw_sector_erase_host_invalid_log(void);
void open_cfw_sector_erase_host_diag(
    open_cfw_sector_erase_u32, open_cfw_sector_erase_u32,
    open_cfw_sector_erase_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_sector_erase_u32
open_cfw_sector_erase_available(void)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    return open_cfw_sector_erase_host_available();
#else
    return *(const volatile open_cfw_sector_erase_u32 *)(open_cfw_sector_erase_word)
        0x200270DCU != 0U;
#endif
}

static __attribute__((always_inline)) inline void open_cfw_sector_erase_event(
    open_cfw_sector_erase_u32 event, open_cfw_sector_erase_word target)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    (void)target;
    open_cfw_sector_erase_host_event(event);
#else
    (void)event;
    ((void (*)(void))target)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_sector_erase_u32
open_cfw_sector_erase_wait(void)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    return open_cfw_sector_erase_host_wait();
#else
    return ((open_cfw_sector_erase_call_fn)(open_cfw_sector_erase_word)
        0x004207F5U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_sector_erase_u32
open_cfw_sector_erase_enable(void)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    return open_cfw_sector_erase_host_enable();
#else
    return ((open_cfw_sector_erase_call_fn)(open_cfw_sector_erase_word)
        0x00420985U)();
#endif
}

static __attribute__((always_inline)) inline open_cfw_sector_erase_u32
open_cfw_sector_erase_transfer(open_cfw_sector_erase_u32 address)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    return open_cfw_sector_erase_host_transfer(OPEN_CFW_SECTOR_ERASE_COMMAND,
        address, 1U, (const open_cfw_sector_erase_u8 *)0, 0U);
#else
    return ((open_cfw_sector_erase_transfer_fn)(open_cfw_sector_erase_word)
        0x0042069FU)(OPEN_CFW_SECTOR_ERASE_COMMAND, address, 1U,
            (const open_cfw_sector_erase_u8 *)0, 0U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_sector_erase_u32
open_cfw_sector_erase_disable(void)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    return open_cfw_sector_erase_host_disable();
#else
    return ((open_cfw_sector_erase_call_fn)(open_cfw_sector_erase_word)
        0x004209C5U)();
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_sector_erase_invalid_log(void)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    open_cfw_sector_erase_host_invalid_log();
#else
    ((open_cfw_sector_erase_log_fn)(open_cfw_sector_erase_word)
        OPEN_CFW_SECTOR_ERASE_LOG_THUMB)(2U,
            (const void *)(open_cfw_sector_erase_word)
                OPEN_CFW_SECTOR_ERASE_LOG_TAG,
            (const void *)(open_cfw_sector_erase_word)
                OPEN_CFW_SECTOR_ERASE_LOG_FILE,
            (const void *)(open_cfw_sector_erase_word)
                OPEN_CFW_SECTOR_ERASE_LOG_FUNCTION,
            OPEN_CFW_SECTOR_ERASE_ALIGN_LINE,
            (const void *)(open_cfw_sector_erase_word)
                OPEN_CFW_SECTOR_ERASE_ALIGN_FORMAT);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_sector_erase_diag(
    open_cfw_sector_erase_u32 format, open_cfw_sector_erase_u32 address,
    open_cfw_sector_erase_u32 status, open_cfw_sector_erase_u32 has_status)
{
#if defined(OPEN_CFW_MSPI_SECTOR_ERASE_HOST)
    open_cfw_sector_erase_host_diag(format, address,
        has_status != 0U ? status : 0U);
#else
    if (has_status != 0U) {
        ((open_cfw_sector_erase_printf2_fn)(open_cfw_sector_erase_word)
            OPEN_CFW_SECTOR_ERASE_PRINTF_THUMB)(
                (const void *)(open_cfw_sector_erase_word)format,
                address, status);
    } else {
        ((open_cfw_sector_erase_printf1_fn)(open_cfw_sector_erase_word)
            OPEN_CFW_SECTOR_ERASE_PRINTF_THUMB)(
                (const void *)(open_cfw_sector_erase_word)format, address);
    }
#endif
}

__attribute__((used, noinline))
open_cfw_sector_erase_u32 open_cfw_bootloader_mspi_sector_erase_420a08(
    open_cfw_sector_erase_u32 address)
{
    open_cfw_sector_erase_u32 status;

    if (open_cfw_sector_erase_available() == 0U) {
        return 2U;
    }
    if ((address & 0xFFFU) != 0U) {
        open_cfw_sector_erase_invalid_log();
        return 6U;
    }
    if (address >= OPEN_CFW_SECTOR_ERASE_LIMIT) {
        return 5U;
    }

    open_cfw_sector_erase_event(1U, 0x0041FF09U);
    open_cfw_sector_erase_event(2U, 0x00420F11U);
    if (open_cfw_sector_erase_wait() != 0U) {
        open_cfw_sector_erase_diag(OPEN_CFW_SECTOR_ERASE_PREWAIT_FORMAT,
            address, 0U, 0U);
        status = 3U;
    } else {
        status = open_cfw_sector_erase_enable();
        if (status != 0U) {
            open_cfw_sector_erase_diag(OPEN_CFW_SECTOR_ERASE_ENABLE_FORMAT,
                address, status, 1U);
        } else {
            status = open_cfw_sector_erase_transfer(address);
            if (status != 0U) {
                open_cfw_sector_erase_diag(OPEN_CFW_SECTOR_ERASE_COMMAND_FORMAT,
                    address, status, 1U);
            } else if (open_cfw_sector_erase_wait() != 0U) {
                open_cfw_sector_erase_diag(
                    OPEN_CFW_SECTOR_ERASE_POSTWAIT_FORMAT,
                    address, 0U, 0U);
                status = 4U;
            } else {
                status = open_cfw_sector_erase_disable();
                if (status != 0U) {
                    open_cfw_sector_erase_diag(
                        OPEN_CFW_SECTOR_ERASE_DISABLE_FORMAT,
                        address, status, 1U);
                }
            }
        }
    }
    open_cfw_sector_erase_event(3U, 0x00420E8DU);
    open_cfw_sector_erase_event(4U, 0x0041FF1FU);
    return status;
}
