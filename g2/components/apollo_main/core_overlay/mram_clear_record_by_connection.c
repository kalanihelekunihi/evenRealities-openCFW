/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio pairing-record clearer matched to stock
 * AppDbClearRecordByConnId at 0x0047C8CC.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_clear_connection_uintptr;

typedef unsigned char *(*open_cfw_mram_clear_connection_lookup_function)(
    unsigned int
);
typedef unsigned int (*open_cfw_mram_clear_connection_log_level_function)(
    void
);
typedef void (*open_cfw_mram_clear_connection_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_clear_connection_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_CLEAR_CONNECTION_KEY_MASK_OFFSET 0x2EU
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_IN_USE_OFFSET 0x2FU
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_VALID_OFFSET 0x30U

#ifndef OPEN_CFW_MRAM_CLEAR_CONNECTION_LOOKUP
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_LOOKUP(conn_id) \
    (((open_cfw_mram_clear_connection_lookup_function) \
        (open_cfw_mram_clear_connection_uintptr)0x004BB07DU)(conn_id))
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_CONNECTION_CLEAR
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_CLEAR(owner, address) \
    open_cfw_mram_clear_record_by_mac_address((owner), (address))
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_CONNECTION_RELOAD
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_RELOAD() \
    open_cfw_mram_reload_resolving_list()
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL() \
    (((open_cfw_mram_clear_connection_log_level_function) \
        (open_cfw_mram_clear_connection_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG(...) \
    (((open_cfw_mram_clear_connection_log_function) \
        (open_cfw_mram_clear_connection_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_CLEAR_CONNECTION_TRACE
#define OPEN_CFW_MRAM_CLEAR_CONNECTION_TRACE(...) \
    (((open_cfw_mram_clear_connection_trace_function) \
        (open_cfw_mram_clear_connection_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned int open_cfw_mram_clear_record_by_mac_address(
    unsigned int,
    const unsigned char *
);
void open_cfw_mram_reload_resolving_list(void);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_clear_connection_pointer(
    open_cfw_mram_clear_connection_uintptr address
)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_clear_connection_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_clear_connection_simple(
    unsigned int severity,
    unsigned int line,
    open_cfw_mram_clear_connection_uintptr structured_identity,
    unsigned int trace_event,
    open_cfw_mram_clear_connection_uintptr trace_identity,
    unsigned int has_connection,
    unsigned int connection
)
{
    if ((OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL() & 2U) != 0U) {
        if (has_connection != 0U) {
            OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG(
                severity,
                open_cfw_mram_clear_connection_pointer(0x0078A0D0U),
                open_cfw_mram_clear_connection_pointer(0x006D84BCU),
                open_cfw_mram_clear_connection_pointer(0x007694A0U),
                line,
                open_cfw_mram_clear_connection_pointer(
                    structured_identity
                ),
                (open_cfw_mram_clear_connection_uintptr)connection
            );
        } else {
            OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG(
                severity,
                open_cfw_mram_clear_connection_pointer(0x0078A0D0U),
                open_cfw_mram_clear_connection_pointer(0x006D84BCU),
                open_cfw_mram_clear_connection_pointer(0x007694A0U),
                line,
                open_cfw_mram_clear_connection_pointer(
                    structured_identity
                )
            );
        }
    }
    if (open_cfw_mram_clear_connection_trace_enabled()) {
        const void *identity =
            open_cfw_mram_clear_connection_pointer(trace_identity);

        if (has_connection != 0U) {
            OPEN_CFW_MRAM_CLEAR_CONNECTION_TRACE(
                trace_event,
                identity,
                identity,
                (open_cfw_mram_clear_connection_uintptr)connection
            );
        } else {
            OPEN_CFW_MRAM_CLEAR_CONNECTION_TRACE(
                trace_event,
                identity,
                identity
            );
        }
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_clear_connection_address(const unsigned char *record)
{
    unsigned int byte_5 = record[5];
    unsigned int byte_4 = record[4];
    unsigned int byte_3 = record[3];
    unsigned int byte_2 = record[2];
    unsigned int byte_1 = record[1];
    unsigned int byte_0 = record[0];

    if ((OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG(
            2U,
            open_cfw_mram_clear_connection_pointer(0x0078A0D0U),
            open_cfw_mram_clear_connection_pointer(0x006D84BCU),
            open_cfw_mram_clear_connection_pointer(0x007694A0U),
            0x8BBU,
            open_cfw_mram_clear_connection_pointer(0x006DC5D4U),
            (open_cfw_mram_clear_connection_uintptr)byte_5,
            (open_cfw_mram_clear_connection_uintptr)byte_4,
            (open_cfw_mram_clear_connection_uintptr)byte_3,
            (open_cfw_mram_clear_connection_uintptr)byte_2,
            (open_cfw_mram_clear_connection_uintptr)byte_1,
            (open_cfw_mram_clear_connection_uintptr)byte_0
        );
    }
    if (open_cfw_mram_clear_connection_trace_enabled()) {
        const void *identity =
            open_cfw_mram_clear_connection_pointer(0x006D858CU);

        OPEN_CFW_MRAM_CLEAR_CONNECTION_TRACE(
            0x09800000U,
            identity,
            identity,
            (open_cfw_mram_clear_connection_uintptr)byte_5,
            (open_cfw_mram_clear_connection_uintptr)byte_4,
            (open_cfw_mram_clear_connection_uintptr)byte_3,
            (open_cfw_mram_clear_connection_uintptr)byte_2,
            (open_cfw_mram_clear_connection_uintptr)byte_1,
            (open_cfw_mram_clear_connection_uintptr)byte_0
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_clear_connection_invalid(
    unsigned int connection,
    unsigned int valid,
    unsigned int key_mask
)
{
    if ((OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_CLEAR_CONNECTION_LOG(
            4U,
            open_cfw_mram_clear_connection_pointer(0x0078A0D0U),
            open_cfw_mram_clear_connection_pointer(0x006D84BCU),
            open_cfw_mram_clear_connection_pointer(0x007694A0U),
            0x8C9U,
            open_cfw_mram_clear_connection_pointer(0x006DA034U),
            (open_cfw_mram_clear_connection_uintptr)connection,
            (open_cfw_mram_clear_connection_uintptr)valid,
            (open_cfw_mram_clear_connection_uintptr)key_mask
        );
    }
    if (open_cfw_mram_clear_connection_trace_enabled()) {
        const void *identity =
            open_cfw_mram_clear_connection_pointer(0x006D6BE0U);

        OPEN_CFW_MRAM_CLEAR_CONNECTION_TRACE(
            0x10C00000U,
            identity,
            identity,
            (open_cfw_mram_clear_connection_uintptr)connection,
            (open_cfw_mram_clear_connection_uintptr)valid,
            (open_cfw_mram_clear_connection_uintptr)key_mask
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_clear_record_by_connection(unsigned int connection_id)
{
    unsigned int connection = (unsigned char)connection_id;
    unsigned char *record =
        OPEN_CFW_MRAM_CLEAR_CONNECTION_LOOKUP(connection);

    if (record == (unsigned char *)0) {
        open_cfw_mram_clear_connection_simple(
            4U,
            0x8D0U,
            0x006E6520U,
            0x10400000U,
            0x006DC634U,
            1U,
            connection
        );
        return;
    }
    if (
        record[OPEN_CFW_MRAM_CLEAR_CONNECTION_VALID_OFFSET] == 0U
        || (
            record[OPEN_CFW_MRAM_CLEAR_CONNECTION_KEY_MASK_OFFSET] & 5U
        ) == 0U
    ) {
        open_cfw_mram_clear_connection_invalid(
            connection,
            record[OPEN_CFW_MRAM_CLEAR_CONNECTION_VALID_OFFSET],
            record[OPEN_CFW_MRAM_CLEAR_CONNECTION_KEY_MASK_OFFSET]
        );
        record[OPEN_CFW_MRAM_CLEAR_CONNECTION_VALID_OFFSET] = 0U;
        record[OPEN_CFW_MRAM_CLEAR_CONNECTION_IN_USE_OFFSET] = 0U;
        return;
    }

    open_cfw_mram_clear_connection_address(record);
    if (
        (unsigned char)OPEN_CFW_MRAM_CLEAR_CONNECTION_CLEAR(
            record[6],
            record
        ) != 0U
    ) {
        open_cfw_mram_clear_connection_simple(
            4U,
            0x8C0U,
            0x006F1AACU,
            0x10000000U,
            0x006E2648U,
            0U,
            0U
        );
    } else {
        open_cfw_mram_clear_connection_simple(
            1U,
            0x8C2U,
            0x007005F0U,
            0x04000000U,
            0x006EB808U,
            0U,
            0U
        );
    }
    OPEN_CFW_MRAM_CLEAR_CONNECTION_RELOAD();
}
