/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the EasyLogger tracepoint file-I/O cluster.
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    unsigned int count;
    unsigned int minimum_index;
    unsigned int maximum_index;
} open_cfw_test_tracepoint_io_directory_stats;

unsigned int open_cfw_test_tracepoint_io_sequence;
unsigned int open_cfw_test_tracepoint_io_next_index;
unsigned char open_cfw_test_tracepoint_io_initialized;
unsigned int open_cfw_test_tracepoint_io_active_index;
unsigned int open_cfw_test_tracepoint_io_active_size;
void *open_cfw_test_tracepoint_io_active_handle;

int open_cfw_test_tracepoint_io_scan_result;
unsigned int open_cfw_test_tracepoint_io_scan_count;
unsigned int open_cfw_test_tracepoint_io_scan_minimum;
unsigned int open_cfw_test_tracepoint_io_scan_maximum;
int open_cfw_test_tracepoint_io_persist_result;
unsigned int open_cfw_test_tracepoint_io_open_fail;
int open_cfw_test_tracepoint_io_close_result;
unsigned int open_cfw_test_tracepoint_io_write_result_first;
unsigned int open_cfw_test_tracepoint_io_write_result_second;
int open_cfw_test_tracepoint_io_flush_result;
int open_cfw_test_tracepoint_io_remove_result;

unsigned int open_cfw_test_tracepoint_io_format_calls;
unsigned int open_cfw_test_tracepoint_io_scan_calls;
unsigned int open_cfw_test_tracepoint_io_persist_calls;
unsigned int open_cfw_test_tracepoint_io_open_calls;
unsigned int open_cfw_test_tracepoint_io_close_calls;
unsigned int open_cfw_test_tracepoint_io_write_calls;
unsigned int open_cfw_test_tracepoint_io_flush_calls;
unsigned int open_cfw_test_tracepoint_io_remove_calls;
unsigned int open_cfw_test_tracepoint_io_header_calls;

unsigned int open_cfw_test_tracepoint_io_header_index;
unsigned int open_cfw_test_tracepoint_io_header_sequence;
unsigned int open_cfw_test_tracepoint_io_write_sizes[8];
unsigned int open_cfw_test_tracepoint_io_event_count;
unsigned int open_cfw_test_tracepoint_io_events[64];

char open_cfw_test_tracepoint_io_last_path[96];
char open_cfw_test_tracepoint_io_last_mode[8];
char open_cfw_test_tracepoint_io_removed_paths[8][96];
unsigned char open_cfw_test_tracepoint_io_write_data[8][128];

static unsigned int open_cfw_test_tracepoint_io_handle_storage;

enum {
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_SCAN = 1,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_FORMAT = 2,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_REMOVE = 3,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_PERSIST = 4,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_OPEN = 5,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_HEADER = 6,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_WRITE = 7,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_CLOSE = 8,
    OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_FLUSH = 9
};

static void open_cfw_test_tracepoint_io_record_event(unsigned int event)
{
    if (open_cfw_test_tracepoint_io_event_count < 64U) {
        open_cfw_test_tracepoint_io_events[
            open_cfw_test_tracepoint_io_event_count
        ] = event;
    }
    open_cfw_test_tracepoint_io_event_count += 1U;
}

static void open_cfw_test_tracepoint_io_copy_text(
    char *destination,
    unsigned int capacity,
    const char *source
)
{
    unsigned int index = 0U;

    if (capacity == 0U) {
        return;
    }
    while (index + 1U < capacity && source[index] != '\0') {
        destination[index] = source[index];
        ++index;
    }
    destination[index] = '\0';
}

