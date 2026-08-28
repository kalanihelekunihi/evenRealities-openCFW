/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio application-database resolving-list reload wrapper matched
 * to stock AppDbReloadResolvingList at 0x0047B4D4.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_reload_uintptr;

typedef void (*open_cfw_mram_reload_request_function)(void);
typedef unsigned int (*open_cfw_mram_reload_log_level_function)(void);
typedef void (*open_cfw_mram_reload_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_reload_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_MRAM_RELOAD_REQUEST
#define OPEN_CFW_MRAM_RELOAD_REQUEST() \
    (((open_cfw_mram_reload_request_function) \
        (open_cfw_mram_reload_uintptr)0x004D28B1U)())
#endif
#ifndef OPEN_CFW_MRAM_RELOAD_SYNC
#define OPEN_CFW_MRAM_RELOAD_SYNC() \
    open_cfw_mram_sync_records()
#endif
#ifndef OPEN_CFW_MRAM_RELOAD_LOG_LEVEL
#define OPEN_CFW_MRAM_RELOAD_LOG_LEVEL() \
    (((open_cfw_mram_reload_log_level_function) \
        (open_cfw_mram_reload_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_RELOAD_LOG
#define OPEN_CFW_MRAM_RELOAD_LOG(...) \
    (((open_cfw_mram_reload_log_function) \
        (open_cfw_mram_reload_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_RELOAD_TRACE
#define OPEN_CFW_MRAM_RELOAD_TRACE(...) \
    (((open_cfw_mram_reload_trace_function) \
        (open_cfw_mram_reload_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

void open_cfw_mram_sync_records(void);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_reload_pointer(open_cfw_mram_reload_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_reload_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_RELOAD_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_RELOAD_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_reload_diagnostic(
    unsigned int line,
    unsigned int structured_identity,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_MRAM_RELOAD_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_RELOAD_LOG(
            4U,
            open_cfw_mram_reload_pointer(0x0078A0D0U),
            open_cfw_mram_reload_pointer(0x006D84BCU),
            open_cfw_mram_reload_pointer(0x007693F8U),
            line,
            open_cfw_mram_reload_pointer(structured_identity)
        );
    }
    if (open_cfw_mram_reload_trace_enabled()) {
        const void *identity =
            open_cfw_mram_reload_pointer(trace_identity);

        OPEN_CFW_MRAM_RELOAD_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_reload_resolving_list(void)
{
    open_cfw_mram_reload_diagnostic(
        0x706U,
        0x0071276CU,
        0x006F8564U
    );
    OPEN_CFW_MRAM_RELOAD_REQUEST();
    OPEN_CFW_MRAM_RELOAD_SYNC();
    open_cfw_mram_reload_diagnostic(
        0x70EU,
        0x00726E24U,
        0x00709324U
    );
}
