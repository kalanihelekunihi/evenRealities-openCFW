/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio protected-MRAM status reporter matched to stock
 * AppDbShowAllRecordsStatus at 0x0047BC30.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_status_uintptr;

typedef unsigned int (*open_cfw_mram_status_log_level_function)(void);
typedef void (*open_cfw_mram_status_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_status_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_STATUS_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_STATUS_RECORD_STRIDE 0x100U
#define OPEN_CFW_MRAM_STATUS_OWNER_OFFSET 0x06U
#define OPEN_CFW_MRAM_STATUS_KEY_MASK_OFFSET 0x2EU
#define OPEN_CFW_MRAM_STATUS_IN_USE_OFFSET 0x2FU
#define OPEN_CFW_MRAM_STATUS_VALID_OFFSET 0x30U
#define OPEN_CFW_MRAM_STATUS_TIMESTAMP_OFFSET 0xC4U

#ifndef OPEN_CFW_MRAM_STATUS_NVM_BASE
#define OPEN_CFW_MRAM_STATUS_NVM_BASE \
    ((const volatile unsigned char *) \
        (open_cfw_mram_status_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_STATUS_TIMESTAMP_COUNTER
#define OPEN_CFW_MRAM_STATUS_TIMESTAMP_COUNTER \
    (*(const volatile unsigned int *) \
        (open_cfw_mram_status_uintptr)0x20074344U)
#endif
#ifndef OPEN_CFW_MRAM_STATUS_CACHE_INVALIDATE
#define OPEN_CFW_MRAM_STATUS_CACHE_INVALIDATE(range, clean) \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)(range), \
        (clean) \
    )
#endif
#ifndef OPEN_CFW_MRAM_STATUS_LOG_LEVEL
#define OPEN_CFW_MRAM_STATUS_LOG_LEVEL() \
    (((open_cfw_mram_status_log_level_function) \
        (open_cfw_mram_status_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_STATUS_LOG
#define OPEN_CFW_MRAM_STATUS_LOG(...) \
    (((open_cfw_mram_status_log_function) \
        (open_cfw_mram_status_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_STATUS_TRACE
#define OPEN_CFW_MRAM_STATUS_TRACE(...) \
    (((open_cfw_mram_status_trace_function) \
        (open_cfw_mram_status_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_mram_status_pointer(open_cfw_mram_status_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_status_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_STATUS_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_STATUS_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_status_u32(const volatile unsigned char *pointer)
{
    return (
        (unsigned int)pointer[0]
        | ((unsigned int)pointer[1] << 8U)
        | ((unsigned int)pointer[2] << 16U)
        | ((unsigned int)pointer[3] << 24U)
    );
}

static __attribute__((always_inline)) inline void
open_cfw_mram_status_pair0(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_MRAM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_STATUS_LOG(
            4U,
            open_cfw_mram_status_pointer(0x0078A0D0U),
            open_cfw_mram_status_pointer(0x006D84BCU),
            open_cfw_mram_status_pointer(0x00769430U),
            line,
            open_cfw_mram_status_pointer(structured_identity)
        );
    }
    if (open_cfw_mram_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_status_pointer(trace_identity);

        OPEN_CFW_MRAM_STATUS_TRACE(event, identity, identity);
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_status_pair1(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    open_cfw_mram_status_uintptr argument0
)
{
    if ((OPEN_CFW_MRAM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_STATUS_LOG(
            4U,
            open_cfw_mram_status_pointer(0x0078A0D0U),
            open_cfw_mram_status_pointer(0x006D84BCU),
            open_cfw_mram_status_pointer(0x00769430U),
            line,
            open_cfw_mram_status_pointer(structured_identity),
            argument0
        );
    }
    if (open_cfw_mram_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_status_pointer(trace_identity);

        OPEN_CFW_MRAM_STATUS_TRACE(
            event,
            identity,
            identity,
            argument0
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_status_pair2(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    open_cfw_mram_status_uintptr argument0,
    open_cfw_mram_status_uintptr argument1
)
{
    if ((OPEN_CFW_MRAM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_STATUS_LOG(
            4U,
            open_cfw_mram_status_pointer(0x0078A0D0U),
            open_cfw_mram_status_pointer(0x006D84BCU),
            open_cfw_mram_status_pointer(0x00769430U),
            line,
            open_cfw_mram_status_pointer(structured_identity),
            argument0,
            argument1
        );
    }
    if (open_cfw_mram_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_status_pointer(trace_identity);

        OPEN_CFW_MRAM_STATUS_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_status_pair3(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    open_cfw_mram_status_uintptr argument0,
    open_cfw_mram_status_uintptr argument1,
    open_cfw_mram_status_uintptr argument2
)
{
    if ((OPEN_CFW_MRAM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_STATUS_LOG(
            4U,
            open_cfw_mram_status_pointer(0x0078A0D0U),
            open_cfw_mram_status_pointer(0x006D84BCU),
            open_cfw_mram_status_pointer(0x00769430U),
            line,
            open_cfw_mram_status_pointer(structured_identity),
            argument0,
            argument1,
            argument2
        );
    }
    if (open_cfw_mram_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_status_pointer(trace_identity);

        OPEN_CFW_MRAM_STATUS_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1,
            argument2
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_status_pair7(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    open_cfw_mram_status_uintptr argument0,
    open_cfw_mram_status_uintptr argument1,
    open_cfw_mram_status_uintptr argument2,
    open_cfw_mram_status_uintptr argument3,
    open_cfw_mram_status_uintptr argument4,
    open_cfw_mram_status_uintptr argument5,
    open_cfw_mram_status_uintptr argument6
)
{
    if ((OPEN_CFW_MRAM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_STATUS_LOG(
            4U,
            open_cfw_mram_status_pointer(0x0078A0D0U),
            open_cfw_mram_status_pointer(0x006D84BCU),
            open_cfw_mram_status_pointer(0x00769430U),
            line,
            open_cfw_mram_status_pointer(structured_identity),
            argument0,
            argument1,
            argument2,
            argument3,
            argument4,
            argument5,
            argument6
        );
    }
    if (open_cfw_mram_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_status_pointer(trace_identity);

        OPEN_CFW_MRAM_STATUS_TRACE(
            event,
            identity,
            identity,
            argument0,
            argument1,
            argument2,
            argument3,
            argument4,
            argument5,
            argument6
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_show_all_records_status(void)
{
    const volatile unsigned char *record =
        OPEN_CFW_MRAM_STATUS_NVM_BASE;
    unsigned int valid_count = 0U;
    unsigned int oldest_timestamp = 0xFFFFFFFFU;
    unsigned int newest_timestamp = 0U;
    unsigned int oldest_index = 0U;
    unsigned int newest_index = 0U;
    unsigned int index;

    open_cfw_mram_status_pair0(
        0x7D3U,
        0x00751F5CU,
        0x10000000U,
        0x00731964U
    );
    open_cfw_mram_status_pair1(
        0x7D4U,
        0x0077DDF8U,
        0x10400000U,
        0x0075DE70U,
        OPEN_CFW_MRAM_STATUS_RECORD_COUNT
    );
    open_cfw_mram_status_pair1(
        0x7D5U,
        0x0075DE90U,
        0x10400000U,
        0x0073C140U,
        OPEN_CFW_MRAM_STATUS_TIMESTAMP_COUNTER
    );

    (void)OPEN_CFW_MRAM_STATUS_CACHE_INVALIDATE(
        (const void *)0,
        1U
    );

#pragma clang loop unroll(disable)
    for (
        index = 0U;
        index < OPEN_CFW_MRAM_STATUS_RECORD_COUNT;
        ++index
    ) {
        unsigned int timestamp = open_cfw_mram_status_u32(
            record + OPEN_CFW_MRAM_STATUS_TIMESTAMP_OFFSET
        );

        if (
            record[OPEN_CFW_MRAM_STATUS_VALID_OFFSET] == 0U
            || record[OPEN_CFW_MRAM_STATUS_IN_USE_OFFSET] == 0U
        ) {
            if (record[OPEN_CFW_MRAM_STATUS_IN_USE_OFFSET] == 0U) {
                open_cfw_mram_status_pair2(
                    0x7F7U,
                    0x00726F5CU,
                    0x10800000U,
                    0x007094E4U,
                    index,
                    timestamp
                );
            }
            else {
                open_cfw_mram_status_pair2(
                    0x7F4U,
                    0x00726F28U,
                    0x10800000U,
                    0x007094A4U,
                    index,
                    timestamp
                );
            }
        }
        else {
            ++valid_count;
            open_cfw_mram_status_pair3(
                0x7E4U,
                0x007004E0U,
                0x10C00000U,
                0x006EB678U,
                index,
                timestamp,
                record[OPEN_CFW_MRAM_STATUS_KEY_MASK_OFFSET]
            );
            open_cfw_mram_status_pair7(
                0x7E7U,
                0x00726EF4U,
                0x11C00000U,
                0x00709464U,
                record[5],
                record[4],
                record[3],
                record[2],
                record[1],
                record[0],
                record[OPEN_CFW_MRAM_STATUS_OWNER_OFFSET]
            );

            if (timestamp < oldest_timestamp) {
                oldest_timestamp = timestamp;
                oldest_index = index;
            }
            if (timestamp > newest_timestamp) {
                newest_timestamp = timestamp;
                newest_index = index;
            }
        }
        record += OPEN_CFW_MRAM_STATUS_RECORD_STRIDE;
    }

    open_cfw_mram_status_pair2(
        0x7FBU,
        0x0077517CU,
        0x10800000U,
        0x0075DEB0U,
        valid_count,
        OPEN_CFW_MRAM_STATUS_RECORD_COUNT
    );
    if (valid_count != 0U) {
        open_cfw_mram_status_pair2(
            0x7FDU,
            0x007478DCU,
            0x10800000U,
            0x00726F90U,
            oldest_index,
            oldest_timestamp
        );
        open_cfw_mram_status_pair2(
            0x7FEU,
            0x00747904U,
            0x10800000U,
            0x00726FC4U,
            newest_index,
            newest_timestamp
        );
    }
    open_cfw_mram_status_pair0(
        0x800U,
        0x0074792CU,
        0x10000000U,
        0x00726FF8U
    );
}
