/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Apollo MRAM persistence helpers matched to stock entries
 * 0x004787A4 and 0x00478860.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_uintptr;

typedef unsigned int (*open_cfw_mram_program_function)(
    unsigned int,
    const unsigned int *,
    unsigned int *,
    unsigned int
);
typedef unsigned int (*open_cfw_mram_log_level_function)(void);
typedef void (*open_cfw_mram_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef void (*open_cfw_mram_hex_dump_function)(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

#define OPEN_CFW_MRAM_PROGRAM_KEY 0x12344321U

#ifndef OPEN_CFW_MRAM_ZERO_SIZE
#define OPEN_CFW_MRAM_ZERO_SIZE \
    (*(const volatile unsigned short *)0x20004524U)
#endif
#ifndef OPEN_CFW_MRAM_ZERO_BUFFER
#define OPEN_CFW_MRAM_ZERO_BUFFER \
    ((volatile unsigned char *) \
        (open_cfw_mram_uintptr)0x200636A0U)
#endif
#ifndef OPEN_CFW_MRAM_ZERO_DESTINATION
#define OPEN_CFW_MRAM_ZERO_DESTINATION \
    ((unsigned int *)(open_cfw_mram_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_FLAG_RECORD
#define OPEN_CFW_MRAM_FLAG_RECORD \
    ((volatile unsigned int *)(open_cfw_mram_uintptr)0x007FE000U)
#endif
#ifndef OPEN_CFW_MRAM_FLAG_TEMPLATE
#define OPEN_CFW_MRAM_FLAG_TEMPLATE \
    ((const volatile unsigned int *) \
        (open_cfw_mram_uintptr)0x00784ED0U)
#endif
#ifndef OPEN_CFW_MRAM_PROGRAM
#define OPEN_CFW_MRAM_PROGRAM(key, source, destination, count) \
    (((open_cfw_mram_program_function) \
        (open_cfw_mram_uintptr)0x004D0A2DU)( \
            (key), (source), (destination), (count) \
        ))
#endif
#ifndef OPEN_CFW_MRAM_LOG_LEVEL
#define OPEN_CFW_MRAM_LOG_LEVEL() \
    (((open_cfw_mram_log_level_function) \
        (open_cfw_mram_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_LOG
#define OPEN_CFW_MRAM_LOG(...) \
    (((open_cfw_mram_log_function) \
        (open_cfw_mram_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_TRACE
#define OPEN_CFW_MRAM_TRACE(...) \
    (((open_cfw_mram_trace_function) \
        (open_cfw_mram_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_HEX_DUMP
#define OPEN_CFW_MRAM_HEX_DUMP(...) \
    (((open_cfw_mram_hex_dump_function) \
        (open_cfw_mram_uintptr)0x0043DACDU)(__VA_ARGS__))
#endif

unsigned int open_cfw_lv_irq_disable(void);

#ifndef OPEN_CFW_MRAM_CACHE_INVALIDATE
unsigned int open_cfw_cache_dcache_invalidate(
    const open_cfw_cache_range *,
    unsigned int
);
#define OPEN_CFW_MRAM_CACHE_INVALIDATE() \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)0, \
        1U \
    )
#endif
#ifndef OPEN_CFW_MRAM_IRQ_DISABLE
#define OPEN_CFW_MRAM_IRQ_DISABLE() open_cfw_lv_irq_disable()
#endif
#ifndef OPEN_CFW_MRAM_PRIMASK_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_mram_primask_restore(unsigned int value)
{
    __asm__ volatile(
        "msr primask, %0"
        :
        : "r"(value)
        : "memory"
    );
}
#define OPEN_CFW_MRAM_PRIMASK_RESTORE(value) \
    open_cfw_mram_primask_restore(value)
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_mram_pointer(unsigned int address)
{
    return (const void *)(open_cfw_mram_uintptr)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_program_result_diagnostic(
    unsigned int status,
    unsigned int success_line,
    unsigned int success_identity
)
{
    unsigned int severity = status == 0U ? 4U : 1U;
    unsigned int line = status == 0U ? success_line : 0x8EU;
    unsigned int structured_identity =
        status == 0U ? success_identity : 0x0073C038U;
    unsigned int event =
        status == 0U ? 0x10400000U : 0x04400000U;
    unsigned int trace_identity =
        status == 0U ? 0x0071BEE8U : 0x00726CB8U;

    if ((OPEN_CFW_MRAM_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOG(
            severity,
            open_cfw_mram_pointer(0x0078A0D0U),
            open_cfw_mram_pointer(0x006D84BCU),
            open_cfw_mram_pointer(0x0077502CU),
            line,
            open_cfw_mram_pointer(structured_identity),
            status
        );
    }
    if (open_cfw_mram_trace_enabled()) {
        const void *identity =
            open_cfw_mram_pointer(trace_identity);

        OPEN_CFW_MRAM_TRACE(
            event,
            identity,
            identity,
            status
        );
    }
}

/*
 * Zero the configured staging buffer and program it into the final 4 KiB
 * Apollo MRAM page. The configured size is truncated to whole words exactly
 * as in the stock body.
 */
__attribute__((used, noinline))
void open_cfw_mram_program_zero_region(void)
{
    volatile unsigned char *buffer = OPEN_CFW_MRAM_ZERO_BUFFER;
    unsigned int size = OPEN_CFW_MRAM_ZERO_SIZE;
    unsigned int primask;
    unsigned int status;
    unsigned int index;

    (void)OPEN_CFW_MRAM_CACHE_INVALIDATE();
    for (index = 0U; index < size; ++index) {
        buffer[index] = 0U;
    }

    primask = OPEN_CFW_MRAM_IRQ_DISABLE();
    status = OPEN_CFW_MRAM_PROGRAM(
        OPEN_CFW_MRAM_PROGRAM_KEY,
        (const unsigned int *)(const void *)buffer,
        OPEN_CFW_MRAM_ZERO_DESTINATION,
        size >> 2U
    );
    OPEN_CFW_MRAM_PRIMASK_RESTORE(primask);
    open_cfw_mram_program_result_diagnostic(
        status,
        0x90U,
        0x0073C064U
    );
}

static __attribute__((always_inline)) inline void
open_cfw_mram_flag_state_diagnostic(
    unsigned int current,
    unsigned int requested
)
{
    if ((OPEN_CFW_MRAM_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOG(
            4U,
            open_cfw_mram_pointer(0x0078A0D0U),
            open_cfw_mram_pointer(0x006D84BCU),
            open_cfw_mram_pointer(0x0075DD50U),
            0x98U,
            open_cfw_mram_pointer(0x0073C090U),
            current,
            requested
        );
    }
    if (open_cfw_mram_trace_enabled()) {
        const void *identity =
            open_cfw_mram_pointer(0x0071BF20U);

        OPEN_CFW_MRAM_TRACE(
            0x10800000U,
            identity,
            identity,
            current,
            requested
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_flag_change_diagnostic(unsigned int requested)
{
    if ((OPEN_CFW_MRAM_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOG(
            4U,
            open_cfw_mram_pointer(0x0078A0D0U),
            open_cfw_mram_pointer(0x006D84BCU),
            open_cfw_mram_pointer(0x0075DD50U),
            0x9FU,
            open_cfw_mram_pointer(0x00751D88U),
            OPEN_CFW_MRAM_FLAG_RECORD,
            requested
        );
    }
    if (open_cfw_mram_trace_enabled()) {
        const void *identity =
            open_cfw_mram_pointer(0x007317E4U);

        OPEN_CFW_MRAM_TRACE(
            0x10800000U,
            identity,
            identity,
            OPEN_CFW_MRAM_FLAG_RECORD,
            requested
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_flag_error_diagnostic(unsigned int status)
{
    if ((OPEN_CFW_MRAM_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_LOG(
            1U,
            open_cfw_mram_pointer(0x0078A0D0U),
            open_cfw_mram_pointer(0x006D84BCU),
            open_cfw_mram_pointer(0x0075DD50U),
            0xA9U,
            open_cfw_mram_pointer(0x0073C038U),
            status
        );
    }
    if (open_cfw_mram_trace_enabled()) {
        const void *identity =
            open_cfw_mram_pointer(0x00726CB8U);

        OPEN_CFW_MRAM_TRACE(
            0x04400000U,
            identity,
            identity,
            status
        );
    }
}

/*
 * Idempotently program the four-word bootloader update selector in the
 * protected MRAM flag record.
 */
__attribute__((used, noinline))
void open_cfw_mram_update_flag_set(unsigned int requested)
{
    volatile unsigned int *flag = OPEN_CFW_MRAM_FLAG_RECORD;
    const volatile unsigned int *template = OPEN_CFW_MRAM_FLAG_TEMPLATE;
    unsigned int record[4];
    unsigned int current = flag[0];
    unsigned int primask;
    unsigned int status;
    unsigned int index;

    open_cfw_mram_flag_state_diagnostic(current, requested);
    OPEN_CFW_MRAM_HEX_DUMP(
        open_cfw_mram_pointer(0x0078A0DCU),
        0x10U,
        (const void *)flag,
        0x20U
    );
    if (requested == current) {
        return;
    }

    for (index = 0U; index < 4U; ++index) {
        record[index] = template[index];
    }
    record[0] = requested;
    open_cfw_mram_flag_change_diagnostic(requested);

    primask = OPEN_CFW_MRAM_IRQ_DISABLE();
    status = OPEN_CFW_MRAM_PROGRAM(
        OPEN_CFW_MRAM_PROGRAM_KEY,
        record,
        (unsigned int *)(open_cfw_mram_uintptr)flag,
        4U
    );
    OPEN_CFW_MRAM_PRIMASK_RESTORE(primask);
    if (status != 0U) {
        open_cfw_mram_flag_error_diagnostic(status);
    }
}
