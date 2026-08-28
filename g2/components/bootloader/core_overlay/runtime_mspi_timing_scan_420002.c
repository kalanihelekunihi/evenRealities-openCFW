/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 bootloader MSPI timing scan.
 */

typedef __UINT8_TYPE__ open_cfw_timing_u8;
typedef __UINT32_TYPE__ open_cfw_timing_u32;
typedef __UINTPTR_TYPE__ open_cfw_timing_word;

enum {
    OPEN_CFW_TIMING_ROW_COUNT = 36U,
    OPEN_CFW_TIMING_ROW_SIZE = 6U,
    OPEN_CFW_TIMING_FINE_COUNT = 32U,
    OPEN_CFW_TIMING_FINE_OFFSET = 4U,
    OPEN_CFW_TIMING_TURNAROUND_OFFSET = 5U,
    OPEN_CFW_TIMING_SCAN_TURNAROUND = 8U,
    OPEN_CFW_TIMING_TABLE_ADDRESS = 0x20000244U,
    OPEN_CFW_TIMING_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_TIMING_CONTROL_REQUEST = 16U,
    OPEN_CFW_TIMING_CONTROL_THUMB = 0x004251C1U,
    OPEN_CFW_TIMING_READ_ID_THUMB = 0x0042059FU,
    OPEN_CFW_TIMING_EXPECTED_ID = 0x002539C2U,
    OPEN_CFW_TIMING_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_TIMING_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_TIMING_LOG_FILE = 0x00431540U,
    OPEN_CFW_TIMING_LOG_FUNCTION = 0x00433AB0U,
    OPEN_CFW_TIMING_LOG_SUMMARY_FORMAT = 0x0043160CU,
    OPEN_CFW_TIMING_LOG_ROW_FORMAT = 0x004313D8U,
    OPEN_CFW_TIMING_LOG_CENTER_FORMAT = 0x004334B4U,
    OPEN_CFW_TIMING_LOG_SUMMARY_LINE = 0x1C6U,
    OPEN_CFW_TIMING_LOG_ROW_LINE = 0x1CDU,
    OPEN_CFW_TIMING_LOG_CENTER_LINE = 0x1D3U
};

typedef open_cfw_timing_u32 (*open_cfw_timing_control_fn)(
    void *, open_cfw_timing_u32, void *);
typedef open_cfw_timing_u32 (*open_cfw_timing_read_id_fn)(
    open_cfw_timing_u32 *);
typedef void (*open_cfw_timing_log_fn)(
    open_cfw_timing_u32,
    const void *,
    const void *,
    const void *,
    open_cfw_timing_u32,
    const void *,
    ...);

open_cfw_timing_u32 open_cfw_bootloader_longest_ones_run_41ff60(
    const open_cfw_timing_u32 *);
open_cfw_timing_u32 open_cfw_bootloader_longest_ones_center_41ff74(
    const open_cfw_timing_u32 *);

#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
const open_cfw_timing_u8 *open_cfw_mspi_timing_scan_host_table(void);
void *open_cfw_mspi_timing_scan_host_handle(void);
open_cfw_timing_u32 open_cfw_mspi_timing_scan_host_control(
    void *, open_cfw_timing_u32, void *);
open_cfw_timing_u32 open_cfw_mspi_timing_scan_host_read_id(
    open_cfw_timing_u32 *);
void open_cfw_mspi_timing_scan_host_log(
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32,
    open_cfw_timing_u32);
#endif

