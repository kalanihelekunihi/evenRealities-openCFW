/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded SARC crash-report state, staging, finalization, and persistence
 * helpers matched to stock entries 0x0047D9FC through 0x0047DB02.
 */

typedef __UINTPTR_TYPE__ open_cfw_sarc_uintptr;

typedef unsigned int (*open_cfw_sarc_checksum_function)(
    const void *,
    unsigned int,
    unsigned int
);
typedef void *(*open_cfw_sarc_clear_function)(
    void *,
    unsigned int,
    unsigned int
);
typedef int (*open_cfw_sarc_vformat_function)(
    char *,
    unsigned int,
    const char *,
    void *
);
typedef void *(*open_cfw_sarc_copy_function)(
    void *,
    const void *,
    unsigned int
);
typedef int (*open_cfw_sarc_snprintf_function)(
    char *,
    unsigned int,
    const char *,
    ...
);

#ifndef OPEN_CFW_SARC_FILE_TYPE
#define OPEN_CFW_SARC_FILE_TYPE open_cfw_file
#endif

unsigned int open_cfw_log_format_dispatch(const char *format, ...);
OPEN_CFW_SARC_FILE_TYPE *open_cfw_file_open(
    const void *path,
    const char *mode
);
int open_cfw_file_close(OPEN_CFW_SARC_FILE_TYPE *stream);
unsigned int open_cfw_file_write(
    const void *buffer,
    unsigned int element_size,
    unsigned int element_count,
    OPEN_CFW_SARC_FILE_TYPE *stream
);
int open_cfw_file_seek(
    OPEN_CFW_SARC_FILE_TYPE *stream,
    int offset,
    unsigned int origin
);
int open_cfw_file_tell(OPEN_CFW_SARC_FILE_TYPE *stream);
int open_cfw_file_flush(OPEN_CFW_SARC_FILE_TYPE *stream);
int open_cfw_file_remove(const void *path);

struct open_cfw_sarc_state {
    unsigned int magic;
    unsigned int valid;
    unsigned int sequence;
    unsigned int payload_length;
    unsigned int flags;
    unsigned int header_checksum;
    unsigned char payload[4500];
};

#define OPEN_CFW_SARC_MAGIC 0x43524153U
#define OPEN_CFW_SARC_HEADER_BYTES 20U
#define OPEN_CFW_SARC_MAX_PAYLOAD_LENGTH 4500U
#define OPEN_CFW_SARC_MAX_REPORT_LENGTH 4499U
#define OPEN_CFW_SARC_STATE_BYTES 4524U

#ifndef OPEN_CFW_SARC_STATE
#define OPEN_CFW_SARC_STATE \
    ((volatile struct open_cfw_sarc_state *)0x20075048U)
#endif
#ifndef OPEN_CFW_SARC_CHECKSUM
#define OPEN_CFW_SARC_CHECKSUM(data, size, seed) \
    (((open_cfw_sarc_checksum_function) \
        (open_cfw_sarc_uintptr)0x004D34C5U)( \
            (data), \
            (size), \
            (seed) \
        ))
#endif
#ifndef OPEN_CFW_SARC_CLEAR
#define OPEN_CFW_SARC_CLEAR(destination, size, value) \
    (((open_cfw_sarc_clear_function) \
        (open_cfw_sarc_uintptr)0x0043C0E5U)( \
            (destination), \
            (size), \
            (value) \
        ))
#endif
#ifndef OPEN_CFW_SARC_REPORT_LENGTH
#define OPEN_CFW_SARC_REPORT_LENGTH \
    (*(volatile unsigned int *)(void *)0x200743A4U)
#endif
#ifndef OPEN_CFW_SARC_REPORT_BUFFER
#define OPEN_CFW_SARC_REPORT_BUFFER \
    ((volatile unsigned char *)(void *)0x2005CE68U)
#endif
#ifndef OPEN_CFW_SARC_FORMAT_ARGUMENT_CURSOR
#define OPEN_CFW_SARC_FORMAT_ARGUMENT_CURSOR(arguments) \
    ((void *)(arguments).__ap)
#endif
#ifndef OPEN_CFW_SARC_VFORMAT
#define OPEN_CFW_SARC_VFORMAT( \
    destination, size, format, arguments \
) \
    (((open_cfw_sarc_vformat_function) \
        (open_cfw_sarc_uintptr)0x0044B76DU)( \
            (destination), \
            (size), \
            (format), \
            (arguments) \
        ))
