/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio protected-MRAM write verifier matched to stock
 * AppDbVerifyMramWrite at 0x0047B730.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_verify_uintptr;

typedef unsigned int (*open_cfw_mram_verify_log_level_function)(void);
typedef void (*open_cfw_mram_verify_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_verify_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef void (*open_cfw_mram_verify_hex_function)(
    const void *,
    unsigned int,
    const void *,
    unsigned int
);

#define OPEN_CFW_MRAM_VERIFY_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_VERIFY_NVM_STRIDE 0x100U
#define OPEN_CFW_MRAM_VERIFY_OWNER_OFFSET 0x06U
#define OPEN_CFW_MRAM_VERIFY_IRK_OFFSET 0x07U
#define OPEN_CFW_MRAM_VERIFY_CSRK_OFFSET 0x1EU
#define OPEN_CFW_MRAM_VERIFY_KEY_MASK_OFFSET 0x2EU
#define OPEN_CFW_MRAM_VERIFY_IN_USE_OFFSET 0x2FU
#define OPEN_CFW_MRAM_VERIFY_VALID_OFFSET 0x30U
#define OPEN_CFW_MRAM_VERIFY_LOCAL_LTK_OFFSET 0x34U
#define OPEN_CFW_MRAM_VERIFY_KEY_SIZE 0x10U

#ifndef OPEN_CFW_MRAM_VERIFY_NVM_BASE
#define OPEN_CFW_MRAM_VERIFY_NVM_BASE \
    ((const volatile unsigned char *) \
        (open_cfw_mram_verify_uintptr)0x007FF000U)
#endif
#ifndef OPEN_CFW_MRAM_VERIFY_CACHE_INVALIDATE
#define OPEN_CFW_MRAM_VERIFY_CACHE_INVALIDATE(range, clean) \
    open_cfw_cache_dcache_invalidate( \
        (const open_cfw_cache_range *)(range), \
        (clean) \
    )
#endif
#ifndef OPEN_CFW_MRAM_VERIFY_COMPARE
#define OPEN_CFW_MRAM_VERIFY_COMPARE(left, right, size) \
    open_cfw_memory_compare((left), (right), (size))
#endif
#ifndef OPEN_CFW_MRAM_VERIFY_LOG_LEVEL
#define OPEN_CFW_MRAM_VERIFY_LOG_LEVEL() \
    (((open_cfw_mram_verify_log_level_function) \
        (open_cfw_mram_verify_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_VERIFY_LOG
#define OPEN_CFW_MRAM_VERIFY_LOG(...) \
    (((open_cfw_mram_verify_log_function) \
        (open_cfw_mram_verify_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_VERIFY_TRACE
#define OPEN_CFW_MRAM_VERIFY_TRACE(...) \
    (((open_cfw_mram_verify_trace_function) \
        (open_cfw_mram_verify_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_VERIFY_HEX
#define OPEN_CFW_MRAM_VERIFY_HEX(...) \
    (((open_cfw_mram_verify_hex_function) \
        (open_cfw_mram_verify_uintptr)0x0043DACDU)(__VA_ARGS__))
#endif

int open_cfw_memory_compare(
    const void *,
    const void *,
    unsigned int
);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_verify_pointer(open_cfw_mram_verify_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_verify_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_VERIFY_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_VERIFY_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_verify_diagnostic(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int trace_event,
    unsigned int trace_identity,
    unsigned int argument_count,
    unsigned int argument0,
    unsigned int argument1
)
{
    if ((OPEN_CFW_MRAM_VERIFY_LOG_LEVEL() & 2U) != 0U) {
        if (argument_count == 0U) {
            OPEN_CFW_MRAM_VERIFY_LOG(
                severity,
                open_cfw_mram_verify_pointer(0x0078A0D0U),
                open_cfw_mram_verify_pointer(0x006D84BCU),
                open_cfw_mram_verify_pointer(0x00775164U),
                line,
                open_cfw_mram_verify_pointer(structured_identity)
            );
        }
        else if (argument_count == 1U) {
            OPEN_CFW_MRAM_VERIFY_LOG(
                severity,
                open_cfw_mram_verify_pointer(0x0078A0D0U),
                open_cfw_mram_verify_pointer(0x006D84BCU),
                open_cfw_mram_verify_pointer(0x00775164U),
                line,
                open_cfw_mram_verify_pointer(structured_identity),
                argument0
            );
        }
        else {
            OPEN_CFW_MRAM_VERIFY_LOG(
                severity,
                open_cfw_mram_verify_pointer(0x0078A0D0U),
                open_cfw_mram_verify_pointer(0x006D84BCU),
                open_cfw_mram_verify_pointer(0x00775164U),
                line,
                open_cfw_mram_verify_pointer(structured_identity),
                argument0,
                argument1
            );
        }
    }

    if (!open_cfw_mram_verify_trace_enabled()) {
        return;
    }
    if (argument_count == 0U) {
        const void *identity =
            open_cfw_mram_verify_pointer(trace_identity);

        OPEN_CFW_MRAM_VERIFY_TRACE(
            trace_event,
            identity,
            identity
        );
    }
    else if (argument_count == 1U) {
        const void *identity =
            open_cfw_mram_verify_pointer(trace_identity);

        OPEN_CFW_MRAM_VERIFY_TRACE(
            trace_event,
            identity,
            identity,
            argument0
        );
    }
    else {
        const void *identity =
            open_cfw_mram_verify_pointer(trace_identity);

        OPEN_CFW_MRAM_VERIFY_TRACE(
            trace_event,
            identity,
            identity,
            argument0,
            argument1
        );
    }
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_verify_key(
    const unsigned char *record,
    const volatile unsigned char *persisted,
    unsigned int offset,
    unsigned int mismatch_line,
    unsigned int mismatch_structured_identity,
    unsigned int mismatch_trace_identity,
    unsigned int ram_label,
    unsigned int flash_label,
    unsigned int passed_line,
    unsigned int passed_structured_identity,
    unsigned int passed_trace_identity
)
{
    const unsigned char *record_key = record + offset;
    const volatile unsigned char *persisted_key = persisted + offset;

    if (
        OPEN_CFW_MRAM_VERIFY_COMPARE(
            record_key,
            (const void *)persisted_key,
            OPEN_CFW_MRAM_VERIFY_KEY_SIZE
        ) == 0
    ) {
        open_cfw_mram_verify_diagnostic(
            4U,
            passed_line,
            passed_structured_identity,
            0x10000000U,
            passed_trace_identity,
            0U,
            0U,
            0U
        );
        return 1U;
    }

    open_cfw_mram_verify_diagnostic(
        1U,
        mismatch_line,
        mismatch_structured_identity,
        0x04000000U,
        mismatch_trace_identity,
        0U,
        0U,
        0U
    );
    OPEN_CFW_MRAM_VERIFY_HEX(
        open_cfw_mram_verify_pointer(ram_label),
        OPEN_CFW_MRAM_VERIFY_KEY_SIZE,
        record_key,
        OPEN_CFW_MRAM_VERIFY_KEY_SIZE
    );
    OPEN_CFW_MRAM_VERIFY_HEX(
        open_cfw_mram_verify_pointer(flash_label),
        OPEN_CFW_MRAM_VERIFY_KEY_SIZE,
        (const void *)persisted_key,
        OPEN_CFW_MRAM_VERIFY_KEY_SIZE
    );
    return 0U;
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_verify_write(const unsigned char *record)
{
    const volatile unsigned char *persisted =
        OPEN_CFW_MRAM_VERIFY_NVM_BASE;
    unsigned int verified = 1U;
    unsigned int index;

    open_cfw_mram_verify_diagnostic(
        4U,
        0x779U,
        0x0071C118U,
        0x10000000U,
        0x00700458U,
        0U,
        0U,
        0U
    );
    (void)OPEN_CFW_MRAM_VERIFY_CACHE_INVALIDATE(
        (const void *)0,
        1U
    );

#pragma clang loop unroll(disable)
    for (
        index = 0U;
        index < OPEN_CFW_MRAM_VERIFY_RECORD_COUNT;
        ++index
    ) {
        unsigned int record_value;
        unsigned int persisted_value;

        if (
            OPEN_CFW_MRAM_VERIFY_COMPARE(
                record,
                (const void *)persisted,
                6U
            ) != 0
            || record[OPEN_CFW_MRAM_VERIFY_OWNER_OFFSET]
                != persisted[OPEN_CFW_MRAM_VERIFY_OWNER_OFFSET]
        ) {
            persisted += OPEN_CFW_MRAM_VERIFY_NVM_STRIDE;
            continue;
        }

        open_cfw_mram_verify_diagnostic(
            4U,
            0x782U,
            0x0071C150U,
            0x10400000U,
            0x0070049CU,
            1U,
            index,
            0U
        );

        record_value = record[OPEN_CFW_MRAM_VERIFY_VALID_OFFSET];
        persisted_value =
            persisted[OPEN_CFW_MRAM_VERIFY_VALID_OFFSET];
        if (record_value != persisted_value) {
            open_cfw_mram_verify_diagnostic(
                1U,
                0x787U,
                0x007093A4U,
                0x04800000U,
                0x006F1A14U,
                2U,
                record_value,
                persisted_value
            );
            verified = 0U;
        }

        record_value = record[OPEN_CFW_MRAM_VERIFY_IN_USE_OFFSET];
        persisted_value =
            persisted[OPEN_CFW_MRAM_VERIFY_IN_USE_OFFSET];
        if (record_value != persisted_value) {
            open_cfw_mram_verify_diagnostic(
                1U,
                0x78DU,
                0x007093E4U,
                0x04800000U,
                0x006F1A60U,
                2U,
                record_value,
                persisted_value
            );
            verified = 0U;
        }

        record_value = record[OPEN_CFW_MRAM_VERIFY_KEY_MASK_OFFSET];
        persisted_value =
            persisted[OPEN_CFW_MRAM_VERIFY_KEY_MASK_OFFSET];
        if (record_value != persisted_value) {
            open_cfw_mram_verify_diagnostic(
                1U,
                0x793U,
                0x006F85F4U,
                0x04800000U,
                0x006E637CU,
                2U,
                record_value,
                persisted_value
            );
            verified = 0U;
        }

        if (
            (record_value & 1U) != 0U
            && open_cfw_mram_verify_key(
                record,
                persisted,
                OPEN_CFW_MRAM_VERIFY_LOCAL_LTK_OFFSET,
                0x79AU,
                0x0073C114U,
                0x00726E8CU,
                0x0078CA5CU,
                0x0078A118U,
                0x79FU,
                0x00726EC0U,
                0x00709424U
            ) == 0U
        ) {
            verified = 0U;
        }
        if (
            (record_value & 4U) != 0U
            && open_cfw_mram_verify_key(
                record,
                persisted,
                OPEN_CFW_MRAM_VERIFY_IRK_OFFSET,
                0x7A6U,
                0x00751F14U,
                0x00731874U,
                0x0078CA64U,
                0x0078A124U,
                0x7ABU,
                0x007318A4U,
                0x007127A8U
            ) == 0U
        ) {
            verified = 0U;
        }
        if (
            (record_value & 8U) != 0U
            && open_cfw_mram_verify_key(
                record,
                persisted,
                OPEN_CFW_MRAM_VERIFY_CSRK_OFFSET,
                0x7B2U,
                0x00751F38U,
                0x007318D4U,
                0x0078A130U,
                0x0078A13CU,
                0x7B7U,
                0x00731904U,
                0x007127E4U
            ) == 0U
        ) {
            verified = 0U;
        }
        break;
    }

    if ((unsigned char)verified != 0U) {
        open_cfw_mram_verify_diagnostic(
            4U,
            0x7C2U,
            0x00731934U,
            0x10000000U,
            0x00712820U,
            0U,
            0U,
            0U
        );
    }
    else {
        open_cfw_mram_verify_diagnostic(
            1U,
            0x7C4U,
            0x006E63D0U,
            0x04000000U,
            0x006DF65CU,
            0U,
            0U,
            0U
        );
    }
    return (unsigned char)verified;
}
