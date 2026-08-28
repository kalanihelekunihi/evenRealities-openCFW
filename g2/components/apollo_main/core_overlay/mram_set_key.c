/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio application-database key writer matched to stock
 * AppDbSetKey at 0x0047AED4.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_set_key_uintptr;

typedef unsigned int (*open_cfw_mram_set_key_verify_function)(
    const unsigned char *
);
typedef unsigned int (*open_cfw_mram_set_key_log_level_function)(void);
typedef void (*open_cfw_mram_set_key_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_set_key_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_MRAM_SET_KEY_UPDATE
#define OPEN_CFW_MRAM_SET_KEY_UPDATE(record) \
    open_cfw_mram_app_db_update(record)
#endif
#ifndef OPEN_CFW_MRAM_SET_KEY_VERIFY
#define OPEN_CFW_MRAM_SET_KEY_VERIFY(record) \
    (((open_cfw_mram_set_key_verify_function) \
        (open_cfw_mram_set_key_uintptr)0x0047B731U)(record))
#endif
#ifndef OPEN_CFW_MRAM_SET_KEY_LOG_LEVEL
#define OPEN_CFW_MRAM_SET_KEY_LOG_LEVEL() \
    (((open_cfw_mram_set_key_log_level_function) \
        (open_cfw_mram_set_key_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_SET_KEY_LOG
#define OPEN_CFW_MRAM_SET_KEY_LOG(...) \
    (((open_cfw_mram_set_key_log_function) \
        (open_cfw_mram_set_key_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_SET_KEY_TRACE
#define OPEN_CFW_MRAM_SET_KEY_TRACE(...) \
    (((open_cfw_mram_set_key_trace_function) \
        (open_cfw_mram_set_key_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned int open_cfw_mram_app_db_update(
    const unsigned char *
);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_set_key_pointer(open_cfw_mram_set_key_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_set_key_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_SET_KEY_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_SET_KEY_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((noinline)) void
open_cfw_mram_set_key_diagnostic(
    unsigned int severity,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int event,
    unsigned int trace_identity,
    unsigned int argument_count,
    const unsigned int *arguments
)
{
    if ((OPEN_CFW_MRAM_SET_KEY_LOG_LEVEL() & 2U) != 0U) {
        if (argument_count == 0U) {
            OPEN_CFW_MRAM_SET_KEY_LOG(
                severity,
                open_cfw_mram_set_key_pointer(0x0078A0D0U),
                open_cfw_mram_set_key_pointer(0x006D84BCU),
                open_cfw_mram_set_key_pointer(0x0078A10CU),
                line,
                open_cfw_mram_set_key_pointer(structured_identity)
            );
        }
        else if (argument_count == 1U) {
            OPEN_CFW_MRAM_SET_KEY_LOG(
                severity,
                open_cfw_mram_set_key_pointer(0x0078A0D0U),
                open_cfw_mram_set_key_pointer(0x006D84BCU),
                open_cfw_mram_set_key_pointer(0x0078A10CU),
                line,
                open_cfw_mram_set_key_pointer(structured_identity),
                arguments[0]
            );
        }
        else if (argument_count == 2U) {
            OPEN_CFW_MRAM_SET_KEY_LOG(
                severity,
                open_cfw_mram_set_key_pointer(0x0078A0D0U),
                open_cfw_mram_set_key_pointer(0x006D84BCU),
                open_cfw_mram_set_key_pointer(0x0078A10CU),
                line,
                open_cfw_mram_set_key_pointer(structured_identity),
                arguments[0],
                arguments[1]
            );
        }
        else if (argument_count == 6U) {
            OPEN_CFW_MRAM_SET_KEY_LOG(
                severity,
                open_cfw_mram_set_key_pointer(0x0078A0D0U),
                open_cfw_mram_set_key_pointer(0x006D84BCU),
                open_cfw_mram_set_key_pointer(0x0078A10CU),
                line,
                open_cfw_mram_set_key_pointer(structured_identity),
                arguments[0],
                arguments[1],
                arguments[2],
                arguments[3],
                arguments[4],
                arguments[5]
            );
        }
        else {
            OPEN_CFW_MRAM_SET_KEY_LOG(
                severity,
                open_cfw_mram_set_key_pointer(0x0078A0D0U),
                open_cfw_mram_set_key_pointer(0x006D84BCU),
                open_cfw_mram_set_key_pointer(0x0078A10CU),
                line,
                open_cfw_mram_set_key_pointer(structured_identity),
                arguments[0],
                arguments[1],
                arguments[2],
                arguments[3],
                arguments[4],
                arguments[5],
                arguments[6],
                arguments[7],
                arguments[8],
                arguments[9],
                arguments[10],
                arguments[11],
                arguments[12],
                arguments[13],
                arguments[14],
                arguments[15]
            );
        }
    }

    if (!open_cfw_mram_set_key_trace_enabled()) {
        return;
    }
    if (argument_count == 0U) {
        const void *identity =
            open_cfw_mram_set_key_pointer(trace_identity);

        OPEN_CFW_MRAM_SET_KEY_TRACE(event, identity, identity);
    }
    else if (argument_count == 1U) {
        const void *identity =
            open_cfw_mram_set_key_pointer(trace_identity);

        OPEN_CFW_MRAM_SET_KEY_TRACE(
            event,
            identity,
            identity,
            arguments[0]
        );
    }
    else if (argument_count == 2U) {
        const void *identity =
            open_cfw_mram_set_key_pointer(trace_identity);

        OPEN_CFW_MRAM_SET_KEY_TRACE(
            event,
            identity,
            identity,
            arguments[0],
            arguments[1]
        );
    }
    else if (argument_count == 6U) {
        const void *identity =
            open_cfw_mram_set_key_pointer(trace_identity);

        OPEN_CFW_MRAM_SET_KEY_TRACE(
            event,
            identity,
            identity,
            arguments[0],
            arguments[1],
            arguments[2],
            arguments[3],
            arguments[4],
            arguments[5]
        );
    }
    else {
        const void *identity =
            open_cfw_mram_set_key_pointer(trace_identity);

        OPEN_CFW_MRAM_SET_KEY_TRACE(
            event,
            identity,
            identity,
            arguments[0],
            arguments[1],
            arguments[2],
            arguments[3],
            arguments[4],
            arguments[5],
            arguments[6],
            arguments[7],
            arguments[8],
            arguments[9],
            arguments[10],
            arguments[11],
            arguments[12],
            arguments[13],
            arguments[14],
            arguments[15]
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_set_key_copy(
    unsigned char *destination,
    const unsigned char *source,
    unsigned int size
)
{
    unsigned int index;

    for (index = 0U; index < size; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_mram_set_key_halfword(const unsigned char *source)
{
    return (unsigned int)source[0]
        | (unsigned int)source[1] << 8U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_set_key_key_arguments(
    const unsigned char *event,
    unsigned int *arguments
)
{
    unsigned int index;

    for (index = 0U; index < 16U; ++index) {
        arguments[index] = event[4U + index];
    }
}

__attribute__((used, noinline))
void open_cfw_mram_set_key(
    unsigned char *record,
    const unsigned char *event
)
{
    unsigned int arguments[16];
    unsigned int key_type = event[0x1EU];
    unsigned int index;

    arguments[0] = key_type;
    open_cfw_mram_set_key_diagnostic(
        4U,
        0x506U,
        0x007693C0U,
        0x10400000U,
        0x00747864U,
        1U,
        arguments
    );

    if (key_type == 1U) {
        record[0x4EU] = event[0x1FU];
        open_cfw_mram_set_key_copy(record + 0x34U, event + 4U, 0x1AU);
        record[0x2EU] |= 1U;

        arguments[0] = event[0x1FU];
        arguments[1] = open_cfw_mram_set_key_halfword(event + 0x1CU);
        open_cfw_mram_set_key_diagnostic(
            4U,
            0x50FU,
            0x007126F4U,
            0x10800000U,
            0x00700348U,
            2U,
            arguments
        );
        open_cfw_mram_set_key_key_arguments(event, arguments);
        open_cfw_mram_set_key_diagnostic(
            4U,
            0x514U,
            0x006A71F4U,
            0x10000000U
                | (event[0x0EU] & 0x0FU) << 22U,
            0x006D5F48U,
            16U,
            arguments
        );
    }
    else if (key_type == 2U) {
        record[0x6AU] = event[0x1FU];
        open_cfw_mram_set_key_copy(record + 0x50U, event + 4U, 0x1AU);
        record[0x2EU] |= 2U;

        arguments[0] = event[0x1FU];
        arguments[1] = open_cfw_mram_set_key_halfword(event + 0x1CU);
        open_cfw_mram_set_key_diagnostic(
            4U,
            0x51CU,
            0x0071C070U,
            0x10800000U,
            0x0070038CU,
            2U,
            arguments
        );
        open_cfw_mram_set_key_key_arguments(event, arguments);
        open_cfw_mram_set_key_diagnostic(
            4U,
            0x521U,
            0x006A7504U,
            0x10000000U
                | (event[0x0EU] & 0x0FU) << 22U,
            0x006D5FC0U,
            16U,
            arguments
        );
    }
    else if (key_type == 4U) {
        open_cfw_mram_set_key_copy(record + 7U, event + 4U, 0x17U);
        record[0x2EU] |= 4U;
        record[6U] = event[0x1AU];
        open_cfw_mram_set_key_copy(record, event + 0x14U, 6U);

        arguments[0] = event[0x1AU];
        open_cfw_mram_set_key_diagnostic(
            4U,
            0x52AU,
            0x0074788CU,
            0x10400000U,
            0x00726DBCU,
            1U,
            arguments
        );
        for (index = 0U; index < 6U; ++index) {
            arguments[index] = event[0x19U - index];
        }
        open_cfw_mram_set_key_diagnostic(
            4U,
            0x52DU,
            0x0071C0A8U,
            0x11800000U,
            0x007092E4U,
            6U,
            arguments
        );
    }
    else if (key_type == 8U) {
        open_cfw_mram_set_key_copy(record + 0x1EU, event + 4U, 0x10U);
        record[0x2EU] |= 8U;
        *(unsigned int *)(void *)(record + 0x80U) = 0U;
        open_cfw_mram_set_key_diagnostic(
            4U,
            0x535U,
            0x007693DCU,
            0x10000000U,
            0x00751EF0U,
            0U,
            arguments
        );
    }
    else {
        arguments[0] = key_type;
        open_cfw_mram_set_key_diagnostic(
            2U,
            0x539U,
            0x007478B4U,
            0x08400000U,
            0x00726DF0U,
            1U,
            arguments
        );
    }

    arguments[0] = record[0x2EU];
    open_cfw_mram_set_key_diagnostic(
        4U,
        0x53CU,
        0x00731844U,
        0x10400000U,
        0x00712730U,
        1U,
        arguments
    );
    if (record[0x30U] == 1U) {
        (void)OPEN_CFW_MRAM_SET_KEY_UPDATE(record);
        (void)OPEN_CFW_MRAM_SET_KEY_VERIFY(record);
    }
}
