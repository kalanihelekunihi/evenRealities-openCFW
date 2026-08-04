/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Cordio pairing-failure handler matched to stock
 * AppDbHandlePairingFailure at 0x0047C568.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_pairing_failure_uintptr;

typedef unsigned char *(*open_cfw_mram_pairing_failure_lookup_function)(
    unsigned int
);
typedef void (*open_cfw_mram_pairing_failure_clear_function)(unsigned int);
typedef unsigned int (*open_cfw_mram_pairing_failure_log_level_function)(
    void
);
typedef void (*open_cfw_mram_pairing_failure_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_mram_pairing_failure_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#define OPEN_CFW_MRAM_PAIRING_FAILURE_KEY_MASK_OFFSET 0x2EU
#define OPEN_CFW_MRAM_PAIRING_FAILURE_IN_USE_OFFSET 0x2FU
#define OPEN_CFW_MRAM_PAIRING_FAILURE_VALID_OFFSET 0x30U

#ifndef OPEN_CFW_MRAM_PAIRING_FAILURE_SHOW_NVM
#define OPEN_CFW_MRAM_PAIRING_FAILURE_SHOW_NVM() \
    open_cfw_mram_show_nvm_status()
#endif
#ifndef OPEN_CFW_MRAM_PAIRING_FAILURE_LOOKUP
#define OPEN_CFW_MRAM_PAIRING_FAILURE_LOOKUP(conn_id) \
    (((open_cfw_mram_pairing_failure_lookup_function) \
        (open_cfw_mram_pairing_failure_uintptr)0x004BB07DU)(conn_id))
#endif
#ifndef OPEN_CFW_MRAM_PAIRING_FAILURE_CLEAR
#define OPEN_CFW_MRAM_PAIRING_FAILURE_CLEAR(conn_id) \
    (((open_cfw_mram_pairing_failure_clear_function) \
        (open_cfw_mram_pairing_failure_uintptr)0x0047C8CDU)(conn_id))
#endif
#ifndef OPEN_CFW_MRAM_PAIRING_FAILURE_LOG_LEVEL
#define OPEN_CFW_MRAM_PAIRING_FAILURE_LOG_LEVEL() \
    (((open_cfw_mram_pairing_failure_log_level_function) \
        (open_cfw_mram_pairing_failure_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_MRAM_PAIRING_FAILURE_LOG
#define OPEN_CFW_MRAM_PAIRING_FAILURE_LOG(...) \
    (((open_cfw_mram_pairing_failure_log_function) \
        (open_cfw_mram_pairing_failure_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE
#define OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE(...) \
    (((open_cfw_mram_pairing_failure_trace_function) \
        (open_cfw_mram_pairing_failure_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

void open_cfw_mram_show_nvm_status(void);

static __attribute__((always_inline)) inline const void *
open_cfw_mram_pairing_failure_pointer(
    open_cfw_mram_pairing_failure_uintptr address
)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_mram_pairing_failure_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_MRAM_PAIRING_FAILURE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_MRAM_PAIRING_FAILURE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_mram_pairing_failure_pair(
    unsigned int severity,
    unsigned int line,
    open_cfw_mram_pairing_failure_uintptr structured_identity,
    unsigned int trace_event,
    open_cfw_mram_pairing_failure_uintptr trace_identity,
    unsigned int argument_count,
    open_cfw_mram_pairing_failure_uintptr argument_0,
    open_cfw_mram_pairing_failure_uintptr argument_1,
    open_cfw_mram_pairing_failure_uintptr argument_2
)
{
    if ((OPEN_CFW_MRAM_PAIRING_FAILURE_LOG_LEVEL() & 2U) != 0U) {
        if (argument_count == 0U) {
            OPEN_CFW_MRAM_PAIRING_FAILURE_LOG(
                severity,
                open_cfw_mram_pairing_failure_pointer(0x0078A0D0U),
                open_cfw_mram_pairing_failure_pointer(0x006D84BCU),
                open_cfw_mram_pairing_failure_pointer(0x00769484U),
                line,
                open_cfw_mram_pairing_failure_pointer(
                    structured_identity
                )
            );
        } else if (argument_count == 1U) {
            OPEN_CFW_MRAM_PAIRING_FAILURE_LOG(
                severity,
                open_cfw_mram_pairing_failure_pointer(0x0078A0D0U),
                open_cfw_mram_pairing_failure_pointer(0x006D84BCU),
                open_cfw_mram_pairing_failure_pointer(0x00769484U),
                line,
                open_cfw_mram_pairing_failure_pointer(
                    structured_identity
                ),
                argument_0
            );
        } else if (argument_count == 2U) {
            OPEN_CFW_MRAM_PAIRING_FAILURE_LOG(
                severity,
                open_cfw_mram_pairing_failure_pointer(0x0078A0D0U),
                open_cfw_mram_pairing_failure_pointer(0x006D84BCU),
                open_cfw_mram_pairing_failure_pointer(0x00769484U),
                line,
                open_cfw_mram_pairing_failure_pointer(
                    structured_identity
                ),
                argument_0,
                argument_1
            );
        } else {
            OPEN_CFW_MRAM_PAIRING_FAILURE_LOG(
                severity,
                open_cfw_mram_pairing_failure_pointer(0x0078A0D0U),
                open_cfw_mram_pairing_failure_pointer(0x006D84BCU),
                open_cfw_mram_pairing_failure_pointer(0x00769484U),
                line,
                open_cfw_mram_pairing_failure_pointer(
                    structured_identity
                ),
                argument_0,
                argument_1,
                argument_2
            );
        }
    }
    if (open_cfw_mram_pairing_failure_trace_enabled()) {
        const void *identity =
            open_cfw_mram_pairing_failure_pointer(trace_identity);

        if (argument_count == 0U) {
            OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE(
                trace_event,
                identity,
                identity
            );
        } else if (argument_count == 1U) {
            OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE(
                trace_event,
                identity,
                identity,
                argument_0
            );
        } else if (argument_count == 2U) {
            OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE(
                trace_event,
                identity,
                identity,
                argument_0,
                argument_1
            );
        } else {
            OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE(
                trace_event,
                identity,
                identity,
                argument_0,
                argument_1,
                argument_2
            );
        }
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_pairing_failure_address(
    const unsigned char *record
)
{
    unsigned int byte_5 = record[5];
    unsigned int byte_4 = record[4];
    unsigned int byte_3 = record[3];
    unsigned int byte_2 = record[2];
    unsigned int byte_1 = record[1];
    unsigned int byte_0 = record[0];

    if ((OPEN_CFW_MRAM_PAIRING_FAILURE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_MRAM_PAIRING_FAILURE_LOG(
            2U,
            open_cfw_mram_pairing_failure_pointer(0x0078A0D0U),
            open_cfw_mram_pairing_failure_pointer(0x006D84BCU),
            open_cfw_mram_pairing_failure_pointer(0x00769484U),
            0x880U,
            open_cfw_mram_pairing_failure_pointer(0x006D9F6CU),
            (open_cfw_mram_pairing_failure_uintptr)byte_5,
            (open_cfw_mram_pairing_failure_uintptr)byte_4,
            (open_cfw_mram_pairing_failure_uintptr)byte_3,
            (open_cfw_mram_pairing_failure_uintptr)byte_2,
            (open_cfw_mram_pairing_failure_uintptr)byte_1,
            (open_cfw_mram_pairing_failure_uintptr)byte_0
        );
    }
    if (open_cfw_mram_pairing_failure_trace_enabled()) {
        const void *identity =
            open_cfw_mram_pairing_failure_pointer(0x006D6B70U);

        OPEN_CFW_MRAM_PAIRING_FAILURE_TRACE(
            0x09800000U,
            identity,
            identity,
            (open_cfw_mram_pairing_failure_uintptr)byte_5,
            (open_cfw_mram_pairing_failure_uintptr)byte_4,
            (open_cfw_mram_pairing_failure_uintptr)byte_3,
            (open_cfw_mram_pairing_failure_uintptr)byte_2,
            (open_cfw_mram_pairing_failure_uintptr)byte_1,
            (open_cfw_mram_pairing_failure_uintptr)byte_0
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_mram_pairing_failure_reason(unsigned int status)
{
    if (status == 0x0BU) {
        open_cfw_mram_pairing_failure_pair(
            1U,
            0x885U,
            0x006E6478U,
            0x04000000U,
            0x006DC574U,
            0U,
            0U,
            0U,
            0U
        );
    } else if (status == 4U) {
        open_cfw_mram_pairing_failure_pair(
            2U,
            0x88AU,
            0x00700568U,
            0x08000000U,
            0x006EB718U,
            0U,
            0U,
            0U,
            0U
        );
    } else if (status == 1U) {
        open_cfw_mram_pairing_failure_pair(
            2U,
            0x88EU,
            0x007005ACU,
            0x08000000U,
            0x006EB768U,
            0U,
            0U,
            0U,
            0U
        );
    } else if (status == 3U) {
        open_cfw_mram_pairing_failure_pair(
            2U,
            0x892U,
            0x006E64CCU,
            0x08000000U,
            0x006DF714U,
            0U,
            0U,
            0U,
            0U
        );
    } else {
        open_cfw_mram_pairing_failure_pair(
            2U,
            0x896U,
            0x006EB7B8U,
            0x08400000U,
            0x006E25F0U,
            1U,
            (open_cfw_mram_pairing_failure_uintptr)status,
            0U,
            0U
        );
    }
}

__attribute__((used, noinline))
void open_cfw_mram_handle_pairing_failure(
    unsigned int connection_id,
    unsigned int status
)
{
    unsigned int connection = (unsigned char)connection_id;
    unsigned int reason = (unsigned char)status;
    unsigned char *record;

    open_cfw_mram_pairing_failure_pair(
        4U,
        0x872U,
        0x006E6424U,
        0x10800000U,
        0x006DC514U,
        2U,
        (open_cfw_mram_pairing_failure_uintptr)connection,
        (open_cfw_mram_pairing_failure_uintptr)reason,
        0U
    );
    OPEN_CFW_MRAM_PAIRING_FAILURE_SHOW_NVM();
    record = OPEN_CFW_MRAM_PAIRING_FAILURE_LOOKUP(connection);
    if (record == (unsigned char *)0) {
        open_cfw_mram_pairing_failure_pair(
            4U,
            0x8A6U,
            0x006DF770U,
            0x10400000U,
            0x006D9FD0U,
            1U,
            (open_cfw_mram_pairing_failure_uintptr)connection,
            0U,
            0U
        );
        return;
    }
    if (
        record[OPEN_CFW_MRAM_PAIRING_FAILURE_VALID_OFFSET] == 0U
        || (
            record[OPEN_CFW_MRAM_PAIRING_FAILURE_KEY_MASK_OFFSET] & 5U
        ) == 0U
    ) {
        open_cfw_mram_pairing_failure_pair(
            4U,
            0x89FU,
            0x006A7814U,
            0x10C00000U,
            0x0069E604U,
            3U,
            (open_cfw_mram_pairing_failure_uintptr)connection,
            (open_cfw_mram_pairing_failure_uintptr)
                record[OPEN_CFW_MRAM_PAIRING_FAILURE_VALID_OFFSET],
            (open_cfw_mram_pairing_failure_uintptr)
                record[OPEN_CFW_MRAM_PAIRING_FAILURE_KEY_MASK_OFFSET]
        );
        record[OPEN_CFW_MRAM_PAIRING_FAILURE_VALID_OFFSET] = 0U;
        record[OPEN_CFW_MRAM_PAIRING_FAILURE_IN_USE_OFFSET] = 0U;
        return;
    }

    open_cfw_mram_pairing_failure_address(record);
    open_cfw_mram_pairing_failure_reason(reason);
    OPEN_CFW_MRAM_PAIRING_FAILURE_CLEAR(connection);
}
