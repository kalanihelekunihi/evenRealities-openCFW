/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * EasyLogger tracepoint file rotation, creation, append, write, commit, and
 * flush helpers matched to stock entries 0x0047E06A through 0x0047E231.
 */

typedef __UINTPTR_TYPE__ open_cfw_tracepoint_io_uintptr;

#ifndef OPEN_CFW_TRACEPOINT_IO_FILE_TYPE
#define OPEN_CFW_TRACEPOINT_IO_FILE_TYPE open_cfw_file
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_DIRECTORY_STATS_TYPE
#define OPEN_CFW_TRACEPOINT_IO_DIRECTORY_STATS_TYPE \
    open_cfw_tracepoint_storage_directory_stats
#endif

typedef void (*open_cfw_tracepoint_io_header_function)(
    void *,
    unsigned int,
    unsigned int
);

extern void open_cfw_tracepoint_path_format(
    char *,
    unsigned int,
    unsigned int
);
extern int open_cfw_tracepoint_directory_scan(
    OPEN_CFW_TRACEPOINT_IO_DIRECTORY_STATS_TYPE *
);
extern int open_cfw_tracepoint_state_persist(void);
extern OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *open_cfw_file_open(
    const void *,
    const char *
);
extern int open_cfw_file_close(OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *);
extern unsigned int open_cfw_file_write(
    const void *,
    unsigned int,
    unsigned int,
    OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *
);
extern int open_cfw_file_flush(OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *);
extern int open_cfw_file_remove(const void *);

#ifndef OPEN_CFW_TRACEPOINT_IO_PATH_FORMAT
#define OPEN_CFW_TRACEPOINT_IO_PATH_FORMAT(buffer, size, index) \
    open_cfw_tracepoint_path_format((buffer), (size), (index))
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_DIRECTORY_SCAN
#define OPEN_CFW_TRACEPOINT_IO_DIRECTORY_SCAN(stats) \
    open_cfw_tracepoint_directory_scan(stats)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_STATE_PERSIST
#define OPEN_CFW_TRACEPOINT_IO_STATE_PERSIST() \
    open_cfw_tracepoint_state_persist()
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_FILE_OPEN
#define OPEN_CFW_TRACEPOINT_IO_FILE_OPEN(path, mode) \
    open_cfw_file_open((path), (mode))
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_FILE_CLOSE
#define OPEN_CFW_TRACEPOINT_IO_FILE_CLOSE(stream) \
    open_cfw_file_close(stream)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_FILE_WRITE
#define OPEN_CFW_TRACEPOINT_IO_FILE_WRITE(buffer, size, count, stream) \
    open_cfw_file_write((buffer), (size), (count), (stream))
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_FILE_FLUSH
#define OPEN_CFW_TRACEPOINT_IO_FILE_FLUSH(stream) \
    open_cfw_file_flush(stream)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_FILE_REMOVE
#define OPEN_CFW_TRACEPOINT_IO_FILE_REMOVE(path) \
    open_cfw_file_remove(path)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_HEADER_BUILD
