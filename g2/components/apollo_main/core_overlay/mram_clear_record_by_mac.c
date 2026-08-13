/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio application-database record clearing wrapper matched to
 * stock AppDbClearRecordByMacAddr at 0x0047B59C.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_clear_uintptr;

typedef void (*open_cfw_mram_clear_release_function)(
    unsigned int,
    unsigned char *,
    unsigned int
);
typedef unsigned int (*open_cfw_mram_clear_log_level_function)(void);
typedef void (*open_cfw_mram_clear_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_clear_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_MRAM_CLEAR_FIND
#define OPEN_CFW_MRAM_CLEAR_FIND(owner, address) \
    open_cfw_mram_find_by_address((owner), (address))
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_DEACTIVATE
#define OPEN_CFW_MRAM_CLEAR_DEACTIVATE(record) \
    open_cfw_mram_deactivate_record(record)
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_RELEASE
#define OPEN_CFW_MRAM_CLEAR_RELEASE(owner, record, flags) \
    (((open_cfw_mram_clear_release_function) \
        (open_cfw_mram_clear_uintptr)0x004D2881U)( \
            (owner), \
            (record), \
            (flags) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_LOG_LEVEL
#define OPEN_CFW_MRAM_CLEAR_LOG_LEVEL() \
    (((open_cfw_mram_clear_log_level_function) \
        (open_cfw_mram_clear_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_LOG
#define OPEN_CFW_MRAM_CLEAR_LOG(...) \
    (((open_cfw_mram_clear_log_function) \
        (open_cfw_mram_clear_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_TRACE
#define OPEN_CFW_MRAM_CLEAR_TRACE(...) \
    (((open_cfw_mram_clear_trace_function) \
        (open_cfw_mram_clear_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned char *open_cfw_mram_find_by_address(
    unsigned int,
    const unsigned char *
);
unsigned int open_cfw_mram_deactivate_record(unsigned char *);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_clear_pointer(open_cfw_mram_clear_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_clear_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_CLEAR_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_CLEAR_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_clear_diagnostic(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int trace_event,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_MRAM_CLEAR_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_CLEAR_LOG(
            severity,
            open_cfw_mram_clear_pointer(0x0078A0D0U),
            open_cfw_mram_clear_pointer(0x006D84BCU),
            open_cfw_mram_clear_pointer(0x00769414U),
            line,
            open_cfw_mram_clear_pointer(structured_identity)
        );
    }
    if (open_cfw_mram_clear_trace_enabled()) {
        const void *identity =
            open_cfw_mram_clear_pointer(trace_identity);

        OPEN_CFW_MRAM_CLEAR_TRACE(
            trace_event,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_clear_record_by_mac_address(
    unsigned int owner,
    const unsigned char *address
)
{
    unsigned char *record;

    if (address == (const unsigned char *)0) {
        open_cfw_mram_clear_diagnostic(
            1U,
            0x74CU,
            0x0071C0E0U,
            0x04000000U,
            0x007003D0U
        );
        return 0U;
    }

    record = OPEN_CFW_MRAM_CLEAR_FIND((unsigned char)owner, address);
    if (record == (unsigned char *)0) {
        open_cfw_mram_clear_diagnostic(
            4U,
            0x765U,
            0x00726E58U,
            0x10000000U,
            0x00709364U
        );
        return 0U;
    }

    open_cfw_mram_clear_diagnostic(
        4U,
        0x755U,
        0x006F85ACU,
        0x10000000U,
        0x006E6328U
    );
    (void)OPEN_CFW_MRAM_CLEAR_DEACTIVATE(record);
    OPEN_CFW_MRAM_CLEAR_RELEASE(record[6U], record, 0U);
    open_cfw_mram_clear_diagnostic(
        4U,
        0x760U,
        0x00700414U,
        0x10000000U,
        0x006EB628U
    );
    return 1U;
}
