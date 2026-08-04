/*
 * Native host oracle for the bounded SARC state helpers.
 */

#include <limits.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

unsigned char open_cfw_test_sarc_state[4524]
    __attribute__((aligned(4)));
unsigned int open_cfw_test_sarc_checksum_result;
unsigned int open_cfw_test_sarc_checksum_calls;
unsigned long open_cfw_test_sarc_checksum_data;
unsigned int open_cfw_test_sarc_checksum_size;
unsigned int open_cfw_test_sarc_checksum_seed;
unsigned int open_cfw_test_sarc_clear_calls;
unsigned long open_cfw_test_sarc_clear_destination;
unsigned int open_cfw_test_sarc_clear_size;
unsigned int open_cfw_test_sarc_clear_value;
unsigned char open_cfw_test_sarc_report_buffer[4600]
    __attribute__((aligned(4)));
unsigned int open_cfw_test_sarc_report_length;
int open_cfw_test_sarc_vformat_result = INT_MIN;
unsigned int open_cfw_test_sarc_vformat_calls;
unsigned long open_cfw_test_sarc_vformat_destination;
unsigned int open_cfw_test_sarc_vformat_size;
unsigned long open_cfw_test_sarc_vformat_format;
unsigned int open_cfw_test_sarc_copy_calls;
unsigned long open_cfw_test_sarc_copy_destination;
unsigned long open_cfw_test_sarc_copy_source;
unsigned int open_cfw_test_sarc_copy_size;
char open_cfw_test_sarc_path_buffer[128];
char open_cfw_test_sarc_header_buffer[512];
char open_cfw_test_sarc_footer_buffer[256];
unsigned int open_cfw_test_sarc_trace[128];
unsigned long open_cfw_test_sarc_trace_args[128 * 4];
unsigned int open_cfw_test_sarc_trace_count;
unsigned long open_cfw_test_sarc_open_results[2];
unsigned int open_cfw_test_sarc_open_calls;
int open_cfw_test_sarc_tell_result;
unsigned int open_cfw_test_sarc_write_results[3];
unsigned int open_cfw_test_sarc_write_calls;
int open_cfw_test_sarc_snprintf_results[3];
unsigned int open_cfw_test_sarc_snprintf_calls;

enum {
    OPEN_CFW_TEST_SARC_TRACE_SNPRINTF = 1,
    OPEN_CFW_TEST_SARC_TRACE_OPEN = 2,
    OPEN_CFW_TEST_SARC_TRACE_SEEK = 3,
    OPEN_CFW_TEST_SARC_TRACE_TELL = 4,
    OPEN_CFW_TEST_SARC_TRACE_CLOSE = 5,
    OPEN_CFW_TEST_SARC_TRACE_REMOVE = 6,
    OPEN_CFW_TEST_SARC_TRACE_WRITE = 7,
    OPEN_CFW_TEST_SARC_TRACE_FLUSH = 8,
    OPEN_CFW_TEST_SARC_TRACE_LOG = 9,
    OPEN_CFW_TEST_SARC_TRACE_CLEAR = 10
};

static void open_cfw_test_sarc_record(
    unsigned int code,
    unsigned long first,
    unsigned long second,
    unsigned long third,
    unsigned long fourth
)
{
    unsigned int index = open_cfw_test_sarc_trace_count++;

    if (index < 128U) {
        open_cfw_test_sarc_trace[index] = code;
        open_cfw_test_sarc_trace_args[index * 4U] = first;
        open_cfw_test_sarc_trace_args[index * 4U + 1U] = second;
        open_cfw_test_sarc_trace_args[index * 4U + 2U] = third;
        open_cfw_test_sarc_trace_args[index * 4U + 3U] = fourth;
    }
}

static unsigned int open_cfw_test_sarc_checksum(
    const void *data,
    unsigned int size,
    unsigned int seed
)
{
    open_cfw_test_sarc_checksum_calls += 1U;
    open_cfw_test_sarc_checksum_data = (unsigned long)data;
    open_cfw_test_sarc_checksum_size = size;
    open_cfw_test_sarc_checksum_seed = seed;
    return open_cfw_test_sarc_checksum_result;
}

static void *open_cfw_test_sarc_clear(
    void *destination,
    unsigned int size,
    unsigned int value
)
{
    open_cfw_test_sarc_clear_calls += 1U;
    open_cfw_test_sarc_clear_destination = (unsigned long)destination;
    open_cfw_test_sarc_clear_size = size;
    open_cfw_test_sarc_clear_value = value;
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_CLEAR,
        (unsigned long)destination,
        size,
        value,
        0U
    );
    memset(destination, (int)(value & 0xFFU), size);
    return destination;
}

static int open_cfw_test_sarc_vformat(
    char *destination,
    unsigned int size,
    const char *format,
    va_list arguments
)
{
    va_list copied_arguments;
    int result;

    open_cfw_test_sarc_vformat_calls += 1U;
    open_cfw_test_sarc_vformat_destination =
        (unsigned long)destination;
    open_cfw_test_sarc_vformat_size = size;
    open_cfw_test_sarc_vformat_format = (unsigned long)format;
    if (open_cfw_test_sarc_vformat_result != INT_MIN) {
        if (size != 0U) {
            destination[0] = 'X';
            destination[size - 1U] = '\0';
        }
        return open_cfw_test_sarc_vformat_result;
    }

    va_copy(copied_arguments, arguments);
    result = vsnprintf(
        destination,
        (size_t)size,
        format,
        copied_arguments
    );
    va_end(copied_arguments);
    return result;
}

static void *open_cfw_test_sarc_copy(
    void *destination,
    const void *source,
    unsigned int size
)
{
    open_cfw_test_sarc_copy_calls += 1U;
    open_cfw_test_sarc_copy_destination = (unsigned long)destination;
    open_cfw_test_sarc_copy_source = (unsigned long)source;
    open_cfw_test_sarc_copy_size = size;
    return memcpy(destination, source, size);
}

struct open_cfw_sarc_file;

static int open_cfw_test_sarc_snprintf(
    char *destination,
    unsigned int size,
    const char *format,
    ...
)
{
    unsigned int index = open_cfw_test_sarc_snprintf_calls++;
    va_list arguments;
    int result;

    va_start(arguments, format);
    result = vsnprintf(destination, (size_t)size, format, arguments);
    va_end(arguments);
    if (
        index < 3U
        && open_cfw_test_sarc_snprintf_results[index] != INT_MIN
    ) {
        result = open_cfw_test_sarc_snprintf_results[index];
    }
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_SNPRINTF,
        (unsigned long)destination,
        size,
        (unsigned long)format,
        (unsigned long)(unsigned int)result
    );
    return result;
}

static struct open_cfw_sarc_file *open_cfw_test_sarc_file_open(
    const void *path,
    const char *mode
)
{
    unsigned int index = open_cfw_test_sarc_open_calls++;
    unsigned long result = index < 2U
        ? open_cfw_test_sarc_open_results[index]
        : 0U;

    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_OPEN,
        (unsigned long)path,
        (unsigned long)mode,
        result,
        0U
    );
    return (struct open_cfw_sarc_file *)result;
}

static int open_cfw_test_sarc_file_close(
    struct open_cfw_sarc_file *stream
)
{
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_CLOSE,
        (unsigned long)stream,
        0U,
        0U,
        0U
    );
    return -77;
}

static unsigned int open_cfw_test_sarc_file_write(
    const void *buffer,
    unsigned int size,
    unsigned int count,
    struct open_cfw_sarc_file *stream
)
{
    unsigned int index = open_cfw_test_sarc_write_calls++;
    unsigned int result = (
        index < 3U
        && open_cfw_test_sarc_write_results[index] != UINT_MAX
    )
        ? open_cfw_test_sarc_write_results[index]
        : count;

    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_WRITE,
        (unsigned long)buffer,
        size,
        count,
        (unsigned long)stream
    );
    return result;
}

static int open_cfw_test_sarc_file_seek(
    struct open_cfw_sarc_file *stream,
    int offset,
    unsigned int origin
)
{
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_SEEK,
        (unsigned long)stream,
        (unsigned long)(unsigned int)offset,
        origin,
        0U
    );
    return -88;
}

static int open_cfw_test_sarc_file_tell(
    struct open_cfw_sarc_file *stream
)
{
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_TELL,
        (unsigned long)stream,
        (unsigned long)(unsigned int)open_cfw_test_sarc_tell_result,
        0U,
        0U
    );
    return open_cfw_test_sarc_tell_result;
}

static int open_cfw_test_sarc_file_flush(
    struct open_cfw_sarc_file *stream
)
{
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_FLUSH,
        (unsigned long)stream,
        0U,
        0U,
        0U
    );
    return -99;
}

static int open_cfw_test_sarc_file_remove(const void *path)
{
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_REMOVE,
        (unsigned long)path,
        0U,
        0U,
        0U
    );
    return -66;
}

