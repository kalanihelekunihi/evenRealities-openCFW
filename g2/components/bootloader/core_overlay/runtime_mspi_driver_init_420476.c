/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 bootloader MX25U25643G
 * public initialization entry.
 */

typedef __UINT8_TYPE__ open_cfw_driver_init_u8;
typedef __UINT32_TYPE__ open_cfw_driver_init_u32;
typedef __UINTPTR_TYPE__ open_cfw_driver_init_word;

enum {
    OPEN_CFW_DRIVER_INIT_STATE_SLOT = 0x200270D8U,
    OPEN_CFW_DRIVER_INIT_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_DRIVER_INIT_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_DRIVER_INIT_LOG_FILE = 0x00431540U,
    OPEN_CFW_DRIVER_INIT_LOG_FUNCTION = 0x004337CCU,
    OPEN_CFW_DRIVER_INIT_FAIL_FORMAT = 0x004337E4U,
    OPEN_CFW_DRIVER_ID_FAIL_FORMAT = 0x00433AC4U,
    OPEN_CFW_DRIVER_ID_FORMAT = 0x00433AD8U,
    OPEN_CFW_DRIVER_INIT_FAIL_LINE = 0x284U,
    OPEN_CFW_DRIVER_ID_FAIL_LINE = 0x28EU,
    OPEN_CFW_DRIVER_ID_LINE = 0x292U
};

typedef void (*open_cfw_driver_init_void_fn)(void);
typedef void (*open_cfw_driver_init_u32_fn)(open_cfw_driver_init_u32);
typedef open_cfw_driver_init_u32 (*open_cfw_driver_init_read_id_fn)(
    open_cfw_driver_init_u32 *);
typedef void (*open_cfw_driver_init_log_fn)(
    open_cfw_driver_init_u32, const void *, const void *, const void *,
    open_cfw_driver_init_u32, const void *, ...);

open_cfw_driver_init_u32 open_cfw_bootloader_mspi_low_level_init_420254(
    open_cfw_driver_init_u32, const open_cfw_driver_init_u8 *, void *);
void open_cfw_bootloader_delay_milliseconds_41f9d8(open_cfw_driver_init_u32);
void open_cfw_bootloader_mspi_timing_auto_4201ba(void);
void open_cfw_bootloader_event_flags_init_41fe62(void);
void open_cfw_bootloader_mspi_enable_41fe28(void);

#if defined(OPEN_CFW_MSPI_DRIVER_INIT_HOST)
open_cfw_driver_init_u32 open_cfw_driver_init_host_call(
    open_cfw_driver_init_u32, open_cfw_driver_init_u32, void *);
void open_cfw_driver_init_host_log(
    open_cfw_driver_init_u32, open_cfw_driver_init_u32,
    open_cfw_driver_init_u32, open_cfw_driver_init_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_driver_init_u32
open_cfw_driver_init_call(open_cfw_driver_init_u32 operation,
    open_cfw_driver_init_u32 value, void *pointer)
{
#if defined(OPEN_CFW_MSPI_DRIVER_INIT_HOST)
    return open_cfw_driver_init_host_call(operation, value, pointer);
#else
    switch (operation) {
    case 0U:
        return open_cfw_bootloader_mspi_low_level_init_420254(
            1U, (const open_cfw_driver_init_u8 *)0,
            (void *)(open_cfw_driver_init_word)OPEN_CFW_DRIVER_INIT_STATE_SLOT);
    case 1U:
        open_cfw_bootloader_delay_milliseconds_41f9d8(value);
        return 0U;
    case 2U:
        ((open_cfw_driver_init_void_fn)(open_cfw_driver_init_word)
            0x0042052BU)();
        return 0U;
    case 3U:
        ((open_cfw_driver_init_void_fn)(open_cfw_driver_init_word)
            0x00420F11U)();
        return 0U;
    case 4U:
        open_cfw_bootloader_mspi_timing_auto_4201ba();
        return 0U;
    case 5U:
        return ((open_cfw_driver_init_read_id_fn)(open_cfw_driver_init_word)
            0x0042059FU)((open_cfw_driver_init_u32 *)pointer);
    case 6U:
        ((open_cfw_driver_init_void_fn)(open_cfw_driver_init_word)
            0x00420891U)();
        return 0U;
    case 7U:
        ((open_cfw_driver_init_u32_fn)(open_cfw_driver_init_word)
            0x00420C5DU)(value);
        return 0U;
    case 8U:
        open_cfw_bootloader_event_flags_init_41fe62();
        return 0U;
    default:
        open_cfw_bootloader_mspi_enable_41fe28();
        return 0U;
    }
#endif
}

static __attribute__((always_inline)) inline void open_cfw_driver_init_log(
    open_cfw_driver_init_u32 level, open_cfw_driver_init_u32 line,
    open_cfw_driver_init_u32 format, open_cfw_driver_init_u32 value)
{
#if defined(OPEN_CFW_MSPI_DRIVER_INIT_HOST)
    open_cfw_driver_init_host_log(level, line, format, value);
#else
    ((open_cfw_driver_init_log_fn)(open_cfw_driver_init_word)
        OPEN_CFW_DRIVER_INIT_LOG_THUMB)(level,
            (const void *)(open_cfw_driver_init_word)OPEN_CFW_DRIVER_INIT_LOG_TAG,
            (const void *)(open_cfw_driver_init_word)OPEN_CFW_DRIVER_INIT_LOG_FILE,
            (const void *)(open_cfw_driver_init_word)
                OPEN_CFW_DRIVER_INIT_LOG_FUNCTION,
            line, (const void *)(open_cfw_driver_init_word)format, value);
#endif
}

__attribute__((used, noinline))
open_cfw_driver_init_u32 open_cfw_bootloader_mspi_driver_init_420476(void)
{
    open_cfw_driver_init_u32 identifier = 0U;
    open_cfw_driver_init_u32 status;

    status = open_cfw_driver_init_call(0U, 0U, (void *)0);
    if (status != 0U) {
        open_cfw_driver_init_log(1U, OPEN_CFW_DRIVER_INIT_FAIL_LINE,
            OPEN_CFW_DRIVER_INIT_FAIL_FORMAT, status);
        return status;
    }

    (void)open_cfw_driver_init_call(1U, 10U, (void *)0);
    (void)open_cfw_driver_init_call(2U, 0U, (void *)0);
    (void)open_cfw_driver_init_call(3U, 0U, (void *)0);
    (void)open_cfw_driver_init_call(4U, 0U, (void *)0);
    (void)open_cfw_driver_init_call(3U, 0U, (void *)0);
    status = open_cfw_driver_init_call(5U, 0U, &identifier);
    if (status != 0U) {
        open_cfw_driver_init_log(1U, OPEN_CFW_DRIVER_ID_FAIL_LINE,
            OPEN_CFW_DRIVER_ID_FAIL_FORMAT, status);
        return status;
    }

    open_cfw_driver_init_log(3U, OPEN_CFW_DRIVER_ID_LINE,
        OPEN_CFW_DRIVER_ID_FORMAT, identifier);
    (void)open_cfw_driver_init_call(6U, 0U, (void *)0);
    (void)open_cfw_driver_init_call(7U, 1U, (void *)0);
    (void)open_cfw_driver_init_call(8U, 0U, (void *)0);
    (void)open_cfw_driver_init_call(9U, 0U, (void *)0);
    return 0U;
}
