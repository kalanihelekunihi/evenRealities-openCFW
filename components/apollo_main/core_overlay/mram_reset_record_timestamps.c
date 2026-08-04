/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio record timestamp-renumbering routine matched to stock
 * AppDbResetRecordTimestamps at 0x0047C164.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_renumber_uintptr;

typedef unsigned int (*open_cfw_mram_renumber_log_level_function)(void);
typedef void (*open_cfw_mram_renumber_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_renumber_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_RENUMBER_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_RENUMBER_RECORD_SIZE 200U
#define OPEN_CFW_MRAM_RENUMBER_ALLOCATED_OFFSET 0x2FU
#define OPEN_CFW_MRAM_RENUMBER_ACTIVE_OFFSET 0x30U
#define OPEN_CFW_MRAM_RENUMBER_TIMESTAMP_OFFSET 0xC4U

#ifndef OPEN_CFW_MRAM_RENUMBER_COUNTER
#define OPEN_CFW_MRAM_RENUMBER_COUNTER \
    (*(volatile unsigned int *) \
        (open_cfw_mram_renumber_uintptr)0x20074344U)
#endif
#ifndef OPEN_CFW_MRAM_RENUMBER_RECORD_BASE
#define OPEN_CFW_MRAM_RENUMBER_RECORD_BASE \
    ((unsigned char *)(open_cfw_mram_renumber_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_RENUMBER_UPDATE
#define OPEN_CFW_MRAM_RENUMBER_UPDATE(record) \
    open_cfw_mram_app_db_update((record))
#endif
#ifndef OPEN_CFW_MRAM_RENUMBER_LOG_LEVEL
#define OPEN_CFW_MRAM_RENUMBER_LOG_LEVEL() \
    (((open_cfw_mram_renumber_log_level_function) \
        (open_cfw_mram_renumber_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_RENUMBER_LOG
#define OPEN_CFW_MRAM_RENUMBER_LOG(...) \
    (((open_cfw_mram_renumber_log_function) \
        (open_cfw_mram_renumber_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_RENUMBER_TRACE
#define OPEN_CFW_MRAM_RENUMBER_TRACE(...) \
    (((open_cfw_mram_renumber_trace_function) \
        (open_cfw_mram_renumber_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned int open_cfw_mram_app_db_update(const unsigned char *);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_renumber_pointer(open_cfw_mram_renumber_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_renumber_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_RENUMBER_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_RENUMBER_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_renumber_boundary_diagnostic(
    unsigned int line,
    open_cfw_mram_renumber_uintptr structured_identity,
    open_cfw_mram_renumber_uintptr trace_identity
)
{
    if ((OPEN_CFW_MRAM_RENUMBER_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RENUMBER_LOG(
            4U,
            open_cfw_mram_renumber_pointer(0x0078A0D0U),
            open_cfw_mram_renumber_pointer(0x006D84BCU),
            open_cfw_mram_renumber_pointer(0x00775194U),
            line,
            open_cfw_mram_renumber_pointer(structured_identity)
        );
    }
    if (open_cfw_mram_renumber_trace_enabled()) {
        const void *identity =
            open_cfw_mram_renumber_pointer(trace_identity);

        OPEN_CFW_MRAM_RENUMBER_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_renumber_record_diagnostic(
    unsigned int index,
    unsigned int timestamp
)
{
    if ((OPEN_CFW_MRAM_RENUMBER_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RENUMBER_LOG(
            4U,
            open_cfw_mram_renumber_pointer(0x0078A0D0U),
            open_cfw_mram_renumber_pointer(0x006D84BCU),
            open_cfw_mram_renumber_pointer(0x00775194U),
            0x835U,
            open_cfw_mram_renumber_pointer(0x00712898U),
            (open_cfw_mram_renumber_uintptr)index,
            (open_cfw_mram_renumber_uintptr)timestamp
        );
    }
    if (open_cfw_mram_renumber_trace_enabled()) {
        const void *identity =
            open_cfw_mram_renumber_pointer(0x006F863CU);

        OPEN_CFW_MRAM_RENUMBER_TRACE(
            0x10800000U,
            identity,
            identity,
            (open_cfw_mram_renumber_uintptr)index,
            (open_cfw_mram_renumber_uintptr)timestamp
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_renumber_store_timestamp(
    unsigned char *record,
    unsigned int timestamp
)
{
    record[OPEN_CFW_MRAM_RENUMBER_TIMESTAMP_OFFSET] =
        (unsigned char)timestamp;
    record[OPEN_CFW_MRAM_RENUMBER_TIMESTAMP_OFFSET + 1U] =
        (unsigned char)(timestamp >> 8U);
    record[OPEN_CFW_MRAM_RENUMBER_TIMESTAMP_OFFSET + 2U] =
        (unsigned char)(timestamp >> 16U);
    record[OPEN_CFW_MRAM_RENUMBER_TIMESTAMP_OFFSET + 3U] =
        (unsigned char)(timestamp >> 24U);
}

__attribute__((used, noinline))
void open_cfw_mram_reset_record_timestamps(void)
{
    unsigned char *record = OPEN_CFW_MRAM_RENUMBER_RECORD_BASE;
    unsigned int index;

    open_cfw_mram_renumber_boundary_diagnostic(
        0x82BU,
        0x0071285CU,
        0x00700524U
    );
    OPEN_CFW_MRAM_RENUMBER_COUNTER = 0U;

    for (index = 0U; index < OPEN_CFW_MRAM_RENUMBER_RECORD_COUNT; ++index) {
        if (
            record[OPEN_CFW_MRAM_RENUMBER_ALLOCATED_OFFSET] != 0U
            && record[OPEN_CFW_MRAM_RENUMBER_ACTIVE_OFFSET] != 0U
        ) {
            unsigned int timestamp = OPEN_CFW_MRAM_RENUMBER_COUNTER + 1U;

            OPEN_CFW_MRAM_RENUMBER_COUNTER = timestamp;
            open_cfw_mram_renumber_store_timestamp(record, timestamp);
            open_cfw_mram_renumber_record_diagnostic(index, timestamp);
            (void)OPEN_CFW_MRAM_RENUMBER_UPDATE(record);
        }
        record += OPEN_CFW_MRAM_RENUMBER_RECORD_SIZE;
    }

    open_cfw_mram_renumber_boundary_diagnostic(
        0x83EU,
        0x007128D4U,
        0x006F8684U
    );
}
