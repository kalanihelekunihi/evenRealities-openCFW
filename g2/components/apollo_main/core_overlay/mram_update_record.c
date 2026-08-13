/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Apollo protected-MRAM record programmer matched to stock entry
 * 0x004799A8 (_updateOneRecordToNVM).
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_update_uintptr;

typedef unsigned int (*open_cfw_mram_update_program_function)(
    unsigned int,
    const unsigned int *,
    unsigned int *,
    unsigned int
);
typedef unsigned int (*open_cfw_mram_update_yield_function)(void);
typedef unsigned int (*open_cfw_mram_update_log_level_function)(void);
typedef void (*open_cfw_mram_update_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_update_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_UPDATE_PROGRAM_KEY 0x12344321U
#define OPEN_CFW_MRAM_UPDATE_HALF_BYTES 0x80U
#define OPEN_CFW_MRAM_UPDATE_HALF_WORDS 0x20U
#define OPEN_CFW_MRAM_UPDATE_RECORD_STRIDE 0x100U

#ifndef OPEN_CFW_MRAM_UPDATE_NVM_BASE
#define OPEN_CFW_MRAM_UPDATE_NVM_BASE \
    ((unsigned char *)(open_cfw_mram_update_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_UPDATE_CACHE_INVALIDATE
#define OPEN_CFW_MRAM_UPDATE_CACHE_INVALIDATE(range, all) \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)(range), \
        (all) \
    )
#endif
#ifndef OPEN_CFW_MRAM_UPDATE_PROGRAM
#define OPEN_CFW_MRAM_UPDATE_PROGRAM(key, source, destination, count) \
    (((open_cfw_mram_update_program_function) \
        (open_cfw_mram_update_uintptr)0x004D0A2DU)( \
            (key), \
            (source), \
            (destination), \
            (count) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_UPDATE_EXCEPTION_NUMBER
static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_update_exception_number(void)
{
    unsigned int exception_number;

    __asm__ volatile(
        "mrs %0, ipsr"
        : "=r"(exception_number)
        :
        : "memory"
    );
    return exception_number;
}
#define OPEN_CFW_MRAM_UPDATE_EXCEPTION_NUMBER() \
    open_cfw_mram_update_exception_number()
#endif
#ifndef OPEN_CFW_MRAM_UPDATE_YIELD
#define OPEN_CFW_MRAM_UPDATE_YIELD() \
    (((open_cfw_mram_update_yield_function) \
        (open_cfw_mram_update_uintptr)0x004491E5U)())
#endif
#ifndef OPEN_CFW_MRAM_UPDATE_LOG_LEVEL
#define OPEN_CFW_MRAM_UPDATE_LOG_LEVEL() \
    (((open_cfw_mram_update_log_level_function) \
        (open_cfw_mram_update_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_UPDATE_LOG
#define OPEN_CFW_MRAM_UPDATE_LOG(...) \
    (((open_cfw_mram_update_log_function) \
        (open_cfw_mram_update_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_UPDATE_TRACE
#define OPEN_CFW_MRAM_UPDATE_TRACE(...) \
    (((open_cfw_mram_update_trace_function) \
        (open_cfw_mram_update_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_mram_update_pointer(open_cfw_mram_update_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_update_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_UPDATE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_UPDATE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_update_result_diagnostic(
    unsigned int first_status,
    unsigned int second_status,
    unsigned char record_index
)
{
    if ((first_status | second_status) != 0U) {
        if ((OPEN_CFW_MRAM_UPDATE_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_MRAM_UPDATE_LOG(
                1U,
                open_cfw_mram_update_pointer(0x0078A0D0U),
                open_cfw_mram_update_pointer(0x006D84BCU),
                open_cfw_mram_update_pointer(0x00775104U),
                0x1B0U,
                open_cfw_mram_update_pointer(0x007090E4U),
                first_status,
                second_status
            );
        }
        if (open_cfw_mram_update_trace_enabled()) {
            const void *identity =
                open_cfw_mram_update_pointer(0x006F17B4U);

            OPEN_CFW_MRAM_UPDATE_TRACE(
                0x04800000U,
                identity,
                identity,
                first_status,
                second_status
            );
        }
        return;
    }

    if ((OPEN_CFW_MRAM_UPDATE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_UPDATE_LOG(
            4U,
            open_cfw_mram_update_pointer(0x0078A0D0U),
            open_cfw_mram_update_pointer(0x006D84BCU),
            open_cfw_mram_update_pointer(0x00775104U),
            0x1B3U,
            open_cfw_mram_update_pointer(0x006E622CU),
            0x40U,
            0x20U,
            (unsigned int)record_index
        );
    }
    if (open_cfw_mram_update_trace_enabled()) {
        const void *identity =
            open_cfw_mram_update_pointer(0x006DF548U);

        OPEN_CFW_MRAM_UPDATE_TRACE(
            0x10C00000U,
            identity,
            identity,
            0x40U,
            0x20U,
            (unsigned int)record_index
        );
    }
}

/*
 * The reviewed MRAM HAL accepts at most 0x20 words per transaction here.
 * Preserve the stock split and its thread-mode-only yield between halves.
 */
__attribute__((used, noinline))
void open_cfw_mram_update_one_record(
    const unsigned char *record,
    unsigned char record_index
)
{
    unsigned char *destination =
        OPEN_CFW_MRAM_UPDATE_NVM_BASE
        + (unsigned int)record_index
            * OPEN_CFW_MRAM_UPDATE_RECORD_STRIDE;
    unsigned int first_status;
    unsigned int second_status;

    (void)OPEN_CFW_MRAM_UPDATE_CACHE_INVALIDATE(0U, 1U);
    first_status = OPEN_CFW_MRAM_UPDATE_PROGRAM(
        OPEN_CFW_MRAM_UPDATE_PROGRAM_KEY,
        (const unsigned int *)(const void *)record,
        (unsigned int *)(void *)destination,
        OPEN_CFW_MRAM_UPDATE_HALF_WORDS
    );
    if (OPEN_CFW_MRAM_UPDATE_EXCEPTION_NUMBER() == 0U) {
        (void)OPEN_CFW_MRAM_UPDATE_YIELD();
    }
    second_status = OPEN_CFW_MRAM_UPDATE_PROGRAM(
        OPEN_CFW_MRAM_UPDATE_PROGRAM_KEY,
        (const unsigned int *)(const void *)(
            record + OPEN_CFW_MRAM_UPDATE_HALF_BYTES
        ),
        (unsigned int *)(void *)(
            destination + OPEN_CFW_MRAM_UPDATE_HALF_BYTES
        ),
        OPEN_CFW_MRAM_UPDATE_HALF_WORDS
    );

    open_cfw_mram_update_result_diagnostic(
        first_status,
        second_status,
        record_index
    );
}