void open_cfw_test_tracepoint_io_reset(void)
{
    open_cfw_test_tracepoint_io_sequence = 1U;
    open_cfw_test_tracepoint_io_next_index = 1U;
    open_cfw_test_tracepoint_io_initialized = 1U;
    open_cfw_test_tracepoint_io_active_index = 0U;
    open_cfw_test_tracepoint_io_active_size = 0U;
    open_cfw_test_tracepoint_io_active_handle = NULL;
    open_cfw_test_tracepoint_io_scan_result = 0;
    open_cfw_test_tracepoint_io_scan_count = 0U;
    open_cfw_test_tracepoint_io_scan_minimum = 0xFFFFFFFFU;
    open_cfw_test_tracepoint_io_scan_maximum = 0U;
    open_cfw_test_tracepoint_io_persist_result = 0;
    open_cfw_test_tracepoint_io_open_fail = 0U;
    open_cfw_test_tracepoint_io_close_result = 0;
    open_cfw_test_tracepoint_io_write_result_first = 0xFFFFFFFFU;
    open_cfw_test_tracepoint_io_write_result_second = 0xFFFFFFFFU;
    open_cfw_test_tracepoint_io_flush_result = 0;
    open_cfw_test_tracepoint_io_remove_result = 0;
    open_cfw_test_tracepoint_io_format_calls = 0U;
    open_cfw_test_tracepoint_io_scan_calls = 0U;
    open_cfw_test_tracepoint_io_persist_calls = 0U;
    open_cfw_test_tracepoint_io_open_calls = 0U;
    open_cfw_test_tracepoint_io_close_calls = 0U;
    open_cfw_test_tracepoint_io_write_calls = 0U;
    open_cfw_test_tracepoint_io_flush_calls = 0U;
    open_cfw_test_tracepoint_io_remove_calls = 0U;
    open_cfw_test_tracepoint_io_header_calls = 0U;
    open_cfw_test_tracepoint_io_header_index = 0U;
    open_cfw_test_tracepoint_io_header_sequence = 0U;
    open_cfw_test_tracepoint_io_event_count = 0U;
    memset(open_cfw_test_tracepoint_io_write_sizes, 0, sizeof(
        open_cfw_test_tracepoint_io_write_sizes
    ));
    memset(open_cfw_test_tracepoint_io_events, 0, sizeof(
        open_cfw_test_tracepoint_io_events
    ));
    memset(open_cfw_test_tracepoint_io_last_path, 0, sizeof(
        open_cfw_test_tracepoint_io_last_path
    ));
    memset(open_cfw_test_tracepoint_io_last_mode, 0, sizeof(
        open_cfw_test_tracepoint_io_last_mode
    ));
    memset(open_cfw_test_tracepoint_io_removed_paths, 0, sizeof(
        open_cfw_test_tracepoint_io_removed_paths
    ));
    memset(open_cfw_test_tracepoint_io_write_data, 0, sizeof(
        open_cfw_test_tracepoint_io_write_data
    ));
}

void open_cfw_test_tracepoint_io_set_handle(unsigned int present)
{
    open_cfw_test_tracepoint_io_active_handle =
        present != 0U
            ? (void *)&open_cfw_test_tracepoint_io_handle_storage
            : NULL;
}

unsigned int open_cfw_test_tracepoint_io_has_handle(void)
{
    return open_cfw_test_tracepoint_io_active_handle != NULL ? 1U : 0U;
}

static void open_cfw_test_tracepoint_io_path_format(
    char *buffer,
    unsigned int size,
    unsigned int index
)
{
    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_FORMAT
    );
    open_cfw_test_tracepoint_io_format_calls += 1U;
    (void)snprintf(buffer, size, "/log/tp/tp_%u.bin", index);
    open_cfw_test_tracepoint_io_copy_text(
        open_cfw_test_tracepoint_io_last_path,
        sizeof(open_cfw_test_tracepoint_io_last_path),
        buffer
    );
}

static int open_cfw_test_tracepoint_io_directory_scan(void *raw_stats)
{
    open_cfw_test_tracepoint_io_directory_stats *stats =
        (open_cfw_test_tracepoint_io_directory_stats *)raw_stats;

    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_SCAN
    );
    open_cfw_test_tracepoint_io_scan_calls += 1U;
    stats->count = open_cfw_test_tracepoint_io_scan_count;
    stats->minimum_index = open_cfw_test_tracepoint_io_scan_minimum;
    stats->maximum_index = open_cfw_test_tracepoint_io_scan_maximum;
    return open_cfw_test_tracepoint_io_scan_result;
}

static int open_cfw_test_tracepoint_io_state_persist(void)
{
    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_PERSIST
    );
    open_cfw_test_tracepoint_io_persist_calls += 1U;
    return open_cfw_test_tracepoint_io_persist_result;
}

static void *open_cfw_test_tracepoint_io_file_open(
    const void *path,
    const char *mode
)
{
    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_OPEN
    );
    open_cfw_test_tracepoint_io_open_calls += 1U;
    open_cfw_test_tracepoint_io_copy_text(
        open_cfw_test_tracepoint_io_last_path,
        sizeof(open_cfw_test_tracepoint_io_last_path),
        (const char *)path
    );
    open_cfw_test_tracepoint_io_copy_text(
        open_cfw_test_tracepoint_io_last_mode,
        sizeof(open_cfw_test_tracepoint_io_last_mode),
        mode
    );
    if (open_cfw_test_tracepoint_io_open_fail != 0U) {
        return NULL;
    }
    return &open_cfw_test_tracepoint_io_handle_storage;
}

static int open_cfw_test_tracepoint_io_file_close(void *stream)
{
    (void)stream;
    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_CLOSE
    );
    open_cfw_test_tracepoint_io_close_calls += 1U;
    return open_cfw_test_tracepoint_io_close_result;
}

static unsigned int open_cfw_test_tracepoint_io_file_write(
    const void *buffer,
    unsigned int element_size,
    unsigned int element_count,
    void *stream
)
{
    unsigned int slot = open_cfw_test_tracepoint_io_write_calls;
    unsigned int bytes = element_size * element_count;
    unsigned int result = element_count;

    (void)stream;
    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_WRITE
    );
    if (slot < 8U) {
        unsigned int copied = bytes < 128U ? bytes : 128U;

        open_cfw_test_tracepoint_io_write_sizes[slot] = bytes;
        memcpy(
            open_cfw_test_tracepoint_io_write_data[slot],
            buffer,
            copied
        );
    }
    open_cfw_test_tracepoint_io_write_calls += 1U;
    if (
        slot == 0U
        && open_cfw_test_tracepoint_io_write_result_first != 0xFFFFFFFFU
    ) {
        result = open_cfw_test_tracepoint_io_write_result_first;
    }
    if (
        slot == 1U
        && open_cfw_test_tracepoint_io_write_result_second != 0xFFFFFFFFU
    ) {
        result = open_cfw_test_tracepoint_io_write_result_second;
    }
    return result;
}

