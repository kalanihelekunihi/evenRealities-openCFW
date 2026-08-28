/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room recovery of the bounded library and G2
 * transport seams used by EasyLogger elog_hexdump in firmware 2.2.6.10.
 * This is not a production overlay input.
 */

#include "runtime_easylogger_hexdump_seams.h"

enum {
    OPEN_CFW_EASYLOGGER_HEXDUMP_RECORD_SIZE = 0x110U,
    OPEN_CFW_EASYLOGGER_HEXDUMP_PAYLOAD_SIZE = 0x100U,
    OPEN_CFW_EASYLOGGER_HEXDUMP_MAX_LENGTH = 0xFFU
};

_Static_assert(
    sizeof(open_cfw_easylogger_hexdump_seam_u8) == 1U
        && sizeof(open_cfw_easylogger_hexdump_seam_u16) == 2U
        && sizeof(open_cfw_easylogger_hexdump_seam_u32) == 4U,
    "G2 EasyLogger seam integer ABI changed"
);

struct open_cfw_easylogger_hexdump_record {
    open_cfw_easylogger_hexdump_seam_u32 next;
    open_cfw_easylogger_hexdump_seam_u32 state;
    open_cfw_easylogger_hexdump_seam_u16 length;
    open_cfw_easylogger_hexdump_seam_u16 metadata;
    open_cfw_easylogger_hexdump_seam_u8 reserved_level;
    char payload[OPEN_CFW_EASYLOGGER_HEXDUMP_PAYLOAD_SIZE];
    open_cfw_easylogger_hexdump_seam_u8 padding[3];
};

_Static_assert(
    sizeof(struct open_cfw_easylogger_hexdump_record) ==
        OPEN_CFW_EASYLOGGER_HEXDUMP_RECORD_SIZE,
    "G2 level-less EasyLogger record stride changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_hexdump_record, length) ==
        0x08U,
    "G2 level-less EasyLogger length offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_hexdump_record, metadata) ==
        0x0AU,
    "G2 level-less EasyLogger metadata offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_hexdump_record, payload) ==
        0x0DU,
    "G2 level-less EasyLogger payload offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_hexdump_record,
        reserved_level
    ) == 0x0CU,
    "G2 level-less EasyLogger reserved-level offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger_hexdump_record, padding) ==
        0x10DU,
    "G2 level-less EasyLogger padding offset changed"
);

extern volatile open_cfw_easylogger_hexdump_seam_u8
    open_cfw_retained_easylogger_async_ready;
extern volatile open_cfw_easylogger_hexdump_seam_u8
    open_cfw_retained_easylogger_async_default_metadata;
extern struct open_cfw_easylogger_hexdump_record *
open_cfw_retained_easylogger_async_record_allocate(void);
extern open_cfw_easylogger_hexdump_seam_u32
open_cfw_retained_easylogger_async_record_enqueue(
    struct open_cfw_easylogger_hexdump_record *record
);
extern void open_cfw_retained_easylogger_async_diagnostic(
    const char *message
);

static const char open_cfw_easylogger_hexdump_enqueue_error[] =
    "error!!!!!!elog_async_ext_output: enqueue_log failed\n";

__attribute__((noinline))
static void open_cfw_easylogger_hexdump_put(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 size,
    open_cfw_easylogger_hexdump_seam_u32 *length,
    char value
)
{
    if (size != 0U && *length < size - 1U) {
        buffer[*length] = value;
    }
    (*length)++;
}

__attribute__((noinline))
static void open_cfw_easylogger_hexdump_put_hex(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 size,
    open_cfw_easylogger_hexdump_seam_u32 *length,
    unsigned int value,
    unsigned int minimum_digits
)
{
    static const char digits[] = "0123456789ABCDEF";
    char reversed[8];
    unsigned int count = 0U;

    do {
        reversed[count++] = digits[value & 0x0FU];
        value >>= 4;
    } while (value != 0U);
    while (count < minimum_digits) {
        reversed[count++] = '0';
    }
    while (count != 0U) {
        open_cfw_easylogger_hexdump_put(
            buffer,
            size,
            length,
            reversed[--count]
        );
    }
}

__attribute__((used, noinline))
void *open_cfw_easylogger_hexdump_fill_source(
    void *destination,
    open_cfw_easylogger_hexdump_seam_u32 count,
    open_cfw_easylogger_hexdump_seam_u32 value
)
{
    open_cfw_easylogger_hexdump_seam_u8 *bytes =
        (open_cfw_easylogger_hexdump_seam_u8 *)destination;
    open_cfw_easylogger_hexdump_seam_u32 index;

    for (index = 0U; index < count; index++) {
        bytes[index] = (open_cfw_easylogger_hexdump_seam_u8)value;
    }
    return destination;
}

