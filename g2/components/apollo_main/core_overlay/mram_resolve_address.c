/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio application-database address resolver matched to stock
 * AppDbResolveAndConnectByAddr at 0x0047A8C4.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_resolve_uintptr;

typedef unsigned int (*open_cfw_mram_resolve_log_level_function)(void);
typedef void (*open_cfw_mram_resolve_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_resolve_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef unsigned int (*open_cfw_mram_resolve_map_owner_function)(
    unsigned int
);
typedef unsigned int (*open_cfw_mram_resolve_compare_function)(
    const void *,
    const void *
);
typedef void (*open_cfw_mram_resolve_queue_function)(
    const unsigned char *,
    const unsigned char *,
    unsigned int
);

#ifndef OPEN_CFW_MRAM_RESOLVE_RECORDS
#define OPEN_CFW_MRAM_RESOLVE_RECORDS \
    ((unsigned char *)(open_cfw_mram_resolve_uintptr)0x20067A30U)
#endif
#ifndef OPEN_CFW_MRAM_RESOLVE_MAP_OWNER
#define OPEN_CFW_MRAM_RESOLVE_MAP_OWNER(owner) \
    (((open_cfw_mram_resolve_map_owner_function) \
        (open_cfw_mram_resolve_uintptr)0x004D2AA9U)(owner))
#endif
#ifndef OPEN_CFW_MRAM_RESOLVE_COMPARE
#define OPEN_CFW_MRAM_RESOLVE_COMPARE(record, address) \
    (((open_cfw_mram_resolve_compare_function) \
        (open_cfw_mram_resolve_uintptr)0x004D294BU)( \
            (record), \
            (address) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_RESOLVE_QUEUE
#define OPEN_CFW_MRAM_RESOLVE_QUEUE(address, irk, index) \
    (((open_cfw_mram_resolve_queue_function) \
        (open_cfw_mram_resolve_uintptr)0x004D27F7U)( \
            (address), \
            (irk), \
            (index) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL
#define OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() \
    (((open_cfw_mram_resolve_log_level_function) \
        (open_cfw_mram_resolve_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_RESOLVE_LOG
#define OPEN_CFW_MRAM_RESOLVE_LOG(...) \
    (((open_cfw_mram_resolve_log_function) \
        (open_cfw_mram_resolve_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_RESOLVE_TRACE
#define OPEN_CFW_MRAM_RESOLVE_TRACE(...) \
    (((open_cfw_mram_resolve_trace_function) \
        (open_cfw_mram_resolve_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

#define OPEN_CFW_MRAM_RESOLVE_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_RESOLVE_RECORD_SIZE 200U

static __attribute__((always_inline)) inline const void *
open_cfw_mram_resolve_pointer(open_cfw_mram_resolve_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_resolve_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolve_null_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVE_LOG(
            1U,
            open_cfw_mram_resolve_pointer(0x0078A0D0U),
            open_cfw_mram_resolve_pointer(0x006D84BCU),
            open_cfw_mram_resolve_pointer(0x0075DE50U),
            0x3E6U,
            open_cfw_mram_resolve_pointer(0x007126B8U)
        );
    }
    if (open_cfw_mram_resolve_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolve_pointer(0x006F851CU);

        OPEN_CFW_MRAM_RESOLVE_TRACE(
            0x04000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolve_random_diagnostic(const unsigned char *address)
{
    if ((OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVE_LOG(
            4U,
            open_cfw_mram_resolve_pointer(0x0078A0D0U),
            open_cfw_mram_resolve_pointer(0x006D84BCU),
            open_cfw_mram_resolve_pointer(0x0075DE50U),
            0x3EEU,
            open_cfw_mram_resolve_pointer(0x006DC454U),
            address[5U],
            address[4U],
            address[3U],
            address[2U],
            address[1U],
            address[0U]
        );
    }
    if (open_cfw_mram_resolve_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolve_pointer(0x006A6EE4U);

        OPEN_CFW_MRAM_RESOLVE_TRACE(
            0x11800000U,
            identity,
            identity,
            address[5U],
            address[4U],
            address[3U],
            address[2U],
            address[1U],
            address[0U]
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolve_try_diagnostic(unsigned int index)
{
    if ((OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVE_LOG(
            4U,
            open_cfw_mram_resolve_pointer(0x0078A0D0U),
            open_cfw_mram_resolve_pointer(0x006D84BCU),
            open_cfw_mram_resolve_pointer(0x0075DE50U),
            0x3F8U,
            open_cfw_mram_resolve_pointer(0x006EB588U),
            (unsigned char)index
        );
    }
    if (open_cfw_mram_resolve_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolve_pointer(0x006DF600U);

        OPEN_CFW_MRAM_RESOLVE_TRACE(
            0x10400000U,
            identity,
            identity,
            (unsigned char)index
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolve_no_irk_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVE_LOG(
            2U,
            open_cfw_mram_resolve_pointer(0x0078A0D0U),
            open_cfw_mram_resolve_pointer(0x006D84BCU),
            open_cfw_mram_resolve_pointer(0x0075DE50U),
            0x404U,
            open_cfw_mram_resolve_pointer(0x006F197CU)
        );
    }
    if (open_cfw_mram_resolve_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolve_pointer(0x006E2490U);

        OPEN_CFW_MRAM_RESOLVE_TRACE(
            0x08000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolve_match_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVE_LOG(
            4U,
            open_cfw_mram_resolve_pointer(0x0078A0D0U),
            open_cfw_mram_resolve_pointer(0x006D84BCU),
            open_cfw_mram_resolve_pointer(0x0075DE50U),
            0x419U,
            open_cfw_mram_resolve_pointer(0x006F19C8U)
        );
    }
    if (open_cfw_mram_resolve_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolve_pointer(0x006E24E8U);

        OPEN_CFW_MRAM_RESOLVE_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_resolve_no_match_diagnostic(void)
{
    if ((OPEN_CFW_MRAM_RESOLVE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RESOLVE_LOG(
            2U,
            open_cfw_mram_resolve_pointer(0x0078A0D0U),
            open_cfw_mram_resolve_pointer(0x006D84BCU),
            open_cfw_mram_resolve_pointer(0x0075DE50U),
            0x41FU,
            open_cfw_mram_resolve_pointer(0x0071C000U)
        );
    }
    if (open_cfw_mram_resolve_trace_enabled()) {
        const void *identity =
            open_cfw_mram_resolve_pointer(0x007092A4U);

        OPEN_CFW_MRAM_RESOLVE_TRACE(
            0x08000000U,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_resolve_and_connect_by_address(
    unsigned int owner,
    const unsigned char *address
)
{
    unsigned char *records = OPEN_CFW_MRAM_RESOLVE_RECORDS;
    unsigned int index;

    if (address == (const unsigned char *)0) {
        open_cfw_mram_resolve_null_diagnostic();
        return 0U;
    }

    if (
        (unsigned char)owner == 1U
        && (address[5U] & 0xC0U) == 0x40U
    ) {
        open_cfw_mram_resolve_random_diagnostic(address);
#pragma clang loop unroll(disable)
        for (
            index = 0U;
            index < OPEN_CFW_MRAM_RESOLVE_RECORD_COUNT;
            ++index
        ) {
            unsigned char *record =
                records + index * OPEN_CFW_MRAM_RESOLVE_RECORD_SIZE;

            if (
                record[0x2FU] != 0U
                && record[0x30U] != 0U
                && (record[0x2EU] & 4U) != 0U
            ) {
                open_cfw_mram_resolve_try_diagnostic(index);
                OPEN_CFW_MRAM_RESOLVE_QUEUE(
                    address,
                    record + 7U,
                    (unsigned short)index
                );
                return 1U;
            }
        }
        open_cfw_mram_resolve_no_irk_diagnostic();
        return 0U;
    }

    owner = (unsigned char)OPEN_CFW_MRAM_RESOLVE_MAP_OWNER(
        (unsigned char)owner
    );
#pragma clang loop unroll(disable)
    for (
        index = 0U;
        index < OPEN_CFW_MRAM_RESOLVE_RECORD_COUNT;
        ++index
    ) {
        unsigned char *record =
            records + index * OPEN_CFW_MRAM_RESOLVE_RECORD_SIZE;

        if (
            record[0x2FU] != 0U
            && record[0x30U] != 0U
            && record[6U] == (unsigned char)owner
            && OPEN_CFW_MRAM_RESOLVE_COMPARE(record, address) != 0U
        ) {
            open_cfw_mram_resolve_match_diagnostic();
            return 1U;
        }
    }

    open_cfw_mram_resolve_no_match_diagnostic();
    return 0U;
}