static int open_cfw_test_tracepoint_io_file_flush(void *stream)
{
    (void)stream;
    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_FLUSH
    );
    open_cfw_test_tracepoint_io_flush_calls += 1U;
    return open_cfw_test_tracepoint_io_flush_result;
}

static int open_cfw_test_tracepoint_io_file_remove(const void *path)
{
    unsigned int slot = open_cfw_test_tracepoint_io_remove_calls;

    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_REMOVE
    );
    if (slot < 8U) {
        open_cfw_test_tracepoint_io_copy_text(
            open_cfw_test_tracepoint_io_removed_paths[slot],
            sizeof(open_cfw_test_tracepoint_io_removed_paths[slot]),
            (const char *)path
        );
    }
    open_cfw_test_tracepoint_io_remove_calls += 1U;
    if (open_cfw_test_tracepoint_io_remove_result != 0) {
        return open_cfw_test_tracepoint_io_remove_result;
    }
    if (open_cfw_test_tracepoint_io_scan_count > 0U) {
        open_cfw_test_tracepoint_io_scan_count -= 1U;
        open_cfw_test_tracepoint_io_scan_minimum += 1U;
    }
    return 0;
}

static void open_cfw_test_tracepoint_io_header_build(
    void *raw_header,
    unsigned int index,
    unsigned int sequence
)
{
    unsigned char *header = (unsigned char *)raw_header;
    unsigned int offset;

    open_cfw_test_tracepoint_io_record_event(
        OPEN_CFW_TEST_TRACEPOINT_IO_EVENT_HEADER
    );
    open_cfw_test_tracepoint_io_header_calls += 1U;
    open_cfw_test_tracepoint_io_header_index = index;
    open_cfw_test_tracepoint_io_header_sequence = sequence;
    for (offset = 0U; offset < 32U; ++offset) {
        header[offset] = (unsigned char)(0xA0U + offset);
    }
}

#define OPEN_CFW_TRACEPOINT_IO_PATH_FORMAT(buffer, size, index) \
    open_cfw_test_tracepoint_io_path_format((buffer), (size), (index))
#define OPEN_CFW_TRACEPOINT_IO_DIRECTORY_SCAN(stats) \
    open_cfw_test_tracepoint_io_directory_scan(stats)
#define OPEN_CFW_TRACEPOINT_IO_STATE_PERSIST() \
    open_cfw_test_tracepoint_io_state_persist()
#define OPEN_CFW_TRACEPOINT_IO_FILE_OPEN(path, mode) \
    open_cfw_test_tracepoint_io_file_open((path), (mode))
#define OPEN_CFW_TRACEPOINT_IO_FILE_CLOSE(stream) \
    open_cfw_test_tracepoint_io_file_close(stream)
#define OPEN_CFW_TRACEPOINT_IO_FILE_WRITE(buffer, size, count, stream) \
    open_cfw_test_tracepoint_io_file_write( \
        (buffer), \
        (size), \
        (count), \
        (stream) \
    )
#define OPEN_CFW_TRACEPOINT_IO_FILE_FLUSH(stream) \
    open_cfw_test_tracepoint_io_file_flush(stream)
#define OPEN_CFW_TRACEPOINT_IO_FILE_REMOVE(path) \
    open_cfw_test_tracepoint_io_file_remove(path)
#define OPEN_CFW_TRACEPOINT_IO_HEADER_BUILD(buffer, index, sequence) \
    open_cfw_test_tracepoint_io_header_build( \
        (buffer), \
        (index), \
        (sequence) \
    )
#define OPEN_CFW_TRACEPOINT_IO_SEQUENCE \
    open_cfw_test_tracepoint_io_sequence
#define OPEN_CFW_TRACEPOINT_IO_NEXT_INDEX \
    open_cfw_test_tracepoint_io_next_index
#define OPEN_CFW_TRACEPOINT_IO_INITIALIZED \
    open_cfw_test_tracepoint_io_initialized
#define OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX \
    open_cfw_test_tracepoint_io_active_index
#define OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE \
    open_cfw_test_tracepoint_io_active_size
#define OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE \
    open_cfw_test_tracepoint_io_active_handle
#define OPEN_CFW_TRACEPOINT_IO_FILE_TYPE void
#define OPEN_CFW_TRACEPOINT_IO_DIRECTORY_STATS_TYPE \
    open_cfw_test_tracepoint_io_directory_stats

#include "../../components/apollo_main/core_overlay/tracepoint_file_io.c"
