/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 bootloader automatic MSPI
 * timing-selection wrapper.
 */

typedef __UINT8_TYPE__ open_cfw_timing_auto_u8;
typedef __UINT32_TYPE__ open_cfw_timing_auto_u32;
typedef __UINTPTR_TYPE__ open_cfw_timing_auto_word;

enum {
    OPEN_CFW_TIMING_AUTO_CONFIGURATION_SIZE = 6U,
    OPEN_CFW_TIMING_AUTO_ACTIVE_ADDRESS = 0x2000023CU,
    OPEN_CFW_TIMING_AUTO_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_TIMING_AUTO_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_TIMING_AUTO_LOG_FILE = 0x00431540U,
    OPEN_CFW_TIMING_AUTO_LOG_FUNCTION = 0x004337B4U,
    OPEN_CFW_TIMING_AUTO_SUCCESS_FORMAT = 0x00430BD0U,
    OPEN_CFW_TIMING_AUTO_FAILURE_FORMAT = 0x00430C4CU,
    OPEN_CFW_TIMING_AUTO_SUCCESS_LINE = 0x1F3U,
    OPEN_CFW_TIMING_AUTO_FAILURE_LINE = 0x1FBU
};

typedef void (*open_cfw_timing_auto_log_fn)(
    open_cfw_timing_auto_u32,
    const void *,
    const void *,
    const void *,
    open_cfw_timing_auto_u32,
    const void *,
    ...);

open_cfw_timing_auto_u32 open_cfw_bootloader_mspi_timing_scan_420002(
    open_cfw_timing_auto_u8 *);

#if defined(OPEN_CFW_MSPI_TIMING_AUTO_HOST)
open_cfw_timing_auto_u8 *open_cfw_mspi_timing_auto_host_active(void);
open_cfw_timing_auto_u32 open_cfw_mspi_timing_auto_host_scan(
    open_cfw_timing_auto_u8 *);
void open_cfw_mspi_timing_auto_host_log(
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32,
    open_cfw_timing_auto_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_timing_auto_u8 *
open_cfw_timing_auto_active(void)
{
#if defined(OPEN_CFW_MSPI_TIMING_AUTO_HOST)
    return open_cfw_mspi_timing_auto_host_active();
#else
    return (open_cfw_timing_auto_u8 *)(open_cfw_timing_auto_word)
        OPEN_CFW_TIMING_AUTO_ACTIVE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_timing_auto_u32
open_cfw_timing_auto_scan(open_cfw_timing_auto_u8 *configuration)
{
#if defined(OPEN_CFW_MSPI_TIMING_AUTO_HOST)
    return open_cfw_mspi_timing_auto_host_scan(configuration);
#else
    return open_cfw_bootloader_mspi_timing_scan_420002(configuration);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_timing_auto_log(
    open_cfw_timing_auto_u32 level,
    open_cfw_timing_auto_u32 line,
    open_cfw_timing_auto_u32 format,
    const open_cfw_timing_auto_u8 *configuration)
{
#if defined(OPEN_CFW_MSPI_TIMING_AUTO_HOST)
    open_cfw_mspi_timing_auto_host_log(
        level,
        line,
        format,
        configuration[0],
        configuration[1],
        configuration[2],
        configuration[3],
        configuration[4],
        configuration[5],
        0U,
        0U,
        6U);
#else
    ((open_cfw_timing_auto_log_fn)(open_cfw_timing_auto_word)
        OPEN_CFW_TIMING_AUTO_LOG_THUMB)(
            level,
            (const void *)(open_cfw_timing_auto_word)
                OPEN_CFW_TIMING_AUTO_LOG_TAG,
            (const void *)(open_cfw_timing_auto_word)
                OPEN_CFW_TIMING_AUTO_LOG_FILE,
            (const void *)(open_cfw_timing_auto_word)
                OPEN_CFW_TIMING_AUTO_LOG_FUNCTION,
            line,
            (const void *)(open_cfw_timing_auto_word)format,
            configuration[0],
            configuration[1],
            configuration[2],
            configuration[3],
            configuration[4],
            configuration[5]);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_timing_auto_4201ba(void)
{
    open_cfw_timing_auto_u8 scanned[OPEN_CFW_TIMING_AUTO_CONFIGURATION_SIZE];
    open_cfw_timing_auto_u8 *const active = open_cfw_timing_auto_active();
    open_cfw_timing_auto_u32 index;

    for (index = 0U; index < OPEN_CFW_TIMING_AUTO_CONFIGURATION_SIZE; ++index) {
        scanned[index] = 0U;
    }

    if (open_cfw_timing_auto_scan(scanned) == 0U) {
        /* The stock widened copy also touches two ABI-padding bytes. Only the
         * six-byte timing object is meaningful, so preserve adjacent state. */
        for (index = 0U; index < OPEN_CFW_TIMING_AUTO_CONFIGURATION_SIZE;
             ++index) {
            active[index] = scanned[index];
        }
        open_cfw_timing_auto_log(
            2U,
            OPEN_CFW_TIMING_AUTO_SUCCESS_LINE,
            OPEN_CFW_TIMING_AUTO_SUCCESS_FORMAT,
            active);
    } else {
        open_cfw_timing_auto_log(
            1U,
            OPEN_CFW_TIMING_AUTO_FAILURE_LINE,
            OPEN_CFW_TIMING_AUTO_FAILURE_FORMAT,
            active);
    }
}
