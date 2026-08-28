/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Apollo MRAM record synchronizer matched to stock entry
 * 0x00479418.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_sync_uintptr;

typedef unsigned int (*open_cfw_mram_sync_timestamp_function)(void);
typedef void (*open_cfw_mram_sync_publish_function)(
    unsigned int,
    const void *,
    const void *,
    unsigned int,
    unsigned int,
    unsigned int
);
typedef void (*open_cfw_mram_sync_commit_function)(unsigned int);
typedef unsigned int (*open_cfw_mram_sync_log_level_function)(void);
typedef void (*open_cfw_mram_sync_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_sync_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_SYNC_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_SYNC_RECORD_SIZE 0xC8U

#ifndef OPEN_CFW_MRAM_SYNC_RECORD_BASE
#define OPEN_CFW_MRAM_SYNC_RECORD_BASE \
    (*(volatile unsigned char * volatile *) \
        (open_cfw_mram_sync_uintptr)0x0078EE60U)
#endif
#ifndef OPEN_CFW_MRAM_SYNC_COMPARE_KEY
#define OPEN_CFW_MRAM_SYNC_COMPARE_KEY \
    ((const void *)(open_cfw_mram_sync_uintptr)0x00784F90U)
#endif
#ifndef OPEN_CFW_MRAM_SYNC_TIMESTAMP
#define OPEN_CFW_MRAM_SYNC_TIMESTAMP() \
    (((open_cfw_mram_sync_timestamp_function) \
        (open_cfw_mram_sync_uintptr)0x004D2525U)())
#endif
#ifndef OPEN_CFW_MRAM_SYNC_PUBLISH
#define OPEN_CFW_MRAM_SYNC_PUBLISH(...) \
    (((open_cfw_mram_sync_publish_function) \
        (open_cfw_mram_sync_uintptr)0x004D282FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_SYNC_COMMIT
#define OPEN_CFW_MRAM_SYNC_COMMIT(value) \
    (((open_cfw_mram_sync_commit_function) \
        (open_cfw_mram_sync_uintptr)0x004D28CDU)((value)))
#endif
#ifndef OPEN_CFW_MRAM_SYNC_LOG_LEVEL
#define OPEN_CFW_MRAM_SYNC_LOG_LEVEL() \
    (((open_cfw_mram_sync_log_level_function) \
        (open_cfw_mram_sync_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_SYNC_LOG
#define OPEN_CFW_MRAM_SYNC_LOG(...) \
    (((open_cfw_mram_sync_log_function) \
        (open_cfw_mram_sync_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_SYNC_TRACE
#define OPEN_CFW_MRAM_SYNC_TRACE(...) \
    (((open_cfw_mram_sync_trace_function) \
        (open_cfw_mram_sync_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_sync_pointer(open_cfw_mram_sync_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_sync_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_SYNC_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_SYNC_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_sync_record_qualifies(
    const volatile unsigned char *record
)
{
    if (record[0x2FU] == 0U || record[0x30U] == 0U) {
        return 0;
    }
    return open_cfw_memory_compare(
        (const void *)(record + 7U),
        OPEN_CFW_MRAM_SYNC_COMPARE_KEY,
        16U
    ) != 0;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_sync_count_diagnostic(unsigned int count)
{
    count = (unsigned char)count;
    if ((OPEN_CFW_MRAM_SYNC_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_SYNC_LOG(
            4U,
            open_cfw_mram_sync_pointer(0x0078A0D0U),
            open_cfw_mram_sync_pointer(0x006D84BCU),
            open_cfw_mram_sync_pointer(0x00784F60U),
            0x115U,
            open_cfw_mram_sync_pointer(0x007477C4U),
            count
        );
    }
    if (open_cfw_mram_sync_trace_enabled()) {
        const void *identity =
            open_cfw_mram_sync_pointer(0x00726D20U);

        OPEN_CFW_MRAM_SYNC_TRACE(
            0x10400000U,
            identity,
            identity,
            count
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_sync_success_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_SYNC_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_SYNC_LOG(
            4U,
            open_cfw_mram_sync_pointer(0x0078A0D0U),
            open_cfw_mram_sync_pointer(0x006D84BCU),
            open_cfw_mram_sync_pointer(0x00784F60U),
            0x130U,
            open_cfw_mram_sync_pointer(0x007477ECU)
        );
    }
    if (open_cfw_mram_sync_trace_enabled()) {
        const void *identity =
            open_cfw_mram_sync_pointer(0x00726D54U);

        OPEN_CFW_MRAM_SYNC_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

/*
 * Count eligible records, report the count, then reload the record-table
 * pointer and publish each eligible record in table order. The final eligible
 * record is marked explicitly before the batch is committed.
 */
__attribute__((used, noinline))
void open_cfw_mram_sync_records_body(void)
{
    volatile unsigned char *record = OPEN_CFW_MRAM_SYNC_RECORD_BASE;
    unsigned int count = 0U;
    unsigned int index;
    unsigned int sent = 0U;

    for (index = 0U; index < OPEN_CFW_MRAM_SYNC_RECORD_COUNT; ++index) {
        if (open_cfw_mram_sync_record_qualifies(record)) {
            ++count;
        }
        record += OPEN_CFW_MRAM_SYNC_RECORD_SIZE;
    }

    open_cfw_mram_sync_count_diagnostic(count);
    record = OPEN_CFW_MRAM_SYNC_RECORD_BASE;

    for (index = 0U; index < OPEN_CFW_MRAM_SYNC_RECORD_COUNT; ++index) {
        if (open_cfw_mram_sync_record_qualifies(record)) {
            unsigned int last =
                (unsigned char)sent
                == (unsigned int)((unsigned char)count - 1U);
            unsigned int timestamp;

            record[0x2EU] |= 4U;
            timestamp = OPEN_CFW_MRAM_SYNC_TIMESTAMP();
            OPEN_CFW_MRAM_SYNC_PUBLISH(
                record[0x1DU],
                (const void *)(record + 0x17U),
                (const void *)(record + 7U),
                timestamp,
                last,
                0U
            );
            ++sent;
        }
        record += OPEN_CFW_MRAM_SYNC_RECORD_SIZE;
    }

    sent = (unsigned char)sent;
    if (sent != 0U) {
        OPEN_CFW_MRAM_SYNC_COMMIT(1U);
        open_cfw_mram_sync_success_diagnostic();
    }
}

#ifdef OPEN_CFW_MRAM_SYNC_HOST
__attribute__((used, noinline))
void open_cfw_mram_sync_records(void)
{
    open_cfw_mram_sync_records_body();
}
#else
/*
 * The stock entry saves and restores r0-r3 despite having no explicit
 * arguments. Preserve that caller-visible ABI while the C body follows the
 * normal AAPCS callee-saved-register contract. Six pushed registers maintain
 * eight-byte stack alignment at the nested call.
 */
__attribute__((used, noinline, naked))
void open_cfw_mram_sync_records(void)
{
    __asm__ volatile(
        "push {r0, r1, r2, r3, r4, lr}\n"
        "bl open_cfw_mram_sync_records_body\n"
        "pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif
