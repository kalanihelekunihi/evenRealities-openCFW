/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the EasyLogger tracepoint storage cluster.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[0x100U];
    unsigned char type;
} open_cfw_test_tracepoint_storage_dirent;

unsigned int open_cfw_test_tracepoint_storage_sequence;
unsigned int open_cfw_test_tracepoint_storage_next_index;
unsigned char open_cfw_test_tracepoint_storage_initialized;
unsigned int open_cfw_test_tracepoint_storage_active_index;
unsigned int open_cfw_test_tracepoint_storage_active_size;

unsigned char open_cfw_test_tracepoint_storage_state[16];
unsigned int open_cfw_test_tracepoint_storage_state_exists;
unsigned int open_cfw_test_tracepoint_storage_state_read_open_fail;
unsigned int open_cfw_test_tracepoint_storage_state_write_open_fail;
unsigned int open_cfw_test_tracepoint_storage_read_result;
unsigned int open_cfw_test_tracepoint_storage_write_result;
unsigned int open_cfw_test_tracepoint_storage_active_open_fail;
int open_cfw_test_tracepoint_storage_seek_result;
int open_cfw_test_tracepoint_storage_tell_result;
unsigned int open_cfw_test_tracepoint_storage_opendir_fail;

unsigned int open_cfw_test_tracepoint_storage_open_calls;
unsigned int open_cfw_test_tracepoint_storage_close_calls;
unsigned int open_cfw_test_tracepoint_storage_read_calls;
unsigned int open_cfw_test_tracepoint_storage_write_calls;
unsigned int open_cfw_test_tracepoint_storage_seek_calls;
unsigned int open_cfw_test_tracepoint_storage_tell_calls;
unsigned int open_cfw_test_tracepoint_storage_mkdir_calls;
unsigned int open_cfw_test_tracepoint_storage_opendir_calls;
unsigned int open_cfw_test_tracepoint_storage_readdir_calls;
unsigned int open_cfw_test_tracepoint_storage_closedir_calls;
unsigned int open_cfw_test_tracepoint_storage_format_calls;
unsigned int open_cfw_test_tracepoint_storage_parse_calls;

char open_cfw_test_tracepoint_storage_last_path[96];
char open_cfw_test_tracepoint_storage_last_mode[8];
char open_cfw_test_tracepoint_storage_last_formatted_path[96];

open_cfw_test_tracepoint_storage_dirent
    open_cfw_test_tracepoint_storage_entries[16];
unsigned int open_cfw_test_tracepoint_storage_entry_count;
unsigned int open_cfw_test_tracepoint_storage_entry_cursor;

static unsigned int open_cfw_test_tracepoint_storage_state_handle;
static unsigned int open_cfw_test_tracepoint_storage_active_handle;
static unsigned int open_cfw_test_tracepoint_storage_directory_handle;