#define OPEN_CFW_TRACEPOINT_IO_HEADER_BUILD(buffer, index, sequence) \
    (((open_cfw_tracepoint_io_header_function) \
        (open_cfw_tracepoint_io_uintptr)0x0048ED01U)( \
            (buffer), \
            (index), \
            (sequence) \
        ))
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_SEQUENCE
#define OPEN_CFW_TRACEPOINT_IO_SEQUENCE \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_io_uintptr)0x20074AD4U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_NEXT_INDEX
#define OPEN_CFW_TRACEPOINT_IO_NEXT_INDEX \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_io_uintptr)0x20004188U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_INITIALIZED
#define OPEN_CFW_TRACEPOINT_IO_INITIALIZED \
    (*(volatile unsigned char *) \
        (open_cfw_tracepoint_io_uintptr)0x20075038U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX
#define OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_io_uintptr)0x20074AD8U)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE
#define OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE \
    (*(volatile unsigned int *) \
        (open_cfw_tracepoint_io_uintptr)0x20074ADCU)
#endif

#ifndef OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
#define OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE \
    (*(OPEN_CFW_TRACEPOINT_IO_FILE_TYPE * volatile *) \
        (open_cfw_tracepoint_io_uintptr)0x20074AE0U)
#endif

#define OPEN_CFW_TRACEPOINT_IO_NOT_READY (-2)
#define OPEN_CFW_TRACEPOINT_IO_ERROR (-5)
#define OPEN_CFW_TRACEPOINT_IO_PATH_CAPACITY 64U
#define OPEN_CFW_TRACEPOINT_IO_HEADER_SIZE 32U
#define OPEN_CFW_TRACEPOINT_IO_MAX_FILES 3U
#define OPEN_CFW_TRACEPOINT_IO_ROTATE_LIMIT 0x8001U

static const char open_cfw_tracepoint_io_write_mode[] = "wb";
static const char open_cfw_tracepoint_io_append_mode[] = "ab";

__attribute__((used, noinline))
void open_cfw_tracepoint_active_close(void)
{
    if (
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
            != (OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *)0
    ) {
        (void)OPEN_CFW_TRACEPOINT_IO_FILE_CLOSE(
            OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
        );
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE =
            (OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *)0;
    }
}

__attribute__((used, noinline))
void open_cfw_tracepoint_active_close_callback(void)
{
    open_cfw_tracepoint_active_close();
}

__attribute__((used, noinline))
int open_cfw_tracepoint_prune_files(void)
{
    OPEN_CFW_TRACEPOINT_IO_DIRECTORY_STATS_TYPE stats;
    char path[OPEN_CFW_TRACEPOINT_IO_PATH_CAPACITY];

    for (;;) {
        int result = OPEN_CFW_TRACEPOINT_IO_DIRECTORY_SCAN(&stats);

        if (result != 0) {
            return result;
        }
        if ((int)stats.count < (int)(OPEN_CFW_TRACEPOINT_IO_MAX_FILES + 1U)) {
            return 0;
        }

        OPEN_CFW_TRACEPOINT_IO_PATH_FORMAT(
            path,
            sizeof(path),
            stats.minimum_index
        );
        if (OPEN_CFW_TRACEPOINT_IO_FILE_REMOVE(path) != 0) {
            return OPEN_CFW_TRACEPOINT_IO_ERROR;
        }
    }
}

__attribute__((used, noinline))
int open_cfw_tracepoint_active_create(void)
{
    unsigned char header[OPEN_CFW_TRACEPOINT_IO_HEADER_SIZE];
    char path[OPEN_CFW_TRACEPOINT_IO_PATH_CAPACITY];
    unsigned int index;
    int result = open_cfw_tracepoint_prune_files();

    if (result != 0) {
        return result;
    }

    index = OPEN_CFW_TRACEPOINT_IO_NEXT_INDEX;
    OPEN_CFW_TRACEPOINT_IO_NEXT_INDEX = index + 1U;
    result = OPEN_CFW_TRACEPOINT_IO_STATE_PERSIST();
    if (result != 0) {
        return result;
    }

    OPEN_CFW_TRACEPOINT_IO_PATH_FORMAT(path, sizeof(path), index);
    OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE =
        OPEN_CFW_TRACEPOINT_IO_FILE_OPEN(
            path,
            open_cfw_tracepoint_io_write_mode
        );
    if (
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
            == (OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *)0
    ) {
        return OPEN_CFW_TRACEPOINT_IO_ERROR;
    }

    OPEN_CFW_TRACEPOINT_IO_HEADER_BUILD(
        header,
        index,
        OPEN_CFW_TRACEPOINT_IO_SEQUENCE
    );
    if (
        OPEN_CFW_TRACEPOINT_IO_FILE_WRITE(
            header,
            1U,
            sizeof(header),
            OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
        )
        != sizeof(header)
    ) {
        open_cfw_tracepoint_active_close();
        return OPEN_CFW_TRACEPOINT_IO_ERROR;
    }

    OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX = index;
    OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE = sizeof(header);
    return 0;
}

__attribute__((used, noinline))
int open_cfw_tracepoint_active_open(void)
{
    char path[OPEN_CFW_TRACEPOINT_IO_PATH_CAPACITY];

    OPEN_CFW_TRACEPOINT_IO_PATH_FORMAT(
        path,
        sizeof(path),
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX
    );
    OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE =
        OPEN_CFW_TRACEPOINT_IO_FILE_OPEN(
            path,
            open_cfw_tracepoint_io_append_mode
        );
    if (
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
            == (OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *)0
    ) {
        return OPEN_CFW_TRACEPOINT_IO_ERROR;
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_tracepoint_write(
    const void *buffer,
    unsigned int size
)
{
    int result;

    if (OPEN_CFW_TRACEPOINT_IO_INITIALIZED == 0U) {
        return OPEN_CFW_TRACEPOINT_IO_NOT_READY;
    }

    if (
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX != 0U
        && OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE + size
            >= OPEN_CFW_TRACEPOINT_IO_ROTATE_LIMIT
    ) {
        open_cfw_tracepoint_active_close();
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX = 0U;
    }

    if (
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
            == (OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *)0
    ) {
        if (OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX == 0U) {
            result = open_cfw_tracepoint_active_create();
        }
        else {
            result = open_cfw_tracepoint_active_open();
        }
        if (result != 0) {
            return result;
        }
    }

    if (
        OPEN_CFW_TRACEPOINT_IO_FILE_WRITE(
            buffer,
            1U,
            size,
            OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
        )
        != size
    ) {
        open_cfw_tracepoint_active_close();
        return OPEN_CFW_TRACEPOINT_IO_ERROR;
    }

    OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE += size;
    return 0;
}

__attribute__((used, noinline))
int open_cfw_tracepoint_commit(void)
{
    if (OPEN_CFW_TRACEPOINT_IO_INITIALIZED == 0U) {
        return OPEN_CFW_TRACEPOINT_IO_NOT_READY;
    }
    if (
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX == 0U
        || OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE
            < OPEN_CFW_TRACEPOINT_IO_HEADER_SIZE + 1U
    ) {
        return 0;
    }

    open_cfw_tracepoint_active_close();
    OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX = 0U;
    OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE = 0U;
    return 0;
}

__attribute__((used, noinline))
int open_cfw_tracepoint_flush(void)
{
    if (
        OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
            != (OPEN_CFW_TRACEPOINT_IO_FILE_TYPE *)0
    ) {
        return OPEN_CFW_TRACEPOINT_IO_FILE_FLUSH(
            OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
        );
    }
    return 0;
}

#undef OPEN_CFW_TRACEPOINT_IO_ROTATE_LIMIT
#undef OPEN_CFW_TRACEPOINT_IO_MAX_FILES
#undef OPEN_CFW_TRACEPOINT_IO_HEADER_SIZE
#undef OPEN_CFW_TRACEPOINT_IO_PATH_CAPACITY
#undef OPEN_CFW_TRACEPOINT_IO_ERROR
#undef OPEN_CFW_TRACEPOINT_IO_NOT_READY
#undef OPEN_CFW_TRACEPOINT_IO_ACTIVE_HANDLE
#undef OPEN_CFW_TRACEPOINT_IO_ACTIVE_SIZE
#undef OPEN_CFW_TRACEPOINT_IO_ACTIVE_INDEX
#undef OPEN_CFW_TRACEPOINT_IO_INITIALIZED
#undef OPEN_CFW_TRACEPOINT_IO_NEXT_INDEX
#undef OPEN_CFW_TRACEPOINT_IO_SEQUENCE
#undef OPEN_CFW_TRACEPOINT_IO_HEADER_BUILD
#undef OPEN_CFW_TRACEPOINT_IO_FILE_REMOVE
#undef OPEN_CFW_TRACEPOINT_IO_FILE_FLUSH
#undef OPEN_CFW_TRACEPOINT_IO_FILE_WRITE
#undef OPEN_CFW_TRACEPOINT_IO_FILE_CLOSE
#undef OPEN_CFW_TRACEPOINT_IO_FILE_OPEN
#undef OPEN_CFW_TRACEPOINT_IO_STATE_PERSIST
#undef OPEN_CFW_TRACEPOINT_IO_DIRECTORY_SCAN
#undef OPEN_CFW_TRACEPOINT_IO_PATH_FORMAT
#undef OPEN_CFW_TRACEPOINT_IO_DIRECTORY_STATS_TYPE
#undef OPEN_CFW_TRACEPOINT_IO_FILE_TYPE
