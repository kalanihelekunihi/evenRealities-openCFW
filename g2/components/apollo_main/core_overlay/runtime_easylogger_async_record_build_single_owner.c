/*
 * SPDX-License-Identifier: MIT
 *
 * Production corrected clean-room source for Apollo main's private G2
 * EasyLogger level-aware record builder at 0x00448D4E...0x00448DD1.
 *
 * Retained enqueue owns the record on both success and retry-limit failure.
 * This removes the stock builder's second recycle.  It is G2 transport glue,
 * not upstream EasyLogger code.  The retained enqueue ownership contract is
 * authenticated by docs/research/easylogger-g2-async-sink-audit.md and gated
 * by tests/test_runtime_easylogger_async_record_build.py.
 */

typedef __UINT8_TYPE__ open_cfw_g2_easylogger_async_u8;
typedef __UINT16_TYPE__ open_cfw_g2_easylogger_async_u16;
typedef __UINT32_TYPE__ open_cfw_g2_easylogger_async_u32;

enum {
    OPEN_CFW_G2_EASYLOGGER_ASYNC_RECORD_SIZE = 0x110U,
    OPEN_CFW_G2_EASYLOGGER_ASYNC_PAYLOAD_SIZE = 0x100U,
    OPEN_CFW_G2_EASYLOGGER_ASYNC_MAX_LENGTH = 0xFFU
};

struct open_cfw_g2_easylogger_async_record {
    open_cfw_g2_easylogger_async_u32 next;
    open_cfw_g2_easylogger_async_u32 state;
    open_cfw_g2_easylogger_async_u16 length;
    open_cfw_g2_easylogger_async_u16 metadata;
    open_cfw_g2_easylogger_async_u8 level;
    char payload[OPEN_CFW_G2_EASYLOGGER_ASYNC_PAYLOAD_SIZE];
    open_cfw_g2_easylogger_async_u8 padding[3];
};

_Static_assert(
    sizeof(open_cfw_g2_easylogger_async_u8) == 1U
        && sizeof(open_cfw_g2_easylogger_async_u16) == 2U
        && sizeof(open_cfw_g2_easylogger_async_u32) == 4U,
    "G2 EasyLogger async integer ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_g2_easylogger_async_record) ==
        OPEN_CFW_G2_EASYLOGGER_ASYNC_RECORD_SIZE,
    "G2 EasyLogger async record stride changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_g2_easylogger_async_record,
        next
    ) == 0x00U,
    "G2 EasyLogger async next offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_g2_easylogger_async_record,
        state
    ) == 0x04U,
    "G2 EasyLogger async state offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_g2_easylogger_async_record,
        length
    ) == 0x08U,
    "G2 EasyLogger async length offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_g2_easylogger_async_record,
        metadata
    ) == 0x0AU,
    "G2 EasyLogger async metadata offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_g2_easylogger_async_record,
        level
    ) == 0x0CU,
    "G2 EasyLogger async level offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_g2_easylogger_async_record,
        payload
    ) == 0x0DU,
    "G2 EasyLogger async payload offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_g2_easylogger_async_record,
        padding
    ) == 0x10DU,
    "G2 EasyLogger async padding offset changed"
);

extern volatile open_cfw_g2_easylogger_async_u8
    open_cfw_retained_easylogger_async_ready;
extern volatile open_cfw_g2_easylogger_async_u8
    open_cfw_retained_easylogger_async_default_metadata;

extern struct open_cfw_g2_easylogger_async_record *
open_cfw_retained_easylogger_async_record_allocate(void);
extern open_cfw_g2_easylogger_async_u32
open_cfw_retained_easylogger_async_record_enqueue(
    struct open_cfw_g2_easylogger_async_record *record
);
extern void open_cfw_retained_easylogger_async_diagnostic(
    const char *message
);

static const char open_cfw_g2_easylogger_async_enqueue_error[] =
    "error!!!!!!elog_async_ext_output: enqueue_log failed\n";

__attribute__((used, noinline))
open_cfw_g2_easylogger_async_u32
open_cfw_g2_easylogger_async_record_build_single_owner(
    const char *buffer,
    open_cfw_g2_easylogger_async_u32 length,
    open_cfw_g2_easylogger_async_u32 metadata,
    open_cfw_g2_easylogger_async_u32 level
)
{
    struct open_cfw_g2_easylogger_async_record *record;
    open_cfw_g2_easylogger_async_u32 index;
    open_cfw_g2_easylogger_async_u8 record_metadata;

    if (
        open_cfw_retained_easylogger_async_ready == 0U
        || buffer == (const char *)0
        || length == 0U
    ) {
        return 0U;
    }

    record_metadata = (open_cfw_g2_easylogger_async_u8)metadata;
    if (record_metadata == 0U) {
        record_metadata =
            open_cfw_retained_easylogger_async_default_metadata;
    }
    if (length >= OPEN_CFW_G2_EASYLOGGER_ASYNC_PAYLOAD_SIZE) {
        length = OPEN_CFW_G2_EASYLOGGER_ASYNC_MAX_LENGTH;
    }

    record = open_cfw_retained_easylogger_async_record_allocate();
    if (record == (struct open_cfw_g2_easylogger_async_record *)0) {
        return 0U;
    }

    for (index = 0U; index < length; index++) {
        record->payload[index] = buffer[index];
    }
    record->payload[length] = '\0';
    record->length = (open_cfw_g2_easylogger_async_u16)length;
    record->metadata =
        (open_cfw_g2_easylogger_async_u16)record_metadata;
    record->level = (open_cfw_g2_easylogger_async_u8)level;

    if (
        open_cfw_retained_easylogger_async_record_enqueue(record) == 0U
    ) {
        /*
         * Corrected ownership: retained enqueue has already recycled the
         * record on its only reachable failure for a nonnull input.
         */
        open_cfw_retained_easylogger_async_diagnostic(
            open_cfw_g2_easylogger_async_enqueue_error
        );
    }
    return 0U;
}
