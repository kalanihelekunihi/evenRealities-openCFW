/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Apollo protected-MRAM record allocator matched to stock entry
 * 0x0047A71C.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_allocate_uintptr;

typedef unsigned int (*open_cfw_mram_allocate_log_level_function)(void);
typedef void (*open_cfw_mram_allocate_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_allocate_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef void (*open_cfw_mram_allocate_release_function)(
    unsigned int,
    unsigned char *,
    unsigned int
);
typedef unsigned int (*open_cfw_mram_allocate_map_owner_function)(
    unsigned int
);
typedef void (*open_cfw_mram_allocate_initialize_function)(
    unsigned char *,
    const void *
);

#ifndef OPEN_CFW_MRAM_ALLOCATE_RECORDS
#define OPEN_CFW_MRAM_ALLOCATE_RECORDS \
    ((unsigned char *)(open_cfw_mram_allocate_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_COUNTER
#define OPEN_CFW_MRAM_ALLOCATE_COUNTER \
    (*(volatile unsigned int *) \
        (open_cfw_mram_allocate_uintptr)0x20074344U)
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_COUNT_TYPE
#define OPEN_CFW_MRAM_ALLOCATE_COUNT_TYPE(type) \
    open_cfw_mram_count_active_type(type)
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_OLDEST_TYPE
#define OPEN_CFW_MRAM_ALLOCATE_OLDEST_TYPE(type) \
    open_cfw_mram_oldest_active_type(type)
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_DEACTIVATE
#define OPEN_CFW_MRAM_ALLOCATE_DEACTIVATE(record) \
    open_cfw_mram_deactivate_record(record)
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_ZERO
#define OPEN_CFW_MRAM_ALLOCATE_ZERO(record, size) \
    open_cfw_lv_memory_zero((record), (size))
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_RELEASE
#define OPEN_CFW_MRAM_ALLOCATE_RELEASE(owner, record, flags) \
    (((open_cfw_mram_allocate_release_function) \
        (open_cfw_mram_allocate_uintptr)0x004D2881U)( \
            (owner), \
            (record), \
            (flags) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_MAP_OWNER
#define OPEN_CFW_MRAM_ALLOCATE_MAP_OWNER(owner) \
    (((open_cfw_mram_allocate_map_owner_function) \
        (open_cfw_mram_allocate_uintptr)0x004D2AA9U)(owner))
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_INITIALIZE
#define OPEN_CFW_MRAM_ALLOCATE_INITIALIZE(record, value) \
    (((open_cfw_mram_allocate_initialize_function) \
        (open_cfw_mram_allocate_uintptr)0x004D293DU)( \
            (record), \
            (value) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_LOG_LEVEL
#define OPEN_CFW_MRAM_ALLOCATE_LOG_LEVEL() \
    (((open_cfw_mram_allocate_log_level_function) \
        (open_cfw_mram_allocate_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_LOG
#define OPEN_CFW_MRAM_ALLOCATE_LOG(...) \
    (((open_cfw_mram_allocate_log_function) \
        (open_cfw_mram_allocate_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_ALLOCATE_TRACE
#define OPEN_CFW_MRAM_ALLOCATE_TRACE(...) \
    (((open_cfw_mram_allocate_trace_function) \
        (open_cfw_mram_allocate_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned int open_cfw_mram_count_active_type(unsigned int);
unsigned char *open_cfw_mram_oldest_active_type(unsigned int);
unsigned int open_cfw_mram_deactivate_record(unsigned char *);
void open_cfw_lv_memory_zero(void *, unsigned int);

#define OPEN_CFW_MRAM_ALLOCATE_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_ALLOCATE_RECORD_SIZE 200U

static __attribute__((always_inline)) inline const void *
open_cfw_mram_allocate_pointer(open_cfw_mram_allocate_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_allocate_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_ALLOCATE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_ALLOCATE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline const void *
open_cfw_mram_allocate_type_label(unsigned int type)
{
    if ((unsigned char)type != 0U) {
        return open_cfw_mram_allocate_pointer(0x0078CA4CU);
    }
    return open_cfw_mram_allocate_pointer(0x0078CA54U);
}

static __attribute__((always_inline)) inline void
open_cfw_mram_allocate_limit_diagnostic(
    unsigned int type,
    unsigned int argument
)
{
    const void *label = open_cfw_mram_allocate_type_label(type);

    if ((OPEN_CFW_MRAM_ALLOCATE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_ALLOCATE_LOG(
            4U,
            open_cfw_mram_allocate_pointer(0x0078A0D0U),
            open_cfw_mram_allocate_pointer(0x006D84BCU),
            open_cfw_mram_allocate_pointer(0x00784F80U),
            0x396U,
            open_cfw_mram_allocate_pointer(0x0071BFC8U),
            label,
            argument
        );
    }
    if (open_cfw_mram_allocate_trace_enabled()) {
        const void *identity =
            open_cfw_mram_allocate_pointer(0x007002C0U);

        OPEN_CFW_MRAM_ALLOCATE_TRACE(
            0x10400000U,
            identity,
            identity,
            label
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_allocate_full_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_ALLOCATE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_ALLOCATE_LOG(
            4U,
            open_cfw_mram_allocate_pointer(0x0078A0D0U),
            open_cfw_mram_allocate_pointer(0x006D84BCU),
            open_cfw_mram_allocate_pointer(0x00784F80U),
            0x3B3U,
            open_cfw_mram_allocate_pointer(0x00709264U)
        );
    }
    if (open_cfw_mram_allocate_trace_enabled()) {
        const void *identity =
            open_cfw_mram_allocate_pointer(0x006F1930U);

        OPEN_CFW_MRAM_ALLOCATE_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
unsigned char *open_cfw_mram_allocate_record(
    unsigned int owner,
    const void *initial_value,
    unsigned int type,
    unsigned int diagnostic_argument
)
{
    unsigned char *records = OPEN_CFW_MRAM_ALLOCATE_RECORDS;
    unsigned char *record = (unsigned char *)0;
    unsigned int index;
    unsigned int timestamp;

    if (OPEN_CFW_MRAM_ALLOCATE_COUNT_TYPE((unsigned char)type) >= 5U) {
        open_cfw_mram_allocate_limit_diagnostic(
            type,
            diagnostic_argument
        );
        record = OPEN_CFW_MRAM_ALLOCATE_OLDEST_TYPE(
            (unsigned char)type
        );
        if (record != (unsigned char *)0) {
            OPEN_CFW_MRAM_ALLOCATE_RELEASE(record[6U], record, 0U);
            (void)OPEN_CFW_MRAM_ALLOCATE_DEACTIVATE(record);
        }
    }

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_ALLOCATE_RECORD_COUNT; ++index) {
        unsigned char *candidate =
            records + index * OPEN_CFW_MRAM_ALLOCATE_RECORD_SIZE;

        if (candidate[0x2FU] == 0U) {
            record = candidate;
            break;
        }
    }
    if (index == OPEN_CFW_MRAM_ALLOCATE_RECORD_COUNT) {
        open_cfw_mram_allocate_full_diagnostic();
        return (unsigned char *)0;
    }

    OPEN_CFW_MRAM_ALLOCATE_ZERO(
        record,
        OPEN_CFW_MRAM_ALLOCATE_RECORD_SIZE
    );
    record[0x2FU] = 1U;
    record[6U] = (unsigned char)OPEN_CFW_MRAM_ALLOCATE_MAP_OWNER(
        (unsigned char)owner
    );
    OPEN_CFW_MRAM_ALLOCATE_INITIALIZE(record, initial_value);
    record[0xC3U] = (unsigned char)type;
    timestamp = OPEN_CFW_MRAM_ALLOCATE_COUNTER + 1U;
    OPEN_CFW_MRAM_ALLOCATE_COUNTER = timestamp;
    *(unsigned int *)(void *)(record + 0xC4U) = timestamp;
    return record;
}