static void open_cfw_test_tracepoint_storage_copy_text(
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

void open_cfw_test_tracepoint_storage_reset(void)
{
    open_cfw_test_tracepoint_storage_sequence = 0U;
    open_cfw_test_tracepoint_storage_next_index = 1U;
    open_cfw_test_tracepoint_storage_initialized = 0U;
    open_cfw_test_tracepoint_storage_active_index = 0U;
    open_cfw_test_tracepoint_storage_active_size = 0U;
    memset(open_cfw_test_tracepoint_storage_state, 0, 16U);
    open_cfw_test_tracepoint_storage_state_exists = 0U;
    open_cfw_test_tracepoint_storage_state_read_open_fail = 0U;
    open_cfw_test_tracepoint_storage_state_write_open_fail = 0U;
    open_cfw_test_tracepoint_storage_read_result = 16U;
    open_cfw_test_tracepoint_storage_write_result = 16U;
    open_cfw_test_tracepoint_storage_active_open_fail = 0U;
    open_cfw_test_tracepoint_storage_seek_result = 0;
    open_cfw_test_tracepoint_storage_tell_result = 0;
    open_cfw_test_tracepoint_storage_opendir_fail = 0U;
    open_cfw_test_tracepoint_storage_open_calls = 0U;
    open_cfw_test_tracepoint_storage_close_calls = 0U;
    open_cfw_test_tracepoint_storage_read_calls = 0U;
    open_cfw_test_tracepoint_storage_write_calls = 0U;
    open_cfw_test_tracepoint_storage_seek_calls = 0U;
    open_cfw_test_tracepoint_storage_tell_calls = 0U;
    open_cfw_test_tracepoint_storage_mkdir_calls = 0U;
    open_cfw_test_tracepoint_storage_opendir_calls = 0U;
    open_cfw_test_tracepoint_storage_readdir_calls = 0U;
    open_cfw_test_tracepoint_storage_closedir_calls = 0U;
    open_cfw_test_tracepoint_storage_format_calls = 0U;
    open_cfw_test_tracepoint_storage_parse_calls = 0U;
    memset(open_cfw_test_tracepoint_storage_last_path, 0, 96U);
    memset(open_cfw_test_tracepoint_storage_last_mode, 0, 8U);
    memset(open_cfw_test_tracepoint_storage_last_formatted_path, 0, 96U);
    memset(
        open_cfw_test_tracepoint_storage_entries,
        0,
        sizeof(open_cfw_test_tracepoint_storage_entries)
    );
    open_cfw_test_tracepoint_storage_entry_count = 0U;
    open_cfw_test_tracepoint_storage_entry_cursor = 0U;
}

void open_cfw_test_tracepoint_storage_set_entry(
    unsigned int slot,
    const char *name,
    unsigned int type
)
{
    if (slot >= 16U) {
        return;
    }
    open_cfw_test_tracepoint_storage_copy_text(
        open_cfw_test_tracepoint_storage_entries[slot].name,
        0x100U,
        name
    );
    open_cfw_test_tracepoint_storage_entries[slot].type =
        (unsigned char)type;
    if (open_cfw_test_tracepoint_storage_entry_count < slot + 1U) {
        open_cfw_test_tracepoint_storage_entry_count = slot + 1U;
    }
}

static unsigned int open_cfw_test_tracepoint_storage_strlen(
    const char *text
)
{
    return (unsigned int)strlen(text);
}

static int open_cfw_test_tracepoint_storage_format(
    char *buffer,
    unsigned int size,
    const char *format,
    unsigned int value
)
{
    int result;

    open_cfw_test_tracepoint_storage_format_calls += 1U;
    result = snprintf(buffer, size, format, value);
    open_cfw_test_tracepoint_storage_copy_text(
        open_cfw_test_tracepoint_storage_last_formatted_path,
        96U,
        buffer
    );
    return result;
}

static unsigned int open_cfw_test_tracepoint_storage_parse_unsigned(
    const char *text,
    char **end,
    int base
)
{
    open_cfw_test_tracepoint_storage_parse_calls += 1U;
    return (unsigned int)strtoul(text, end, base);
}

static void *open_cfw_test_tracepoint_storage_file_open(
    const void *path,
    const char *mode
)
{
    const char *text = (const char *)path;

    open_cfw_test_tracepoint_storage_open_calls += 1U;
    open_cfw_test_tracepoint_storage_copy_text(
        open_cfw_test_tracepoint_storage_last_path,
        96U,
        text
    );
    open_cfw_test_tracepoint_storage_copy_text(
        open_cfw_test_tracepoint_storage_last_mode,
        8U,
        mode
    );

    if (strcmp(text, "/log/tp/state.bin") == 0) {
        if (
            strcmp(mode, "rb") == 0
            && (
                open_cfw_test_tracepoint_storage_state_read_open_fail != 0U
                || open_cfw_test_tracepoint_storage_state_exists == 0U
            )
        ) {
            return NULL;
        }
        if (
            strcmp(mode, "wb") == 0
            && open_cfw_test_tracepoint_storage_state_write_open_fail != 0U
        ) {
            return NULL;
        }
        return &open_cfw_test_tracepoint_storage_state_handle;
    }

    if (open_cfw_test_tracepoint_storage_active_open_fail != 0U) {
        return NULL;
    }
    return &open_cfw_test_tracepoint_storage_active_handle;
}

static int open_cfw_test_tracepoint_storage_file_close(void *stream)
{
    (void)stream;
    open_cfw_test_tracepoint_storage_close_calls += 1U;
    return 0;
}

static unsigned int open_cfw_test_tracepoint_storage_file_read(
    void *buffer,
    unsigned int size,
    unsigned int count,
    void *stream
)
{
    unsigned int bytes = size * count;

    (void)stream;
    open_cfw_test_tracepoint_storage_read_calls += 1U;
    if (bytes > 16U) {
        bytes = 16U;
    }
    memcpy(buffer, open_cfw_test_tracepoint_storage_state, bytes);
    return open_cfw_test_tracepoint_storage_read_result;
}

static unsigned int open_cfw_test_tracepoint_storage_file_write(
    const void *buffer,
    unsigned int size,
    unsigned int count,
    void *stream
)
{
    unsigned int bytes = size * count;

    (void)stream;
    open_cfw_test_tracepoint_storage_write_calls += 1U;
    if (bytes > 16U) {
        bytes = 16U;
    }
    memcpy(open_cfw_test_tracepoint_storage_state, buffer, bytes);
    open_cfw_test_tracepoint_storage_state_exists = 1U;
    return open_cfw_test_tracepoint_storage_write_result;
}

static int open_cfw_test_tracepoint_storage_file_seek(
    void *stream,
    int offset,
    unsigned int origin
)
{
    (void)stream;
    (void)offset;
    (void)origin;
    open_cfw_test_tracepoint_storage_seek_calls += 1U;
    return open_cfw_test_tracepoint_storage_seek_result;
}

static int open_cfw_test_tracepoint_storage_file_tell(void *stream)
{
    (void)stream;
    open_cfw_test_tracepoint_storage_tell_calls += 1U;
    return open_cfw_test_tracepoint_storage_tell_result;
}

static int open_cfw_test_tracepoint_storage_file_mkdir(
    const void *path,
    unsigned int mode
)
{
    (void)path;
    (void)mode;
    open_cfw_test_tracepoint_storage_mkdir_calls += 1U;
    return 0;
}

static void *open_cfw_test_tracepoint_storage_file_opendir(
    const char *path
)
{
    (void)path;
    open_cfw_test_tracepoint_storage_opendir_calls += 1U;
    open_cfw_test_tracepoint_storage_entry_cursor = 0U;
    if (open_cfw_test_tracepoint_storage_opendir_fail != 0U) {
        return NULL;
    }
    return &open_cfw_test_tracepoint_storage_directory_handle;
}

static void *open_cfw_test_tracepoint_storage_file_readdir(
    void *directory
)
{
    (void)directory;
    open_cfw_test_tracepoint_storage_readdir_calls += 1U;
    if (
        open_cfw_test_tracepoint_storage_entry_cursor
        >= open_cfw_test_tracepoint_storage_entry_count
    ) {
        return NULL;
    }
    return &open_cfw_test_tracepoint_storage_entries[
        open_cfw_test_tracepoint_storage_entry_cursor++
    ];
}

static int open_cfw_test_tracepoint_storage_file_closedir(void *directory)
{
    (void)directory;
    open_cfw_test_tracepoint_storage_closedir_calls += 1U;
    return 0;
}

#define OPEN_CFW_TRACEPOINT_STORAGE_STRLEN(text) \
    open_cfw_test_tracepoint_storage_strlen(text)
#define OPEN_CFW_TRACEPOINT_STORAGE_FORMAT(buffer, size, format, value) \
    open_cfw_test_tracepoint_storage_format( \
        (buffer), \
        (size), \
        (format), \
        (value) \
    )
#define OPEN_CFW_TRACEPOINT_STORAGE_PARSE_UNSIGNED(text, end, base) \
    open_cfw_test_tracepoint_storage_parse_unsigned((text), (end), (base))
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPEN(path, mode) \
    open_cfw_test_tracepoint_storage_file_open((path), (mode))
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSE(stream) \
    open_cfw_test_tracepoint_storage_file_close(stream)
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_READ(buffer, size, count, stream) \
    open_cfw_test_tracepoint_storage_file_read( \
        (buffer), \
        (size), \
        (count), \
        (stream) \
    )
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_WRITE(buffer, size, count, stream) \
    open_cfw_test_tracepoint_storage_file_write( \
        (buffer), \
        (size), \
        (count), \
        (stream) \
    )
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_SEEK(stream, offset, origin) \
    open_cfw_test_tracepoint_storage_file_seek( \
        (stream), \
        (offset), \
        (origin) \
    )
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_TELL(stream) \
    open_cfw_test_tracepoint_storage_file_tell(stream)
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_MKDIR(path, mode) \
    open_cfw_test_tracepoint_storage_file_mkdir((path), (mode))
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPENDIR(path) \
    open_cfw_test_tracepoint_storage_file_opendir(path)
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_READDIR(directory) \
    open_cfw_test_tracepoint_storage_file_readdir(directory)
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSEDIR(directory) \
    open_cfw_test_tracepoint_storage_file_closedir(directory)
#define OPEN_CFW_TRACEPOINT_STORAGE_SEQUENCE \
    open_cfw_test_tracepoint_storage_sequence
#define OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX \
    open_cfw_test_tracepoint_storage_next_index
#define OPEN_CFW_TRACEPOINT_STORAGE_INITIALIZED \
    open_cfw_test_tracepoint_storage_initialized
#define OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_INDEX \
    open_cfw_test_tracepoint_storage_active_index
#define OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE \
    open_cfw_test_tracepoint_storage_active_size

#include "../../components/apollo_main/core_overlay/tracepoint_storage.c"