static __attribute__((always_inline)) inline const open_cfw_timing_u8 *
open_cfw_timing_table(void)
{
#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
    return open_cfw_mspi_timing_scan_host_table();
#else
    return (const open_cfw_timing_u8 *)(open_cfw_timing_word)
        OPEN_CFW_TIMING_TABLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void *open_cfw_timing_handle(void)
{
#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
    return open_cfw_mspi_timing_scan_host_handle();
#else
    return *(void **)(open_cfw_timing_word)OPEN_CFW_TIMING_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void open_cfw_timing_control(
    void *handle,
    open_cfw_timing_u8 *configuration)
{
#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
    (void)open_cfw_mspi_timing_scan_host_control(
        handle, OPEN_CFW_TIMING_CONTROL_REQUEST, configuration);
#else
    (void)((open_cfw_timing_control_fn)(open_cfw_timing_word)
        OPEN_CFW_TIMING_CONTROL_THUMB)(
            handle, OPEN_CFW_TIMING_CONTROL_REQUEST, configuration);
#endif
}

static __attribute__((always_inline)) inline open_cfw_timing_u32
open_cfw_timing_read_id(open_cfw_timing_u32 *identifier)
{
#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
    return open_cfw_mspi_timing_scan_host_read_id(identifier);
#else
    return ((open_cfw_timing_read_id_fn)(open_cfw_timing_word)
        OPEN_CFW_TIMING_READ_ID_THUMB)(identifier);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_timing_log_summary(
    open_cfw_timing_u32 length,
    open_cfw_timing_u32 row)
{
#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
    open_cfw_mspi_timing_scan_host_log(
        OPEN_CFW_TIMING_LOG_SUMMARY_LINE,
        OPEN_CFW_TIMING_LOG_SUMMARY_FORMAT,
        length,
        row,
        0U,
        0U,
        0U,
        0U,
        0U,
        0U,
        0U,
        2U);
#else
    ((open_cfw_timing_log_fn)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_THUMB)(
        2U,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_TAG,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_FILE,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_FUNCTION,
        OPEN_CFW_TIMING_LOG_SUMMARY_LINE,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_SUMMARY_FORMAT,
        length,
        row);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_timing_log_row(
    const open_cfw_timing_u8 *row,
    open_cfw_timing_u32 pass_mask)
{
#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
    open_cfw_mspi_timing_scan_host_log(
        OPEN_CFW_TIMING_LOG_ROW_LINE,
        OPEN_CFW_TIMING_LOG_ROW_FORMAT,
        row[0],
        row[1],
        row[2],
        row[3],
        row[5],
        pass_mask,
        0U,
        0U,
        0U,
        6U);
#else
    ((open_cfw_timing_log_fn)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_THUMB)(
        2U,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_TAG,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_FILE,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_FUNCTION,
        OPEN_CFW_TIMING_LOG_ROW_LINE,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_ROW_FORMAT,
        row[0],
        row[1],
        row[2],
        row[3],
        row[5],
        pass_mask);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_timing_log_center(
    open_cfw_timing_u32 center)
{
#if defined(OPEN_CFW_MSPI_TIMING_SCAN_HOST)
    open_cfw_mspi_timing_scan_host_log(
        OPEN_CFW_TIMING_LOG_CENTER_LINE,
        OPEN_CFW_TIMING_LOG_CENTER_FORMAT,
        center,
        0U,
        0U,
        0U,
        0U,
        0U,
        0U,
        0U,
        0U,
        1U);
#else
    ((open_cfw_timing_log_fn)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_THUMB)(
        2U,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_TAG,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_FILE,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_FUNCTION,
        OPEN_CFW_TIMING_LOG_CENTER_LINE,
        (const void *)(open_cfw_timing_word)OPEN_CFW_TIMING_LOG_CENTER_FORMAT,
        center);
#endif
}

__attribute__((used, noinline))
open_cfw_timing_u32 open_cfw_bootloader_mspi_timing_scan_420002(
    open_cfw_timing_u8 *result)
{
    open_cfw_timing_u32 pass_masks[OPEN_CFW_TIMING_ROW_COUNT];
    open_cfw_timing_u8 configuration[OPEN_CFW_TIMING_ROW_SIZE];
    const open_cfw_timing_u8 *const table = open_cfw_timing_table();
    void *const handle = open_cfw_timing_handle();
    open_cfw_timing_u32 row;
    open_cfw_timing_u32 fine;
    open_cfw_timing_u32 best_length = 0U;
    open_cfw_timing_u32 best_row = 0U;
    open_cfw_timing_u32 center;

    for (row = 0U; row < OPEN_CFW_TIMING_ROW_COUNT; ++row) {
        pass_masks[row] = 0U;
    }
    for (fine = 0U; fine < OPEN_CFW_TIMING_ROW_SIZE; ++fine) {
        configuration[fine] = 0U;
    }

    for (row = 0U; row < OPEN_CFW_TIMING_ROW_COUNT; ++row) {
        const open_cfw_timing_u8 *const candidate =
            table + row * OPEN_CFW_TIMING_ROW_SIZE;
        configuration[0] = candidate[0];
        configuration[1] = candidate[1];
        configuration[2] = candidate[2];
        configuration[3] = candidate[3];
        configuration[OPEN_CFW_TIMING_TURNAROUND_OFFSET] =
            OPEN_CFW_TIMING_SCAN_TURNAROUND;

        for (fine = 0U; fine < OPEN_CFW_TIMING_FINE_COUNT; ++fine) {
            open_cfw_timing_u32 identifier = 0U;
            configuration[OPEN_CFW_TIMING_FINE_OFFSET] =
                (open_cfw_timing_u8)fine;
            open_cfw_timing_control(handle, configuration);
            if (open_cfw_timing_read_id(&identifier) == 0U &&
                identifier == OPEN_CFW_TIMING_EXPECTED_ID) {
                pass_masks[row] |= 1UL << fine;
            }
        }
    }

    for (row = 0U; row < OPEN_CFW_TIMING_ROW_COUNT; ++row) {
        const open_cfw_timing_u32 length =
            open_cfw_bootloader_longest_ones_run_41ff60(&pass_masks[row]);
        if (best_length < length) {
            best_length = length;
            best_row = row;
        }
    }

    open_cfw_timing_log_summary(best_length, best_row);
    open_cfw_timing_log_row(
        table + best_row * OPEN_CFW_TIMING_ROW_SIZE,
        pass_masks[best_row]);
    center = open_cfw_bootloader_longest_ones_center_41ff74(
        &pass_masks[best_row]);
    open_cfw_timing_log_center(center);

    result[OPEN_CFW_TIMING_FINE_OFFSET] = (open_cfw_timing_u8)center;
    result[0] = table[best_row * OPEN_CFW_TIMING_ROW_SIZE + 0U];
    result[1] = table[best_row * OPEN_CFW_TIMING_ROW_SIZE + 1U];
    result[2] = table[best_row * OPEN_CFW_TIMING_ROW_SIZE + 2U];
    result[3] = table[best_row * OPEN_CFW_TIMING_ROW_SIZE + 3U];
    result[OPEN_CFW_TIMING_TURNAROUND_OFFSET] =
        table[best_row * OPEN_CFW_TIMING_ROW_SIZE +
            OPEN_CFW_TIMING_TURNAROUND_OFFSET];
    return 0U;
}