static unsigned int open_cfw_test_sarc_log(const char *format, ...)
{
    va_list arguments;
    unsigned int kind = 0U;
    unsigned long first = 0U;
    unsigned long second = 0U;

    va_start(arguments, format);
    if (strstr(format, "Too many crashes") != (char *)0) {
        kind = 1U;
        first = va_arg(arguments, unsigned int);
    } else if (strstr(format, "size exceeded") != (char *)0) {
        kind = 2U;
    } else if (strstr(format, "Failed to open") != (char *)0) {
        kind = 3U;
        first = (unsigned long)va_arg(arguments, char *);
    } else if (strstr(format, "only wrote") != (char *)0) {
        kind = 4U;
        first = va_arg(arguments, unsigned int);
        second = va_arg(arguments, unsigned int);
    } else if (strstr(format, "recovered to") != (char *)0) {
        kind = 5U;
        first = va_arg(arguments, unsigned int);
        second = (unsigned long)va_arg(arguments, char *);
    }
    va_end(arguments);
    open_cfw_test_sarc_record(
        OPEN_CFW_TEST_SARC_TRACE_LOG,
        kind,
        first,
        second,
        (unsigned long)format
    );
    return 0xA5A55A5AU;
}

#define OPEN_CFW_SARC_STATE \
    ((volatile struct open_cfw_sarc_state *)open_cfw_test_sarc_state)
#define OPEN_CFW_SARC_CHECKSUM(data, size, seed) \
    open_cfw_test_sarc_checksum((data), (size), (seed))
#define OPEN_CFW_SARC_CLEAR(destination, size, value) \
    open_cfw_test_sarc_clear((destination), (size), (value))
#define OPEN_CFW_SARC_REPORT_LENGTH open_cfw_test_sarc_report_length
#define OPEN_CFW_SARC_REPORT_BUFFER open_cfw_test_sarc_report_buffer
#define OPEN_CFW_SARC_FORMAT_ARGUMENT_CURSOR(arguments) (arguments)
#define OPEN_CFW_SARC_VFORMAT(destination, size, format, arguments) \
    open_cfw_test_sarc_vformat( \
        (destination), \
        (size), \
        (format), \
        (arguments) \
    )
#define OPEN_CFW_SARC_COPY(destination, source, size) \
    open_cfw_test_sarc_copy((destination), (source), (size))
#define OPEN_CFW_SARC_SNPRINTF(destination, size, format, ...) \
    open_cfw_test_sarc_snprintf( \
        (destination), \
        (size), \
        (format), \
        __VA_ARGS__ \
    )
#define OPEN_CFW_SARC_LOG(...) open_cfw_test_sarc_log(__VA_ARGS__)
#define OPEN_CFW_SARC_FILE_OPEN(path, mode) \
    open_cfw_test_sarc_file_open((path), (mode))
#define OPEN_CFW_SARC_FILE_CLOSE(stream) \
    open_cfw_test_sarc_file_close((stream))
#define OPEN_CFW_SARC_FILE_WRITE(buffer, size, count, stream) \
    open_cfw_test_sarc_file_write((buffer), (size), (count), (stream))
#define OPEN_CFW_SARC_FILE_SEEK(stream, offset, origin) \
    open_cfw_test_sarc_file_seek((stream), (offset), (origin))
#define OPEN_CFW_SARC_FILE_TELL(stream) \
    open_cfw_test_sarc_file_tell((stream))
#define OPEN_CFW_SARC_FILE_FLUSH(stream) \
    open_cfw_test_sarc_file_flush((stream))
#define OPEN_CFW_SARC_FILE_REMOVE(path) \
    open_cfw_test_sarc_file_remove((path))
#define OPEN_CFW_SARC_PATH_BUFFER open_cfw_test_sarc_path_buffer
#define OPEN_CFW_SARC_HEADER_BUFFER open_cfw_test_sarc_header_buffer
#define OPEN_CFW_SARC_FOOTER_BUFFER open_cfw_test_sarc_footer_buffer
#define OPEN_CFW_SARC_FILE_TYPE struct open_cfw_sarc_file
#include "../../components/apollo_main/core_overlay/sarc_state.c"

void open_cfw_test_sarc_report_append0(const char *format)
{
    open_cfw_sarc_report_append(format);
}

void open_cfw_test_sarc_report_append1(
    const char *format,
    unsigned int value
)
{
    open_cfw_sarc_report_append(format, value);
}

void open_cfw_test_sarc_report_append2(
    const char *format,
    unsigned int first,
    unsigned int second
)
{
    open_cfw_sarc_report_append(format, first, second);
}
