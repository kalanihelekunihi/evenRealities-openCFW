/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Apollo protected-MRAM record activation and persistence adapter
 * matched to stock entry 0x0047A49C.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_activate_uintptr;

typedef unsigned int (*open_cfw_mram_activate_verify_function)(
    const unsigned char *
);
typedef unsigned int (*open_cfw_mram_activate_log_level_function)(void);
typedef void (*open_cfw_mram_activate_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_activate_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_MRAM_ACTIVATE_COUNTER
#define OPEN_CFW_MRAM_ACTIVATE_COUNTER \
    (*(volatile unsigned int *) \
        (open_cfw_mram_activate_uintptr)0x20074344U)
#endif
#ifndef OPEN_CFW_MRAM_ACTIVATE_UPDATE
#define OPEN_CFW_MRAM_ACTIVATE_UPDATE(record) \
    open_cfw_mram_app_db_update(record)
#endif
#ifndef OPEN_CFW_MRAM_ACTIVATE_VERIFY
#define OPEN_CFW_MRAM_ACTIVATE_VERIFY(record) \
    (((open_cfw_mram_activate_verify_function) \
        (open_cfw_mram_activate_uintptr)0x0047B731U)(record))
#endif
#ifndef OPEN_CFW_MRAM_ACTIVATE_LOG_LEVEL
#define OPEN_CFW_MRAM_ACTIVATE_LOG_LEVEL() \
    (((open_cfw_mram_activate_log_level_function) \
        (open_cfw_mram_activate_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_ACTIVATE_LOG
#define OPEN_CFW_MRAM_ACTIVATE_LOG(...) \
    (((open_cfw_mram_activate_log_function) \
        (open_cfw_mram_activate_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_ACTIVATE_TRACE
#define OPEN_CFW_MRAM_ACTIVATE_TRACE(...) \
    (((open_cfw_mram_activate_trace_function) \
        (open_cfw_mram_activate_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned int open_cfw_mram_app_db_update(
    const unsigned char *
);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_activate_pointer(open_cfw_mram_activate_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_activate_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_ACTIVATE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_ACTIVATE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_activate_pair1(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int trace_identity,
    unsigned int argument
)
{
    if ((OPEN_CFW_MRAM_ACTIVATE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_ACTIVATE_LOG(
            4U,
            open_cfw_mram_activate_pointer(0x0078A0D0U),
            open_cfw_mram_activate_pointer(0x006D84BCU),
            open_cfw_mram_activate_pointer(0x0077DDE4U),
            line,
            open_cfw_mram_activate_pointer(structured_identity),
            argument
        );
    }
    if (open_cfw_mram_activate_trace_enabled()) {
        const void *identity =
            open_cfw_mram_activate_pointer(trace_identity);

        OPEN_CFW_MRAM_ACTIVATE_TRACE(
            0x10400000U,
            identity,
            identity,
            argument
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_activate_pair0(void)
{
    if ((OPEN_CFW_MRAM_ACTIVATE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_ACTIVATE_LOG(
            4U,
            open_cfw_mram_activate_pointer(0x0078A0D0U),
            open_cfw_mram_activate_pointer(0x006D84BCU),
            open_cfw_mram_activate_pointer(0x0077DDE4U),
            0x2D3U,
            open_cfw_mram_activate_pointer(0x0071BF90U)
        );
    }
    if (open_cfw_mram_activate_trace_enabled()) {
        const void *identity =
            open_cfw_mram_activate_pointer(0x0070027CU);

        OPEN_CFW_MRAM_ACTIVATE_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_activate_record(
    unsigned char *record,
    unsigned int mask
)
{
    unsigned int timestamp;
    volatile unsigned int result;

    open_cfw_mram_activate_pair1(
        0x2C5U,
        0x0071267CU,
        0x006F84D4U,
        (unsigned char)mask
    );
    record[0x30U] = 1U;
    record[0x2FU] = 1U;
    record[0x2EU] = (unsigned char)mask;
    timestamp = OPEN_CFW_MRAM_ACTIVATE_COUNTER + 1U;
    OPEN_CFW_MRAM_ACTIVATE_COUNTER = timestamp;
    *(unsigned int *)(void *)(record + 0xC4U) = timestamp;
    open_cfw_mram_activate_pair1(
        0x2CCU,
        0x006EB538U,
        0x006DF5A4U,
        (unsigned char)mask
    );

    result = OPEN_CFW_MRAM_ACTIVATE_UPDATE(record);
    (void)OPEN_CFW_MRAM_ACTIVATE_VERIFY(record);
    if (result == 1U) {
        open_cfw_mram_activate_pair0();
    }
    return mask;
}
