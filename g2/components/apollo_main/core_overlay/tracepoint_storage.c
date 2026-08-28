/*
 * SPDX-License-Identifier: MIT
 *
 * EasyLogger tracepoint filename, directory, and persistent-state helpers
 * matched to stock entries 0x0047DDFE through 0x0047E069.
 */

typedef __UINTPTR_TYPE__ open_cfw_tracepoint_storage_uintptr;

typedef struct {
    char name[0x100U];
    unsigned char type;
} open_cfw_tracepoint_storage_dirent;

typedef struct {
    unsigned int count;
    unsigned int minimum_index;
    unsigned int maximum_index;
} open_cfw_tracepoint_storage_directory_stats;

typedef int (*open_cfw_tracepoint_storage_format_function)(
    char *,
    unsigned int,
    const char *,
    ...
);
typedef unsigned int (*open_cfw_tracepoint_storage_parse_unsigned_function)(
    const char *,
    char **,
    int
);

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_STRLEN
#define OPEN_CFW_TRACEPOINT_STORAGE_STRLEN(text) open_cfw_strlen(text)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FORMAT
#define OPEN_CFW_TRACEPOINT_STORAGE_FORMAT(buffer, size, format, value) \
    (((open_cfw_tracepoint_storage_format_function) \
        (open_cfw_tracepoint_storage_uintptr)0x0044B729U)( \
            (buffer), \
            (size), \
            (format), \
            (value) \
        ))
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_PARSE_UNSIGNED
#define OPEN_CFW_TRACEPOINT_STORAGE_PARSE_UNSIGNED(text, end, base) \
    (((open_cfw_tracepoint_storage_parse_unsigned_function) \
        (open_cfw_tracepoint_storage_uintptr)0x0048D875U)( \
            (text), \
            (end), \
            (base) \
        ))
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPEN
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPEN(path, mode) \
    open_cfw_file_open((path), (mode))
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSE
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSE(stream) \
    open_cfw_file_close(stream)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_READ
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_READ( \
    buffer, size, count, stream \
) \
    open_cfw_file_read((buffer), (size), (count), (stream))
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_WRITE
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_WRITE( \
    buffer, size, count, stream \
) \
    open_cfw_file_write((buffer), (size), (count), (stream))
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_SEEK
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_SEEK(stream, offset, origin) \
    open_cfw_file_seek((stream), (offset), (origin))
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_TELL
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_TELL(stream) \
    open_cfw_file_tell(stream)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_MKDIR
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_MKDIR(path, mode) \
    open_cfw_file_mkdir((path), (mode))
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPENDIR
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPENDIR(path) \
    open_cfw_file_opendir(path)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_READDIR
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_READDIR(directory) \
    open_cfw_file_readdir(directory)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSEDIR
#define OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSEDIR(directory) \
    open_cfw_file_closedir(directory)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_SEQUENCE