#endif
#ifndef OPEN_CFW_SARC_COPY
#define OPEN_CFW_SARC_COPY(destination, source, size) \
    (((open_cfw_sarc_copy_function) \
        (open_cfw_sarc_uintptr)0x00439BE5U)( \
            (destination), \
            (source), \
            (size) \
        ))
#endif
#ifndef OPEN_CFW_SARC_SNPRINTF
#define OPEN_CFW_SARC_SNPRINTF(destination, size, format, ...) \
    (((open_cfw_sarc_snprintf_function) \
        (open_cfw_sarc_uintptr)0x0044B729U)( \
            (destination), \
            (size), \
            (format), \
            __VA_ARGS__ \
        ))
#endif
#ifndef OPEN_CFW_SARC_LOG
#define OPEN_CFW_SARC_LOG(...) open_cfw_log_format_dispatch(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_SARC_FILE_OPEN
#define OPEN_CFW_SARC_FILE_OPEN(path, mode) \
    open_cfw_file_open((path), (mode))
#endif
#ifndef OPEN_CFW_SARC_FILE_CLOSE
#define OPEN_CFW_SARC_FILE_CLOSE(stream) open_cfw_file_close((stream))
#endif
#ifndef OPEN_CFW_SARC_FILE_WRITE
#define OPEN_CFW_SARC_FILE_WRITE(buffer, size, count, stream) \
    open_cfw_file_write((buffer), (size), (count), (stream))
#endif
#ifndef OPEN_CFW_SARC_FILE_SEEK
#define OPEN_CFW_SARC_FILE_SEEK(stream, offset, origin) \
    open_cfw_file_seek((stream), (offset), (origin))
#endif
#ifndef OPEN_CFW_SARC_FILE_TELL
#define OPEN_CFW_SARC_FILE_TELL(stream) open_cfw_file_tell((stream))
#endif
#ifndef OPEN_CFW_SARC_FILE_FLUSH
#define OPEN_CFW_SARC_FILE_FLUSH(stream) open_cfw_file_flush((stream))
#endif
#ifndef OPEN_CFW_SARC_FILE_REMOVE
#define OPEN_CFW_SARC_FILE_REMOVE(path) open_cfw_file_remove((path))
#endif
#ifndef OPEN_CFW_SARC_PATH_BUFFER
#define OPEN_CFW_SARC_PATH_BUFFER ((char *)(void *)0x200E3B00U)
#endif
#ifndef OPEN_CFW_SARC_HEADER_BUFFER
#define OPEN_CFW_SARC_HEADER_BUFFER ((char *)(void *)0x200E3B80U)
#endif
#ifndef OPEN_CFW_SARC_FOOTER_BUFFER
#define OPEN_CFW_SARC_FOOTER_BUFFER ((char *)(void *)0x200E3D80U)
#endif

static const char open_cfw_sarc_read_mode[] = "r";
static const char open_cfw_sarc_append_mode[] = "a+";
static const char open_cfw_sarc_unavailable[] = "N/A";
static const char open_cfw_sarc_available[] = "Available";
static const char open_cfw_sarc_filename_format[] = "%s/hardfault.txt";
static const char open_cfw_sarc_too_many_format[] =
    "[CRASH] Too many crashes (%u), entering safe mode\n";
static const char open_cfw_sarc_size_format[] =
    "[CRASH] hardfault.txt size exceeded 100KB, deleted and recreating\n";
static const char open_cfw_sarc_open_failure_format[] =
    "[CRASH] Failed to open %s\n";
static const char open_cfw_sarc_write_warning_format[] =
    "[CRASH] Warning: only wrote %u/%u bytes\n";
static const char open_cfw_sarc_recovered_format[] =
    "[CRASH] Crash info #%u recovered to %s\n";
static const char open_cfw_sarc_header_format[] =
    "\n========================================\n"
    "===== CRASH #%u =====\n"
    "Timestamp: %s\n"
    "Data Length: %u bytes\n"
    "CRC32: 0x%08X\n"
    "----------------------------------------\n\n";
static const char open_cfw_sarc_footer_format[] =
    "\n========================================\n"
    "===== END CRASH #%u =====\n"
    "========================================\n\n";

