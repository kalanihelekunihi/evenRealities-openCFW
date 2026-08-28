/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio persistent-record reporter matched to stock
 * AppDbShowNvmStatus at 0x0047C2BC.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_nvm_status_uintptr;

typedef unsigned int (*open_cfw_mram_nvm_status_log_level_function)(void);
typedef void (*open_cfw_mram_nvm_status_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_nvm_status_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_NVM_STATUS_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_NVM_STATUS_RECORD_STRIDE 0x100U
#define OPEN_CFW_MRAM_NVM_STATUS_KEY_MASK_OFFSET 0x2EU
#define OPEN_CFW_MRAM_NVM_STATUS_IN_USE_OFFSET 0x2FU
#define OPEN_CFW_MRAM_NVM_STATUS_VALID_OFFSET 0x30U

#ifndef OPEN_CFW_MRAM_NVM_STATUS_BASE
#define OPEN_CFW_MRAM_NVM_STATUS_BASE \
    ((const volatile unsigned char *) \
        (open_cfw_mram_nvm_status_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_NVM_STATUS_CACHE_INVALIDATE
#define OPEN_CFW_MRAM_NVM_STATUS_CACHE_INVALIDATE(range, clean) \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)(range), \
        (clean) \
    )
#endif
#ifndef OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL
#define OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL() \
    (((open_cfw_mram_nvm_status_log_level_function) \
        (open_cfw_mram_nvm_status_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_NVM_STATUS_LOG
#define OPEN_CFW_MRAM_NVM_STATUS_LOG(...) \
    (((open_cfw_mram_nvm_status_log_function) \
        (open_cfw_mram_nvm_status_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_NVM_STATUS_TRACE
#define OPEN_CFW_MRAM_NVM_STATUS_TRACE(...) \
    (((open_cfw_mram_nvm_status_trace_function) \
        (open_cfw_mram_nvm_status_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned int open_cfw_cache_dcache_invalidate(
    const open_cfw_cache_range *,
    unsigned int
);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_nvm_status_pointer(
    open_cfw_mram_nvm_status_uintptr address
)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_nvm_status_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_nvm_status_word(
    const volatile unsigned char *record
)
{
    return (unsigned int)record[0]
        | ((unsigned int)record[1] << 8U)
        | ((unsigned int)record[2] << 16U)
        | ((unsigned int)record[3] << 24U);
}

static __attribute__((always_inline)) inline void
open_cfw_mram_nvm_status_boundary(
    unsigned int line,
    open_cfw_mram_nvm_status_uintptr structured_identity,
    open_cfw_mram_nvm_status_uintptr trace_identity
)
{
    if ((OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_NVM_STATUS_LOG(
            4U,
            open_cfw_mram_nvm_status_pointer(0x0078A0D0U),
            open_cfw_mram_nvm_status_pointer(0x006D84BCU),
            open_cfw_mram_nvm_status_pointer(0x0077DE0CU),
            line,
            open_cfw_mram_nvm_status_pointer(structured_identity)
        );
    }
    if (open_cfw_mram_nvm_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_nvm_status_pointer(trace_identity);

        OPEN_CFW_MRAM_NVM_STATUS_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_nvm_status_record(
    unsigned int index,
    const volatile unsigned char *record
)
{
    unsigned int key_mask =
        record[OPEN_CFW_MRAM_NVM_STATUS_KEY_MASK_OFFSET];
    unsigned int byte_5 = record[5];
    unsigned int byte_4 = record[4];
    unsigned int byte_3 = record[3];
    unsigned int byte_2 = record[2];
    unsigned int byte_1 = record[1];
    unsigned int byte_0 = record[0];

    if ((OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_NVM_STATUS_LOG(
            4U,
            open_cfw_mram_nvm_status_pointer(0x0078A0D0U),
            open_cfw_mram_nvm_status_pointer(0x006D84BCU),
            open_cfw_mram_nvm_status_pointer(0x0077DE0CU),
            0x85BU,
            open_cfw_mram_nvm_status_pointer(0x006EB6C8U),
            (open_cfw_mram_nvm_status_uintptr)index,
            (open_cfw_mram_nvm_status_uintptr)key_mask,
            (open_cfw_mram_nvm_status_uintptr)byte_5,
            (open_cfw_mram_nvm_status_uintptr)byte_4,
            (open_cfw_mram_nvm_status_uintptr)byte_3,
            (open_cfw_mram_nvm_status_uintptr)byte_2,
            (open_cfw_mram_nvm_status_uintptr)byte_1,
            (open_cfw_mram_nvm_status_uintptr)byte_0
        );
    }
    if (open_cfw_mram_nvm_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_nvm_status_pointer(0x006E2598U);

        OPEN_CFW_MRAM_NVM_STATUS_TRACE(
            0x12000000U,
            identity,
            identity,
            (open_cfw_mram_nvm_status_uintptr)index,
            (open_cfw_mram_nvm_status_uintptr)key_mask,
            (open_cfw_mram_nvm_status_uintptr)byte_5,
            (open_cfw_mram_nvm_status_uintptr)byte_4,
            (open_cfw_mram_nvm_status_uintptr)byte_3,
            (open_cfw_mram_nvm_status_uintptr)byte_2,
            (open_cfw_mram_nvm_status_uintptr)byte_1,
            (open_cfw_mram_nvm_status_uintptr)byte_0
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_nvm_status_summary(
    unsigned int valid_count,
    unsigned int total_count
)
{
    if ((OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_NVM_STATUS_LOG(
            4U,
            open_cfw_mram_nvm_status_pointer(0x0078A0D0U),
            open_cfw_mram_nvm_status_pointer(0x006D84BCU),
            open_cfw_mram_nvm_status_pointer(0x0077DE0CU),
            0x860U,
            open_cfw_mram_nvm_status_pointer(0x0075DED0U),
            (open_cfw_mram_nvm_status_uintptr)valid_count,
            (open_cfw_mram_nvm_status_uintptr)total_count
        );
    }
    if (open_cfw_mram_nvm_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_nvm_status_pointer(0x0073C16CU);

        OPEN_CFW_MRAM_NVM_STATUS_TRACE(
            0x10800000U,
            identity,
            identity,
            (open_cfw_mram_nvm_status_uintptr)valid_count,
            (open_cfw_mram_nvm_status_uintptr)total_count
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_nvm_status_address(void)
{
    open_cfw_mram_nvm_status_uintptr address = 0x007FF000U;

    if ((OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_NVM_STATUS_LOG(
            4U,
            open_cfw_mram_nvm_status_pointer(0x0078A0D0U),
            open_cfw_mram_nvm_status_pointer(0x006D84BCU),
            open_cfw_mram_nvm_status_pointer(0x0077DE0CU),
            0x861U,
            open_cfw_mram_nvm_status_pointer(0x0077DE20U),
            address
        );
    }
    if (open_cfw_mram_nvm_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_nvm_status_pointer(0x0075DEF0U);

        OPEN_CFW_MRAM_NVM_STATUS_TRACE(
            0x10400000U,
            identity,
            identity,
            address
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_nvm_status_geometry(void)
{
    if ((OPEN_CFW_MRAM_NVM_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_NVM_STATUS_LOG(
            4U,
            open_cfw_mram_nvm_status_pointer(0x0078A0D0U),
            open_cfw_mram_nvm_status_pointer(0x006D84BCU),
            open_cfw_mram_nvm_status_pointer(0x0077DE0CU),
            0x862U,
            open_cfw_mram_nvm_status_pointer(0x00751F80U),
            (open_cfw_mram_nvm_status_uintptr)0x100U,
            (open_cfw_mram_nvm_status_uintptr)0x40U
        );
    }
    if (open_cfw_mram_nvm_status_trace_enabled()) {
        const void *identity =
            open_cfw_mram_nvm_status_pointer(0x0073C198U);

        OPEN_CFW_MRAM_NVM_STATUS_TRACE(
            0x10800000U,
            identity,
            identity,
            (open_cfw_mram_nvm_status_uintptr)0x100U,
            (open_cfw_mram_nvm_status_uintptr)0x40U
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_show_nvm_status(void)
{
    const volatile unsigned char *record = OPEN_CFW_MRAM_NVM_STATUS_BASE;
    unsigned int valid_count = 0U;
    unsigned int index;

    open_cfw_mram_nvm_status_boundary(
        0x84BU,
        0x00769468U,
        0x00747954U
    );
    (void)OPEN_CFW_MRAM_NVM_STATUS_CACHE_INVALIDATE(
        (const open_cfw_cache_range *)0,
        1U
    );

    for (index = 0U; index < OPEN_CFW_MRAM_NVM_STATUS_RECORD_COUNT; ++index) {
        unsigned int identifier = open_cfw_mram_nvm_status_word(record);

        if (
            record[OPEN_CFW_MRAM_NVM_STATUS_IN_USE_OFFSET] != 0U
            && record[OPEN_CFW_MRAM_NVM_STATUS_VALID_OFFSET] != 0U
            && identifier != 0xFFFFFFFFU
            && identifier != 0U
        ) {
            ++valid_count;
            open_cfw_mram_nvm_status_record(index, record);
        }
        record += OPEN_CFW_MRAM_NVM_STATUS_RECORD_STRIDE;
    }

    open_cfw_mram_nvm_status_summary(
        valid_count,
        OPEN_CFW_MRAM_NVM_STATUS_RECORD_COUNT
    );
    open_cfw_mram_nvm_status_address();
    open_cfw_mram_nvm_status_geometry();
    open_cfw_mram_nvm_status_boundary(
        0x863U,
        0x0075DF10U,
        0x0073C1C4U
    );
}