#define OPEN_CFW_TRACEPOINT_STORAGE_SEQUENCE \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_storage_uintptr)0x20074AD4U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX
#define OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_storage_uintptr)0x20004188U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_INITIALIZED
#define OPEN_CFW_TRACEPOINT_STORAGE_INITIALIZED \
    (*(volatile unsigned char *) \
        (open_cfw_tracepoint_storage_uintptr)0x20075038U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_INDEX
#define OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_INDEX \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_storage_uintptr)0x20074AD8U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE
#define OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_storage_uintptr)0x20074ADCU)
#endif

#define OPEN_CFW_TRACEPOINT_STORAGE_ERROR (-5)
#define OPEN_CFW_TRACEPOINT_STORAGE_RECORD_SIZE 16U
#define OPEN_CFW_TRACEPOINT_STORAGE_DATA_SIZE 12U
#define OPEN_CFW_TRACEPOINT_STORAGE_DIRECTORY_TYPE_FILE 8U
#define OPEN_CFW_TRACEPOINT_STORAGE_MIN_ACTIVE_SIZE 32U
#define OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE_WINDOW 0x7FE0U

static const char open_cfw_tracepoint_storage_path_format[] =
    "/log/tp/tp_%u.bin";
static const char open_cfw_tracepoint_storage_state_path[] =
    "/log/tp/state.bin";
static const char open_cfw_tracepoint_storage_directory[] = "/log/tp";
static const char open_cfw_tracepoint_storage_read_mode[] = "rb";
static const char open_cfw_tracepoint_storage_write_mode[] = "wb";
static const char open_cfw_tracepoint_storage_prefix[] = "tp_";
static const char open_cfw_tracepoint_storage_suffix[] = ".bin";

static int open_cfw_tracepoint_storage_bytes_equal(
    const char *left,
    const char *right,
    unsigned int count
)
{
    unsigned int index;

    for (index = 0U; index < count; ++index) {
        if ((unsigned char)left[index] != (unsigned char)right[index]) {
            return 0;
        }
    }
    return 1;
}

__attribute__((used, noinline))
unsigned int open_cfw_tracepoint_state_crc32(const void *record)
{
    const unsigned char *bytes = (const unsigned char *)record;
    unsigned int crc = 0xFFFFFFFFU;
    unsigned int index;
    unsigned int bit;

    for (index = 0U; index < OPEN_CFW_TRACEPOINT_STORAGE_DATA_SIZE; ++index) {
        crc ^= bytes[index];
        for (bit = 0U; bit < 8U; ++bit) {
            unsigned int mask = 0U - (crc & 1U);

            crc = (crc >> 1U) ^ (0xEDB88320U & mask);
        }
    }
    return ~crc;
}

__attribute__((used, noinline))
void open_cfw_tracepoint_path_format(
    char *buffer,
    unsigned int size,
    unsigned int index
)
{
    (void)OPEN_CFW_TRACEPOINT_STORAGE_FORMAT(
        buffer,
        size,
        open_cfw_tracepoint_storage_path_format,
        index
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_tracepoint_path_parse(
    const char *name,
    unsigned int *index_out
)
{
    unsigned int length = OPEN_CFW_TRACEPOINT_STORAGE_STRLEN(name);
    char *end = (char *)0;
    unsigned int value;

    if (length < 8U) {
        return 0U;
    }
    if (!open_cfw_tracepoint_storage_bytes_equal(
            name,
            open_cfw_tracepoint_storage_prefix,
            3U
        )) {
        return 0U;
    }
    if (!open_cfw_tracepoint_storage_bytes_equal(
            name + length - 4U,
            open_cfw_tracepoint_storage_suffix,
            4U
        )) {
        return 0U;
    }

    value = OPEN_CFW_TRACEPOINT_STORAGE_PARSE_UNSIGNED(
        name + 3U,
        &end,
        10
    );
    if (end == (char *)0 || end != name + length - 4U) {
        return 0U;
    }

    *index_out = value;
    return 1U;
}

__attribute__((used, noinline))
int open_cfw_tracepoint_file_size(const char *path)
{
    void *stream = OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPEN(
        path,
        open_cfw_tracepoint_storage_read_mode
    );
    int size = 0;

    if (stream == (void *)0) {
        return 0;
    }
    if (OPEN_CFW_TRACEPOINT_STORAGE_FILE_SEEK(stream, 0, 2U) == 0) {
        size = OPEN_CFW_TRACEPOINT_STORAGE_FILE_TELL(stream);
    }
    (void)OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSE(stream);

    if (size < 1) {
        return 0;
    }
    return size;
}

__attribute__((used, noinline))
int open_cfw_tracepoint_directory_scan(
    open_cfw_tracepoint_storage_directory_stats *stats
)
{
    void *directory;
    open_cfw_tracepoint_storage_dirent *entry;

    stats->count = 0U;
    stats->minimum_index = 0xFFFFFFFFU;
    stats->maximum_index = 0U;

    directory = OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPENDIR(
        open_cfw_tracepoint_storage_directory
    );
    if (directory == (void *)0) {
        return OPEN_CFW_TRACEPOINT_STORAGE_ERROR;
    }

    while (
        (entry = (open_cfw_tracepoint_storage_dirent *)
            OPEN_CFW_TRACEPOINT_STORAGE_FILE_READDIR(directory))
        != (open_cfw_tracepoint_storage_dirent *)0
    ) {
        unsigned int index;

        if (
            entry->type != OPEN_CFW_TRACEPOINT_STORAGE_DIRECTORY_TYPE_FILE
            || open_cfw_tracepoint_path_parse(entry->name, &index) == 0U
        ) {
            continue;
        }

        stats->count += 1U;
        if (index < stats->minimum_index) {
            stats->minimum_index = index;
        }
        if (index > stats->maximum_index) {
            stats->maximum_index = index;
        }
    }

    (void)OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSEDIR(directory);
    return 0;
}

__attribute__((used, noinline))
int open_cfw_tracepoint_state_persist(void)
{
    unsigned int record[4];
    void *stream;
    unsigned int written;

    record[0] = 0x31535054U;
    record[1] = OPEN_CFW_TRACEPOINT_STORAGE_SEQUENCE;
    record[2] = OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX;
    record[3] = open_cfw_tracepoint_state_crc32(record);

    stream = OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPEN(
        open_cfw_tracepoint_storage_state_path,
        open_cfw_tracepoint_storage_write_mode
    );
    if (stream == (void *)0) {
        return OPEN_CFW_TRACEPOINT_STORAGE_ERROR;
    }

    written = OPEN_CFW_TRACEPOINT_STORAGE_FILE_WRITE(
        record,
        1U,
        OPEN_CFW_TRACEPOINT_STORAGE_RECORD_SIZE,
        stream
    );
    (void)OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSE(stream);
    if (written != OPEN_CFW_TRACEPOINT_STORAGE_RECORD_SIZE) {
        return OPEN_CFW_TRACEPOINT_STORAGE_ERROR;
    }
    return 0;
}

__attribute__((used, noinline))
void open_cfw_tracepoint_state_load(void)
{
    unsigned int record[4];
    void *stream = OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPEN(
        open_cfw_tracepoint_storage_state_path,
        open_cfw_tracepoint_storage_read_mode
    );
    unsigned int read;

    if (stream == (void *)0) {
        return;
    }

    read = OPEN_CFW_TRACEPOINT_STORAGE_FILE_READ(
        record,
        1U,
        OPEN_CFW_TRACEPOINT_STORAGE_RECORD_SIZE,
        stream
    );
    (void)OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSE(stream);
    if (
        read != OPEN_CFW_TRACEPOINT_STORAGE_RECORD_SIZE
        || record[0] != 0x31535054U
        || record[3] != open_cfw_tracepoint_state_crc32(record)
    ) {
        return;
    }

    OPEN_CFW_TRACEPOINT_STORAGE_SEQUENCE = record[1];
    if (record[2] < 2U) {
        OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX = 1U;
    }
    else {
        OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX = record[2];
    }
}

__attribute__((used, noinline))
int open_cfw_tracepoint_storage_initialize(void)
{
    open_cfw_tracepoint_storage_directory_stats stats;
    char path[64];
    int result;

    if (OPEN_CFW_TRACEPOINT_STORAGE_INITIALIZED != 0U) {
        return 0;
    }

    (void)OPEN_CFW_TRACEPOINT_STORAGE_FILE_MKDIR(
        open_cfw_tracepoint_storage_directory,
        0U
    );
    open_cfw_tracepoint_state_load();
    OPEN_CFW_TRACEPOINT_STORAGE_SEQUENCE += 1U;

    result = open_cfw_tracepoint_directory_scan(&stats);
    if (result != 0) {
        return result;
    }

    if (stats.count > 0U) {
        int size;

        if (OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX < stats.maximum_index + 1U) {
            OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX =
                stats.maximum_index + 1U;
        }

        open_cfw_tracepoint_path_format(
            path,
            sizeof(path),
            stats.maximum_index
        );
        size = open_cfw_tracepoint_file_size(path);
        if (
            (unsigned int)size
                - OPEN_CFW_TRACEPOINT_STORAGE_MIN_ACTIVE_SIZE
            < OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE_WINDOW
        ) {
            OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_INDEX = stats.maximum_index;
            OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE = (unsigned int)size;
        }
    }

    result = open_cfw_tracepoint_state_persist();
    if (result == 0) {
        OPEN_CFW_TRACEPOINT_STORAGE_INITIALIZED = 1U;
    }
    return result;
}

#undef OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE_WINDOW
#undef OPEN_CFW_TRACEPOINT_STORAGE_MIN_ACTIVE_SIZE
#undef OPEN_CFW_TRACEPOINT_STORAGE_DIRECTORY_TYPE_FILE
#undef OPEN_CFW_TRACEPOINT_STORAGE_DATA_SIZE
#undef OPEN_CFW_TRACEPOINT_STORAGE_RECORD_SIZE
#undef OPEN_CFW_TRACEPOINT_STORAGE_ERROR
#undef OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_SIZE
#undef OPEN_CFW_TRACEPOINT_STORAGE_ACTIVE_INDEX
#undef OPEN_CFW_TRACEPOINT_STORAGE_INITIALIZED
#undef OPEN_CFW_TRACEPOINT_STORAGE_NEXT_INDEX
#undef OPEN_CFW_TRACEPOINT_STORAGE_SEQUENCE
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSEDIR
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_READDIR
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPENDIR
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_MKDIR
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_TELL
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_SEEK
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_WRITE
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_READ
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_CLOSE
#undef OPEN_CFW_TRACEPOINT_STORAGE_FILE_OPEN
#undef OPEN_CFW_TRACEPOINT_STORAGE_PARSE_UNSIGNED
#undef OPEN_CFW_TRACEPOINT_STORAGE_FORMAT
#undef OPEN_CFW_TRACEPOINT_STORAGE_STRLEN