__attribute__((used, noinline))
unsigned int open_cfw_sarc_header_checksum(
    const struct open_cfw_sarc_state *state
)
{
    if (state->payload_length > OPEN_CFW_SARC_MAX_PAYLOAD_LENGTH) {
        return 0U;
    }
    return OPEN_CFW_SARC_CHECKSUM(
        state,
        OPEN_CFW_SARC_HEADER_BYTES,
        0U
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_sarc_state_valid(void)
{
    volatile struct open_cfw_sarc_state *state = OPEN_CFW_SARC_STATE;
    unsigned int calculated;

    if (state->magic != OPEN_CFW_SARC_MAGIC) {
        return 0U;
    }
    if (state->valid != 1U) {
        return 0U;
    }
    if (
        state->payload_length == 0U
        || state->payload_length > OPEN_CFW_SARC_MAX_PAYLOAD_LENGTH
    ) {
        return 0U;
    }

    calculated = open_cfw_sarc_header_checksum(
        (const struct open_cfw_sarc_state *)state
    );
    return calculated == state->header_checksum ? 1U : 0U;
}

__attribute__((used, noinline))
void open_cfw_sarc_state_initialize(void)
{
    volatile struct open_cfw_sarc_state *state = OPEN_CFW_SARC_STATE;

    if (state->magic == OPEN_CFW_SARC_MAGIC) {
        return;
    }
    (void)OPEN_CFW_SARC_CLEAR(
        (void *)state,
        OPEN_CFW_SARC_STATE_BYTES,
        0U
    );
    state->sequence = 0U;
}

__attribute__((used, noinline))
void open_cfw_sarc_report_append(const char *format, ...)
{
    unsigned int current;
    unsigned int remaining;
    int formatted;
    __builtin_va_list arguments;

    if (format == (const char *)0) {
        return;
    }

    current = OPEN_CFW_SARC_REPORT_LENGTH;
    remaining = OPEN_CFW_SARC_MAX_REPORT_LENGTH - current;
    if (remaining == 0U) {
        return;
    }

    __builtin_va_start(arguments, format);
    formatted = OPEN_CFW_SARC_VFORMAT(
        (char *)(void *)(OPEN_CFW_SARC_REPORT_BUFFER + current),
        remaining + 1U,
        format,
        OPEN_CFW_SARC_FORMAT_ARGUMENT_CURSOR(arguments)
    );
    __builtin_va_end(arguments);

    if (formatted > 0) {
        OPEN_CFW_SARC_REPORT_LENGTH = current + (
            (unsigned int)formatted > remaining
                ? remaining
                : (unsigned int)formatted
        );
    }
    OPEN_CFW_SARC_REPORT_BUFFER[OPEN_CFW_SARC_REPORT_LENGTH] = 0U;
}

__attribute__((used, noinline))
void open_cfw_sarc_report_finalize(void)
{
    volatile struct open_cfw_sarc_state *state = OPEN_CFW_SARC_STATE;
    unsigned int length = OPEN_CFW_SARC_REPORT_LENGTH;

    if (length == 0U) {
        return;
    }

    state->magic = OPEN_CFW_SARC_MAGIC;
    state->valid = 1U;
    state->sequence += 1U;
    state->payload_length = length;
    state->flags = 0U;
    (void)OPEN_CFW_SARC_COPY(
        (void *)(open_cfw_sarc_uintptr)&state->payload[0],
        (const void *)(open_cfw_sarc_uintptr)OPEN_CFW_SARC_REPORT_BUFFER,
        length
    );
    state->payload[length] = 0U;
    state->header_checksum = open_cfw_sarc_header_checksum(
        (const struct open_cfw_sarc_state *)state
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_sarc_report_persist(const char *directory)
{
    volatile struct open_cfw_sarc_state *state = OPEN_CFW_SARC_STATE;
    OPEN_CFW_SARC_FILE_TYPE *stream;
    const char *availability;
    unsigned int sequence;
    unsigned int written;
    int formatted;
    int existing_size;

    if (open_cfw_sarc_state_valid() == 0U) {
        return 0U;
    }

    if (state->sequence > 10U) {
        OPEN_CFW_SARC_LOG(
            open_cfw_sarc_too_many_format,
            state->sequence
        );
    }

    (void)OPEN_CFW_SARC_SNPRINTF(
        OPEN_CFW_SARC_PATH_BUFFER,
        128U,
        open_cfw_sarc_filename_format,
        directory
    );
    stream = OPEN_CFW_SARC_FILE_OPEN(
        OPEN_CFW_SARC_PATH_BUFFER,
        open_cfw_sarc_read_mode
    );
    if (stream != (OPEN_CFW_SARC_FILE_TYPE *)0) {
        (void)OPEN_CFW_SARC_FILE_SEEK(stream, 0, 2U);
        existing_size = OPEN_CFW_SARC_FILE_TELL(stream);
        (void)OPEN_CFW_SARC_FILE_CLOSE(stream);
        if (existing_size >= 102401) {
            (void)OPEN_CFW_SARC_FILE_REMOVE(
                OPEN_CFW_SARC_PATH_BUFFER
            );
            OPEN_CFW_SARC_LOG(open_cfw_sarc_size_format);
        }
    }

    stream = OPEN_CFW_SARC_FILE_OPEN(
        OPEN_CFW_SARC_PATH_BUFFER,
        open_cfw_sarc_append_mode
    );
    if (stream == (OPEN_CFW_SARC_FILE_TYPE *)0) {
        OPEN_CFW_SARC_LOG(
            open_cfw_sarc_open_failure_format,
            OPEN_CFW_SARC_PATH_BUFFER
        );
    } else {
        availability = state->flags == 0U
            ? open_cfw_sarc_unavailable
            : open_cfw_sarc_available;
        formatted = OPEN_CFW_SARC_SNPRINTF(
            OPEN_CFW_SARC_HEADER_BUFFER,
            512U,
            open_cfw_sarc_header_format,
            state->sequence,
            availability,
            state->payload_length,
            state->header_checksum
        );
        if (formatted > 0) {
            (void)OPEN_CFW_SARC_FILE_WRITE(
                OPEN_CFW_SARC_HEADER_BUFFER,
                1U,
                (unsigned int)formatted,
                stream
            );
        }
        written = OPEN_CFW_SARC_FILE_WRITE(
            (const void *)(open_cfw_sarc_uintptr)&state->payload[0],
            1U,
            state->payload_length,
            stream
        );
        if (written != state->payload_length) {
            OPEN_CFW_SARC_LOG(
                open_cfw_sarc_write_warning_format,
                written,
                state->payload_length
            );
        }
        formatted = OPEN_CFW_SARC_SNPRINTF(
            OPEN_CFW_SARC_FOOTER_BUFFER,
            256U,
            open_cfw_sarc_footer_format,
            state->sequence,
            availability,
            state->payload_length,
            state->header_checksum
        );
        if (formatted > 0) {
            (void)OPEN_CFW_SARC_FILE_WRITE(
                OPEN_CFW_SARC_FOOTER_BUFFER,
                1U,
                (unsigned int)formatted,
                stream
            );
        }
        (void)OPEN_CFW_SARC_FILE_FLUSH(stream);
        (void)OPEN_CFW_SARC_FILE_CLOSE(stream);
        OPEN_CFW_SARC_LOG(
            open_cfw_sarc_recovered_format,
            state->sequence,
            OPEN_CFW_SARC_PATH_BUFFER
        );
    }

    sequence = state->sequence;
    (void)OPEN_CFW_SARC_CLEAR(
        (void *)state,
        OPEN_CFW_SARC_STATE_BYTES,
        0U
    );
    state->sequence = sequence;
    return 1U;
}

#undef OPEN_CFW_SARC_FOOTER_BUFFER
#undef OPEN_CFW_SARC_HEADER_BUFFER
#undef OPEN_CFW_SARC_PATH_BUFFER
#undef OPEN_CFW_SARC_FILE_REMOVE
#undef OPEN_CFW_SARC_FILE_FLUSH
#undef OPEN_CFW_SARC_FILE_TELL
#undef OPEN_CFW_SARC_FILE_SEEK
#undef OPEN_CFW_SARC_FILE_WRITE
#undef OPEN_CFW_SARC_FILE_CLOSE
#undef OPEN_CFW_SARC_FILE_OPEN
#undef OPEN_CFW_SARC_LOG
#undef OPEN_CFW_SARC_SNPRINTF
#undef OPEN_CFW_SARC_FILE_TYPE
#undef OPEN_CFW_SARC_COPY
#undef OPEN_CFW_SARC_VFORMAT
#undef OPEN_CFW_SARC_FORMAT_ARGUMENT_CURSOR
#undef OPEN_CFW_SARC_REPORT_BUFFER
#undef OPEN_CFW_SARC_REPORT_LENGTH
#undef OPEN_CFW_SARC_CLEAR
#undef OPEN_CFW_SARC_CHECKSUM
#undef OPEN_CFW_SARC_STATE