__attribute__((used, noinline))
int open_cfw_easylogger_hexdump_format_header_source(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 size,
    const char *name,
    unsigned int offset,
    unsigned int end
)
{
    static const char prefix[] = "D/HEX ";
    static const char middle[] = ": ";
    open_cfw_easylogger_hexdump_seam_u32 length = 0U;
    open_cfw_easylogger_hexdump_seam_u32 index;

    for (index = 0U; prefix[index] != '\0'; index++) {
        open_cfw_easylogger_hexdump_put(buffer, size, &length, prefix[index]);
    }
    for (index = 0U; name[index] != '\0'; index++) {
        open_cfw_easylogger_hexdump_put(buffer, size, &length, name[index]);
    }
    for (index = 0U; middle[index] != '\0'; index++) {
        open_cfw_easylogger_hexdump_put(buffer, size, &length, middle[index]);
    }
    open_cfw_easylogger_hexdump_put_hex(buffer, size, &length, offset, 4U);
    open_cfw_easylogger_hexdump_put(buffer, size, &length, '-');
    open_cfw_easylogger_hexdump_put_hex(buffer, size, &length, end, 4U);
    open_cfw_easylogger_hexdump_put(buffer, size, &length, ':');
    open_cfw_easylogger_hexdump_put(buffer, size, &length, ' ');
    if (size != 0U) {
        open_cfw_easylogger_hexdump_seam_u32 terminator =
            length < size ? length : size - 1U;
        buffer[terminator] = '\0';
    }
    return (int)length;
}

__attribute__((used, noinline))
void open_cfw_easylogger_hexdump_format_hex_source(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u8 value
)
{
    static const char digits[] = "0123456789ABCDEF";
    buffer[0] = digits[value >> 4];
    buffer[1] = digits[value & 0x0FU];
    buffer[2] = ' ';
    buffer[3] = '\0';
}

__attribute__((used, noinline))
void open_cfw_easylogger_hexdump_format_character_source(
    char *buffer,
    open_cfw_easylogger_hexdump_seam_u8 value
)
{
    buffer[0] = (char)value;
    buffer[1] = '\0';
}

__attribute__((used, noinline))
void open_cfw_easylogger_hexdump_blank_hex_source(char *buffer)
{
    open_cfw_easylogger_hexdump_seam_u32 index;
    buffer[0] = ' ';
    buffer[1] = ' ';
    buffer[2] = ' ';
    for (index = 3U; index < 8U; index++) {
        buffer[index] = '\0';
    }
}

__attribute__((used, noinline))
open_cfw_easylogger_hexdump_seam_u32
open_cfw_g2_easylogger_async_record_build_level_less(
    const char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 length,
    open_cfw_easylogger_hexdump_seam_u32 metadata
)
{
    struct open_cfw_easylogger_hexdump_record *record;
    open_cfw_easylogger_hexdump_seam_u32 index;
    open_cfw_easylogger_hexdump_seam_u8 record_metadata;

    if (
        open_cfw_retained_easylogger_async_ready == 0U
        || buffer == (const char *)0
        || length == 0U
    ) {
        return 0U;
    }
    record_metadata = (open_cfw_easylogger_hexdump_seam_u8)metadata;
    if (record_metadata == 0U) {
        record_metadata = open_cfw_retained_easylogger_async_default_metadata;
    }
    if (length >= OPEN_CFW_EASYLOGGER_HEXDUMP_PAYLOAD_SIZE) {
        length = OPEN_CFW_EASYLOGGER_HEXDUMP_MAX_LENGTH;
    }
    record = open_cfw_retained_easylogger_async_record_allocate();
    if (record == (struct open_cfw_easylogger_hexdump_record *)0) {
        return 0U;
    }
    for (index = 0U; index < length; index++) {
        record->payload[index] = buffer[index];
    }
    record->payload[length] = '\0';
    record->length = (open_cfw_easylogger_hexdump_seam_u16)length;
    record->metadata =
        (open_cfw_easylogger_hexdump_seam_u16)record_metadata;
    if (open_cfw_retained_easylogger_async_record_enqueue(record) == 0U) {
        /*
         * Deliberate openCFW safety correction: enqueue consumes the record
         * on both success and failure.  The authenticated stock builder calls
         * a recycler again after the retained enqueue has already recycled a
         * failed record; reproducing that double recycle would corrupt the
         * free list.  Ownership never returns to this builder after enqueue.
         */
        open_cfw_retained_easylogger_async_diagnostic(
            open_cfw_easylogger_hexdump_enqueue_error
        );
    }
    return 0U;
}

__attribute__((used, noinline))
void open_cfw_easylogger_hexdump_raw_submit_source(
    const char *buffer,
    open_cfw_easylogger_hexdump_seam_u32 length
)
{
    (void)open_cfw_g2_easylogger_async_record_build_level_less(
        buffer,
        length,
        0U
    );
}
