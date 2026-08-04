/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Apollo protected-MRAM record-database updater matched to stock
 * entry 0x00479B74 (_AppDbUpdateNVM).
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_db_uintptr;

typedef unsigned int (*open_cfw_mram_db_log_level_function)(void);
typedef void (*open_cfw_mram_db_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_db_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_DB_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_DB_RECORD_STRIDE 0x100U
#define OPEN_CFW_MRAM_DB_IDENTIFIER_SIZE 6U

#ifndef OPEN_CFW_MRAM_DB_NVM_BASE
#define OPEN_CFW_MRAM_DB_NVM_BASE \
    ((volatile unsigned char *) \
        (open_cfw_mram_db_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_DB_CACHE_INVALIDATE
#define OPEN_CFW_MRAM_DB_CACHE_INVALIDATE(range, all) \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)(range), \
        (all) \
    )
#endif
#ifndef OPEN_CFW_MRAM_DB_UPDATE_RECORD
#define OPEN_CFW_MRAM_DB_UPDATE_RECORD(record, index) \
    open_cfw_mram_update_one_record((record), (index))
#endif
#ifndef OPEN_CFW_MRAM_DB_DUMP_RECORD
#define OPEN_CFW_MRAM_DB_DUMP_RECORD(record, index) \
    open_cfw_mram_record_diagnostic_dump((record), (index))
#endif
#ifndef OPEN_CFW_MRAM_DB_LOG_LEVEL
#define OPEN_CFW_MRAM_DB_LOG_LEVEL() \
    (((open_cfw_mram_db_log_level_function) \
        (open_cfw_mram_db_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_DB_LOG
#define OPEN_CFW_MRAM_DB_LOG(...) \
    (((open_cfw_mram_db_log_function) \
        (open_cfw_mram_db_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_DB_TRACE
#define OPEN_CFW_MRAM_DB_TRACE(...) \
    (((open_cfw_mram_db_trace_function) \
        (open_cfw_mram_db_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);
void open_cfw_mram_update_one_record(
    const unsigned char *,
    unsigned char
);
void open_cfw_mram_record_diagnostic_dump(
    const void *,
    unsigned int
);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_db_pointer(open_cfw_mram_db_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_db_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_DB_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_DB_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((noinline)) void
open_cfw_mram_db_diagnostic(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    unsigned int argument_count,
    const unsigned int *arguments
)
{
    if ((OPEN_CFW_MRAM_DB_LOG_LEVEL() & 2U) != 0U) {
        if (argument_count == 0U) {
            OPEN_CFW_MRAM_DB_LOG(
                severity,
                open_cfw_mram_db_pointer(0x0078A0D0U),
                open_cfw_mram_db_pointer(0x006D84BCU),
                open_cfw_mram_db_pointer(0x00784F70U),
                line,
                open_cfw_mram_db_pointer(structured_identity)
            );
        }
        else if (argument_count == 1U) {
            OPEN_CFW_MRAM_DB_LOG(
                severity,
                open_cfw_mram_db_pointer(0x0078A0D0U),
                open_cfw_mram_db_pointer(0x006D84BCU),
                open_cfw_mram_db_pointer(0x00784F70U),
                line,
                open_cfw_mram_db_pointer(structured_identity),
                arguments[0]
            );
        }
        else if (argument_count == 2U) {
            OPEN_CFW_MRAM_DB_LOG(
                severity,
                open_cfw_mram_db_pointer(0x0078A0D0U),
                open_cfw_mram_db_pointer(0x006D84BCU),
                open_cfw_mram_db_pointer(0x00784F70U),
                line,
                open_cfw_mram_db_pointer(structured_identity),
                arguments[0],
                arguments[1]
            );
        }
        else if (argument_count == 3U) {
            OPEN_CFW_MRAM_DB_LOG(
                severity,
                open_cfw_mram_db_pointer(0x0078A0D0U),
                open_cfw_mram_db_pointer(0x006D84BCU),
                open_cfw_mram_db_pointer(0x00784F70U),
                line,
                open_cfw_mram_db_pointer(structured_identity),
                arguments[0],
                arguments[1],
                arguments[2]
            );
        }
        else if (argument_count == 6U) {
            OPEN_CFW_MRAM_DB_LOG(
                severity,
                open_cfw_mram_db_pointer(0x0078A0D0U),
                open_cfw_mram_db_pointer(0x006D84BCU),
                open_cfw_mram_db_pointer(0x00784F70U),
                line,
                open_cfw_mram_db_pointer(structured_identity),
                arguments[0],
                arguments[1],
                arguments[2],
                arguments[3],
                arguments[4],
                arguments[5]
            );
        }
        else {
            OPEN_CFW_MRAM_DB_LOG(
                severity,
                open_cfw_mram_db_pointer(0x0078A0D0U),
                open_cfw_mram_db_pointer(0x006D84BCU),
                open_cfw_mram_db_pointer(0x00784F70U),
                line,
                open_cfw_mram_db_pointer(structured_identity),
                arguments[0],
                arguments[1],
                arguments[2],
                arguments[3],
                arguments[4],
                arguments[5],
                arguments[6]
            );
        }
    }

    if (!open_cfw_mram_db_trace_enabled()) {
        return;
    }
    if (argument_count == 0U) {
        const void *identity =
            open_cfw_mram_db_pointer(trace_identity);

        OPEN_CFW_MRAM_DB_TRACE(event, identity, identity);
    }
    else if (argument_count == 1U) {
        const void *identity =
            open_cfw_mram_db_pointer(trace_identity);

        OPEN_CFW_MRAM_DB_TRACE(
            event,
            identity,
            identity,
            arguments[0]
        );
    }
    else if (argument_count == 2U) {
        const void *identity =
            open_cfw_mram_db_pointer(trace_identity);

        OPEN_CFW_MRAM_DB_TRACE(
            event,
            identity,
            identity,
            arguments[0],
            arguments[1]
        );
    }
    else if (argument_count == 3U) {
        const void *identity =
            open_cfw_mram_db_pointer(trace_identity);

        OPEN_CFW_MRAM_DB_TRACE(
            event,
            identity,
            identity,
            arguments[0],
            arguments[1],
            arguments[2]
        );
    }
    else if (argument_count == 6U) {
        const void *identity =
            open_cfw_mram_db_pointer(trace_identity);

        OPEN_CFW_MRAM_DB_TRACE(
            event,
            identity,
            identity,
            arguments[0],
            arguments[1],
            arguments[2],
            arguments[3],
            arguments[4],
            arguments[5]
        );
    }
    else {
        const void *identity =
            open_cfw_mram_db_pointer(trace_identity);

        OPEN_CFW_MRAM_DB_TRACE(
            event,
            identity,
            identity,
            arguments[0],
            arguments[1],
            arguments[2],
            arguments[3],
            arguments[4],
            arguments[5],
            arguments[6]
        );
    }
}

static __attribute__((always_inline)) inline volatile unsigned char *
open_cfw_mram_db_record(unsigned int index)
{
    return OPEN_CFW_MRAM_DB_NVM_BASE
        + index * OPEN_CFW_MRAM_DB_RECORD_STRIDE;
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_db_timestamp(const volatile unsigned char *record)
{
    return *(const volatile unsigned int *)(const volatile void *)(
        record + 0xC4U
    );
}

static __attribute__((always_inline)) inline int
open_cfw_mram_db_identifier_empty(
    const volatile unsigned char *record
)
{
    unsigned int all_zero = 1U;
    unsigned int all_erased = 1U;
    unsigned int index;

    for (index = 0U; index < OPEN_CFW_MRAM_DB_IDENTIFIER_SIZE; ++index) {
        unsigned int value = record[index];

        if (value != 0U) {
            all_zero = 0U;
        }
        if (value != 0xFFU) {
            all_erased = 0U;
        }
    }
    return (all_zero | all_erased) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_db_address_arguments(
    const volatile unsigned char *record,
    unsigned int *arguments
)
{
    arguments[0] = record[5];
    arguments[1] = record[4];
    arguments[2] = record[3];
    arguments[3] = record[2];
    arguments[4] = record[1];
    arguments[5] = record[0];
}

static __attribute__((always_inline)) inline void
open_cfw_mram_db_write_and_dump(
    const unsigned char *record,
    unsigned int index
)
{
    OPEN_CFW_MRAM_DB_UPDATE_RECORD(record, (unsigned char)index);
    OPEN_CFW_MRAM_DB_DUMP_RECORD(
        (const void *)record,
        index
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_app_db_update(
    const unsigned char *record
)
{
    volatile unsigned char *candidate = (volatile unsigned char *)0;
    unsigned int arguments[7];
    unsigned int candidate_index = 0U;
    unsigned int minimum_timestamp = 0xFFFFFFFFU;
    unsigned int priority_selected = 0U;
    unsigned int input_type;
    unsigned int index;

    open_cfw_mram_db_diagnostic(
        4U,
        0x1BEU,
        0x0071258CU,
        0x10000000U,
        0x006F82DCU,
        0U,
        arguments
    );
    (void)OPEN_CFW_MRAM_DB_CACHE_INVALIDATE(0U, 1U);

    arguments[0] = 0x007FF000U;
    arguments[1] = 0x100U;
    arguments[2] = 0x40U;
    open_cfw_mram_db_diagnostic(
        4U,
        0x1CEU,
        0x006F8324U,
        0x10C00000U,
        0x006E6280U,
        3U,
        arguments
    );

    for (index = 0U; index < OPEN_CFW_MRAM_DB_RECORD_COUNT; ++index) {
        volatile unsigned char *stored =
            open_cfw_mram_db_record(index);

        if (
            !open_cfw_mram_db_identifier_empty(stored)
            && open_cfw_memory_compare(
                record,
                (const void *)stored,
                OPEN_CFW_MRAM_DB_IDENTIFIER_SIZE
            ) == 0
        ) {
            arguments[0] = index;
            open_cfw_mram_db_diagnostic(
                4U,
                0x1E8U,
                0x00709124U,
                0x10400000U,
                0x006F836CU,
                1U,
                arguments
            );
            open_cfw_mram_db_write_and_dump(record, index);
            open_cfw_mram_db_diagnostic(
                4U,
                0x1EDU,
                0x00769388U,
                0x10400000U,
                0x00751EA8U,
                1U,
                arguments
            );
            return 1U;
        }
    }

    for (index = 0U; index < OPEN_CFW_MRAM_DB_RECORD_COUNT; ++index) {
        volatile unsigned char *stored =
            open_cfw_mram_db_record(index);

        if (open_cfw_mram_db_identifier_empty(stored)) {
            arguments[0] = index;
            open_cfw_mram_db_diagnostic(
                4U,
                0x20EU,
                0x007001B0U,
                0x10400000U,
                0x006EB4E8U,
                1U,
                arguments
            );
            open_cfw_mram_db_write_and_dump(record, index);
            open_cfw_mram_db_diagnostic(
                4U,
                0x213U,
                0x007693A4U,
                0x10400000U,
                0x00747814U,
                1U,
                arguments
            );
            return 1U;
        }
    }

    input_type = record[0xC3U];
    arguments[0] = input_type != 0U
        ? 0x0078CA4CU
        : 0x0078CA54U;
    open_cfw_mram_db_diagnostic(
        2U,
        0x222U,
        0x006F1800U,
        0x08400000U,
        0x006E2388U,
        1U,
        arguments
    );

    for (index = 0U; index < OPEN_CFW_MRAM_DB_RECORD_COUNT; ++index) {
        volatile unsigned char *stored =
            open_cfw_mram_db_record(index);

        OPEN_CFW_MRAM_DB_DUMP_RECORD(
            (const void *)stored,
            index
        );
        if (stored[0x30U] == 0U && stored[0x2FU] == 0U) {
            arguments[0] = index;
            open_cfw_mram_db_diagnostic(
                4U,
                0x231U,
                0x00709164U,
                0x10400000U,
                0x006F83B4U,
                1U,
                arguments
            );
            candidate = stored;
            candidate_index = index;
            priority_selected = 1U;
            break;
        }
    }

    if (priority_selected == 0U) {
        for (index = 0U; index < OPEN_CFW_MRAM_DB_RECORD_COUNT; ++index) {
            volatile unsigned char *stored =
                open_cfw_mram_db_record(index);
            unsigned int timestamp;

            if (
                stored[0x30U] != 0U
                || stored[0x2FU] != 1U
            ) {
                continue;
            }
            timestamp = open_cfw_mram_db_timestamp(stored);
            if (timestamp < minimum_timestamp) {
                minimum_timestamp = timestamp;
                candidate = stored;
                candidate_index = index;
                priority_selected = 1U;
            }
        }
        if (priority_selected != 0U) {
            arguments[0] = candidate_index;
            arguments[1] = minimum_timestamp;
            open_cfw_mram_db_diagnostic(
                4U,
                0x249U,
                0x006E23E0U,
                0x10800000U,
                0x006D9EA4U,
                2U,
                arguments
            );
        }
    }

    if (priority_selected == 0U) {
        candidate = (volatile unsigned char *)0;
        for (index = 0U; index < OPEN_CFW_MRAM_DB_RECORD_COUNT; ++index) {
            volatile unsigned char *stored =
                open_cfw_mram_db_record(index);
            unsigned int timestamp;

            if (
                stored[0x30U] == 0U
                || stored[0x2FU] == 0U
                || stored[0xC3U] != (unsigned char)input_type
            ) {
                continue;
            }
            timestamp = open_cfw_mram_db_timestamp(stored);
            if (timestamp < minimum_timestamp) {
                minimum_timestamp = timestamp;
                candidate = stored;
                candidate_index = index;
            }
        }

        if (candidate == (volatile unsigned char *)0) {
            for (
                index = 0U;
                index < OPEN_CFW_MRAM_DB_RECORD_COUNT;
                ++index
            ) {
                volatile unsigned char *stored =
                    open_cfw_mram_db_record(index);
                unsigned int timestamp;

                if (
                    stored[0x30U] == 0U
                    || stored[0x2FU] == 0U
                ) {
                    continue;
                }
                timestamp = open_cfw_mram_db_timestamp(stored);
                if (timestamp < minimum_timestamp) {
                    minimum_timestamp = timestamp;
                    candidate = stored;
                    candidate_index = index;
                }
            }
        }

        if (candidate == (volatile unsigned char *)0) {
            for (
                index = 0U;
                index < OPEN_CFW_MRAM_DB_RECORD_COUNT;
                ++index
            ) {
                volatile unsigned char *stored =
                    open_cfw_mram_db_record(index);
                unsigned int timestamp;

                if (
                    stored[0x30U] != 0U
                    || stored[0x2FU] != 1U
                ) {
                    continue;
                }
                timestamp = open_cfw_mram_db_timestamp(stored);
                if (timestamp < minimum_timestamp) {
                    minimum_timestamp = timestamp;
                    candidate = stored;
                    candidate_index = index;
                }
            }
        }
    }

    if (candidate == (volatile unsigned char *)0) {
        open_cfw_mram_db_diagnostic(
            1U,
            0x29CU,
            0x00712640U,
            0x04000000U,
            0x006F848CU,
            0U,
            arguments
        );
        return 0U;
    }

    arguments[0] = candidate_index;
    arguments[1] = open_cfw_mram_db_timestamp(candidate);
    open_cfw_mram_db_diagnostic(
        4U,
        0x27CU,
        0x007125C8U,
        0x10800000U,
        0x007001F4U,
        2U,
        arguments
    );
    open_cfw_mram_db_address_arguments(candidate, arguments);
    open_cfw_mram_db_diagnostic(
        4U,
        0x27FU,
        0x00712604U,
        0x11800000U,
        0x006F83FCU,
        6U,
        arguments
    );
    arguments[0] = candidate_index;
    open_cfw_mram_db_diagnostic(
        4U,
        0x282U,
        0x0074783CU,
        0x10400000U,
        0x00726D88U,
        1U,
        arguments
    );
    arguments[0] = candidate_index << 6U;
    arguments[1] = candidate_index << 8U;
    open_cfw_mram_db_diagnostic(
        4U,
        0x284U,
        0x007091A4U,
        0x10800000U,
        0x006F184CU,
        2U,
        arguments
    );
    arguments[0] = candidate_index << 6U;
    open_cfw_mram_db_diagnostic(
        4U,
        0x285U,
        0x0071BF58U,
        0x10400000U,
        0x00700238U,
        1U,
        arguments
    );

    OPEN_CFW_MRAM_DB_UPDATE_RECORD(
        record,
        (unsigned char)candidate_index
    );
    (void)OPEN_CFW_MRAM_DB_CACHE_INVALIDATE(0U, 1U);
    candidate = open_cfw_mram_db_record(candidate_index);
    if (
        open_cfw_memory_compare(
            (const void *)candidate,
            record,
            OPEN_CFW_MRAM_DB_IDENTIFIER_SIZE
        ) == 0
    ) {
        open_cfw_mram_db_address_arguments(candidate, arguments);
        arguments[6] = candidate_index;
        open_cfw_mram_db_diagnostic(
            4U,
            0x28FU,
            0x006D9F08U,
            0x11C00000U,
            0x006A6BD4U,
            7U,
            arguments
        );
    }
    else {
        arguments[0] = candidate_index;
        open_cfw_mram_db_diagnostic(
            1U,
            0x291U,
            0x006F1898U,
            0x04400000U,
            0x006E2438U,
            1U,
            arguments
        );
        open_cfw_mram_db_address_arguments(
            (const volatile unsigned char *)record,
            arguments
        );
        open_cfw_mram_db_diagnostic(
            1U,
            0x294U,
            0x007091E4U,
            0x05800000U,
            0x006F18E4U,
            6U,
            arguments
        );
        open_cfw_mram_db_address_arguments(candidate, arguments);
        open_cfw_mram_db_diagnostic(
            1U,
            0x297U,
            0x00709224U,
            0x05800000U,
            0x006F8444U,
            6U,
            arguments
        );
    }
    return 1U;
}
