/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio record timestamp-update wrapper matched to stock
 * AppDbUpdateRecordTimestamp at 0x0047C084.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_timestamp_uintptr;

typedef unsigned int (*open_cfw_mram_timestamp_log_level_function)(void);
typedef void (*open_cfw_mram_timestamp_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_timestamp_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
#define OPEN_CFW_MRAM_TIMESTAMP_OFFSET 0xC4U

#ifndef OPEN_CFW_MRAM_TIMESTAMP_COUNTER
#define OPEN_CFW_MRAM_TIMESTAMP_COUNTER \
    (*(volatile unsigned int *) \
        (open_cfw_mram_timestamp_uintptr)0x20074344U)
#endif
#ifndef OPEN_CFW_MRAM_TIMESTAMP_RESET
#define OPEN_CFW_MRAM_TIMESTAMP_RESET() \
    open_cfw_mram_reset_record_timestamps()
#endif
#ifndef OPEN_CFW_MRAM_TIMESTAMP_UPDATE
#define OPEN_CFW_MRAM_TIMESTAMP_UPDATE(record) \
    open_cfw_mram_app_db_update((record))
#endif
#ifndef OPEN_CFW_MRAM_TIMESTAMP_VERIFY
#define OPEN_CFW_MRAM_TIMESTAMP_VERIFY(record) \
    open_cfw_mram_verify_write((record))
#endif
#ifndef OPEN_CFW_MRAM_TIMESTAMP_LOG_LEVEL
#define OPEN_CFW_MRAM_TIMESTAMP_LOG_LEVEL() \
    (((open_cfw_mram_timestamp_log_level_function) \
        (open_cfw_mram_timestamp_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_TIMESTAMP_LOG
#define OPEN_CFW_MRAM_TIMESTAMP_LOG(...) \
    (((open_cfw_mram_timestamp_log_function) \
        (open_cfw_mram_timestamp_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_TIMESTAMP_TRACE
#define OPEN_CFW_MRAM_TIMESTAMP_TRACE(...) \
    (((open_cfw_mram_timestamp_trace_function) \
        (open_cfw_mram_timestamp_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned int open_cfw_mram_app_db_update(const unsigned char *);
unsigned int open_cfw_mram_verify_write(const unsigned char *);
void open_cfw_mram_reset_record_timestamps(void);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_timestamp_pointer(open_cfw_mram_timestamp_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_timestamp_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_TIMESTAMP_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_TIMESTAMP_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_timestamp_overflow_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_TIMESTAMP_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_TIMESTAMP_LOG(
            2U,
            open_cfw_mram_timestamp_pointer(0x0078A0D0U),
            open_cfw_mram_timestamp_pointer(0x006D84BCU),
            open_cfw_mram_timestamp_pointer(0x0076944CU),
            0x813U,
            open_cfw_mram_timestamp_pointer(0x006DF6B8U)
        );
    }
    if (open_cfw_mram_timestamp_trace_enabled()) {
        const void *identity =
            open_cfw_mram_timestamp_pointer(0x006D8524U);

        OPEN_CFW_MRAM_TIMESTAMP_TRACE(
            0x08000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_timestamp_updated_diagnostic(unsigned int timestamp)
{
    if ((OPEN_CFW_MRAM_TIMESTAMP_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_TIMESTAMP_LOG(
            4U,
            open_cfw_mram_timestamp_pointer(0x0078A0D0U),
            open_cfw_mram_timestamp_pointer(0x006D84BCU),
            open_cfw_mram_timestamp_pointer(0x0076944CU),
            0x818U,
            open_cfw_mram_timestamp_pointer(0x0071C188U),
            (open_cfw_mram_timestamp_uintptr)timestamp
        );
    }
    if (open_cfw_mram_timestamp_trace_enabled()) {
        const void *identity =
            open_cfw_mram_timestamp_pointer(0x00709524U);

        OPEN_CFW_MRAM_TIMESTAMP_TRACE(
            0x10400000U,
            identity,
            identity,
            (open_cfw_mram_timestamp_uintptr)timestamp
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_timestamp_store(
    unsigned char *record,
    unsigned int timestamp
)
{
    record[OPEN_CFW_MRAM_TIMESTAMP_OFFSET] =
        (unsigned char)timestamp;
    record[OPEN_CFW_MRAM_TIMESTAMP_OFFSET + 1U] =
        (unsigned char)(timestamp >> 8U);
    record[OPEN_CFW_MRAM_TIMESTAMP_OFFSET + 2U] =
        (unsigned char)(timestamp >> 16U);
    record[OPEN_CFW_MRAM_TIMESTAMP_OFFSET + 3U] =
        (unsigned char)(timestamp >> 24U);
}

__attribute__((used, noinline))
void open_cfw_mram_update_record_timestamp(unsigned char *record)
{
    unsigned int timestamp;

    if (record == (unsigned char *)0) {
        return;
    }
    if (OPEN_CFW_MRAM_TIMESTAMP_COUNTER == 0xFFFFFFFFU) {
        open_cfw_mram_timestamp_overflow_diagnostic();
        OPEN_CFW_MRAM_TIMESTAMP_RESET();
    }

    timestamp = OPEN_CFW_MRAM_TIMESTAMP_COUNTER + 1U;
    OPEN_CFW_MRAM_TIMESTAMP_COUNTER = timestamp;
    open_cfw_mram_timestamp_store(record, timestamp);
    open_cfw_mram_timestamp_updated_diagnostic(timestamp);
    (void)OPEN_CFW_MRAM_TIMESTAMP_UPDATE(record);
    (void)OPEN_CFW_MRAM_TIMESTAMP_VERIFY(record);
}
