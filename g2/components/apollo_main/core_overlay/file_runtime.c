/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 shared file open, close, read,
 * write, seek, tell, size, flush, remove, rename, directory-create,
 * directory-open, directory-read, directory-close, and synchronized
 * allocation/free/reallocation and initialization runtime at
 * 0x00474550...0x00474E3B.
 */

typedef struct {
    unsigned int driver;
    unsigned int state[23];
} open_cfw_file;

typedef struct {
    unsigned int driver;
    unsigned char state[0x13CU];
    char path[0x100U];
} open_cfw_directory;

typedef struct {
    char name[0x100U];
    unsigned char type;
} open_cfw_dirent;

typedef void *(*open_cfw_file_allocate_fn)(unsigned int size);
typedef void (*open_cfw_file_free_fn)(void *allocation);
typedef int (*open_cfw_file_mutex_acquire_fn)(
    void *mutex,
    unsigned int timeout
);
typedef void (*open_cfw_file_mutex_release_fn)(void *mutex);
typedef int (*open_cfw_file_backend_open_fn)(
    unsigned int driver,
    void *state,
    const void *path,
    unsigned int flags
);
typedef int (*open_cfw_file_backend_close_fn)(
    unsigned int driver,
    void *state
);
typedef int (*open_cfw_file_backend_read_fn)(
    unsigned int driver,
    void *state,
    void *buffer,
    unsigned int size
);
typedef int (*open_cfw_file_backend_write_fn)(
    unsigned int driver,
    void *state,
    const void *buffer,
    unsigned int size
);
typedef int (*open_cfw_file_backend_seek_fn)(
    unsigned int driver,
    void *state,
    int offset,
    unsigned int origin
);
typedef int (*open_cfw_file_backend_tell_fn)(
    unsigned int driver,
    void *state
);
typedef int (*open_cfw_file_backend_size_fn)(
    unsigned int driver,
    void *state
);
typedef int (*open_cfw_file_backend_flush_fn)(
    unsigned int driver,
    void *state
);
typedef int (*open_cfw_file_backend_remove_fn)(
    unsigned int driver,
    const void *path
);
typedef int (*open_cfw_file_backend_rename_fn)(
    unsigned int driver,
    const void *old_path,
    const void *new_path
);
typedef int (*open_cfw_file_backend_mkdir_fn)(
    unsigned int driver,
    const void *path
);
typedef int (*open_cfw_file_backend_opendir_fn)(
    unsigned int driver,
    void *state,
    const void *path
);
typedef int (*open_cfw_file_backend_readdir_fn)(
    unsigned int driver,
    void *state,
    void *entry
);
typedef int (*open_cfw_file_backend_closedir_fn)(
    unsigned int driver,
    void *state
);
typedef void *(*open_cfw_file_heap_allocate_backend_fn)(
    void *heap,
    unsigned int size
);
typedef void (*open_cfw_file_heap_free_backend_fn)(
    void *heap,
    void *allocation
);
typedef void *(*open_cfw_file_heap_reallocate_backend_fn)(
    void *heap,
    void *allocation,
    unsigned int size
);
typedef unsigned int (*open_cfw_file_heap_format_fn)(
    const char *format,
    ...
);
typedef void (*open_cfw_file_heap_diagnostic_fn)(
    const void *context,
    const void *file,
    unsigned int line
);
typedef void *(*open_cfw_file_runtime_mutex_create_fn)(unsigned int mode);
typedef int *(*open_cfw_file_errno_location_fn)(void);
typedef unsigned int (*open_cfw_file_log_flags_fn)(void);
typedef void (*open_cfw_file_log_fn)(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_file_backend_log_fn)(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
);

_Static_assert(sizeof(open_cfw_file) == 0x60U, "file ABI size drift");
_Static_assert(
    sizeof(open_cfw_directory) == 0x240U,
    "directory ABI size drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_directory, state) == 4U,
    "directory state offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_directory, path) == 0x140U,
    "directory path offset drift"
);
_Static_assert(
    __builtin_offsetof(open_cfw_dirent, type) == 0x100U,
    "directory entry type offset drift"
);

#ifndef OPEN_CFW_FILE_DRIVER
#define OPEN_CFW_FILE_DRIVER 0x20071AC8U
#endif

#ifndef OPEN_CFW_FILE_MUTEX_HANDLE
#define OPEN_CFW_FILE_MUTEX_HANDLE \
    (*(void * volatile *)(void *)0x200748F4U)
#endif

#ifndef OPEN_CFW_FILE_READY_STATE
#define OPEN_CFW_FILE_READY_STATE \
    (*(volatile unsigned int *)(void *)0x200746A8U)
#endif

#ifndef OPEN_CFW_FILE_ALLOCATE
#define OPEN_CFW_FILE_ALLOCATE(size) \
    (((open_cfw_file_allocate_fn)0x00474CD3U)(size))
#endif

#ifndef OPEN_CFW_FILE_FREE
#define OPEN_CFW_FILE_FREE(allocation) \
    (((open_cfw_file_free_fn)0x00474D17U)(allocation))
#endif

#ifndef OPEN_CFW_FILE_MUTEX_ACQUIRE
#define OPEN_CFW_FILE_MUTEX_ACQUIRE(mutex, timeout) \
    (((open_cfw_file_mutex_acquire_fn)0x004497B7U)( \
        (mutex), \
        (timeout) \
    ))
#endif

#ifndef OPEN_CFW_FILE_MUTEX_RELEASE
#define OPEN_CFW_FILE_MUTEX_RELEASE(mutex) \
    (((open_cfw_file_mutex_release_fn)0x0044981DU)(mutex))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_OPEN
#define OPEN_CFW_FILE_BACKEND_OPEN(driver, state, path, flags) \
    (((open_cfw_file_backend_open_fn)0x004CFA95U)( \
        (driver), \
        (state), \
        (path), \
        (flags) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_CLOSE
#define OPEN_CFW_FILE_BACKEND_CLOSE(driver, state) \
    (((open_cfw_file_backend_close_fn)0x004CFAD1U)( \
        (driver), \
        (state) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_READ
#define OPEN_CFW_FILE_BACKEND_READ(driver, state, buffer, size) \
    (((open_cfw_file_backend_read_fn)0x004CFB41U)( \
        (driver), \
        (state), \
        (buffer), \
        (size) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_WRITE
#define OPEN_CFW_FILE_BACKEND_WRITE(driver, state, buffer, size) \
    (((open_cfw_file_backend_write_fn)0x004CFB7DU)( \
        (driver), \
        (state), \
        (buffer), \
        (size) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_SEEK
#define OPEN_CFW_FILE_BACKEND_SEEK(driver, state, offset, origin) \
    (((open_cfw_file_backend_seek_fn)0x004CFBB3U)( \
        (driver), \
        (state), \
        (offset), \
        (origin) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_TELL
#define OPEN_CFW_FILE_BACKEND_TELL(driver, state) \
    (((open_cfw_file_backend_tell_fn)0x004CFBE9U)( \
        (driver), \
        (state) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_SIZE
#define OPEN_CFW_FILE_BACKEND_SIZE(driver, state) \
    (((open_cfw_file_backend_size_fn)0x004CFC2FU)( \
        (driver), \
        (state) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_FLUSH
#define OPEN_CFW_FILE_BACKEND_FLUSH(driver, state) \
    (((open_cfw_file_backend_flush_fn)0x004CFB09U)( \
        (driver), \
        (state) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_REMOVE
#define OPEN_CFW_FILE_BACKEND_REMOVE(driver, path) \
    (((open_cfw_file_backend_remove_fn)0x004CFA77U)( \
        (driver), \
        (path) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_RENAME
#define OPEN_CFW_FILE_BACKEND_RENAME(driver, old_path, new_path) \
    (((open_cfw_file_backend_rename_fn)0x004CFA81U)( \
        (driver), \
        (old_path), \
        (new_path) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_MKDIR
#define OPEN_CFW_FILE_BACKEND_MKDIR(driver, path) \
    (((open_cfw_file_backend_mkdir_fn)0x004CFC5DU)( \
        (driver), \
        (path) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_OPENDIR
#define OPEN_CFW_FILE_BACKEND_OPENDIR(driver, state, path) \
    (((open_cfw_file_backend_opendir_fn)0x004CFC67U)( \
        (driver), \
        (state), \
        (path) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_READDIR
#define OPEN_CFW_FILE_BACKEND_READDIR(driver, state, entry) \
    (((open_cfw_file_backend_readdir_fn)0x004CFD03U)( \
        (driver), \
        (state), \
        (entry) \
    ))
#endif

#ifndef OPEN_CFW_FILE_BACKEND_CLOSEDIR
#define OPEN_CFW_FILE_BACKEND_CLOSEDIR(driver, state) \
    (((open_cfw_file_backend_closedir_fn)0x004CFCF9U)( \
        (driver), \
        (state) \
    ))
#endif

#ifndef OPEN_CFW_FILE_DIRENT
#define OPEN_CFW_FILE_DIRENT \
    ((open_cfw_dirent *)(void *)0x200701E8U)
#endif

#ifndef OPEN_CFW_FILE_HEAP_MUTEX_HANDLE
#define OPEN_CFW_FILE_HEAP_MUTEX_HANDLE \
    (*(void * volatile *)(void *)0x200748F8U)
#endif

#ifndef OPEN_CFW_FILE_HEAP_HANDLE
#define OPEN_CFW_FILE_HEAP_HANDLE \
    (*(void * volatile *)(void *)0x20074ABCU)
#endif

#ifndef OPEN_CFW_FILE_HEAP_MUTEX_ACQUIRE
#define OPEN_CFW_FILE_HEAP_MUTEX_ACQUIRE(mutex, timeout) \
    OPEN_CFW_FILE_MUTEX_ACQUIRE((mutex), (timeout))
#endif

#ifndef OPEN_CFW_FILE_HEAP_MUTEX_RELEASE
#define OPEN_CFW_FILE_HEAP_MUTEX_RELEASE(mutex) \
    OPEN_CFW_FILE_MUTEX_RELEASE(mutex)
#endif

#ifndef OPEN_CFW_FILE_HEAP_ALLOCATE_BACKEND
#define OPEN_CFW_FILE_HEAP_ALLOCATE_BACKEND(heap, size) \
    (((open_cfw_file_heap_allocate_backend_fn)0x004D0723U)( \
        (heap), \
        (size) \
    ))
#endif

#ifndef OPEN_CFW_FILE_HEAP_FREE_BACKEND
#define OPEN_CFW_FILE_HEAP_FREE_BACKEND(heap, allocation) \
    (((open_cfw_file_heap_free_backend_fn)0x004D0809U)( \
        (heap), \
        (allocation) \
    ))
#endif

#ifndef OPEN_CFW_FILE_HEAP_REALLOCATE_BACKEND
#define OPEN_CFW_FILE_HEAP_REALLOCATE_BACKEND(heap, allocation, size) \
    (((open_cfw_file_heap_reallocate_backend_fn)0x004D0869U)( \
        (heap), \
        (allocation), \
        (size) \
    ))
#endif

#ifndef OPEN_CFW_FILE_HEAP_FORMAT
#define OPEN_CFW_FILE_HEAP_FORMAT \
    ((open_cfw_file_heap_format_fn)0x004733EFU)
#endif

#ifndef OPEN_CFW_FILE_HEAP_DIAGNOSTIC
#define OPEN_CFW_FILE_HEAP_DIAGNOSTIC \
    ((open_cfw_file_heap_diagnostic_fn)0x004D09B5U)
#endif

#ifndef OPEN_CFW_FILE_HEAP_DIAGNOSTIC_CONTEXT
#define OPEN_CFW_FILE_HEAP_DIAGNOSTIC_CONTEXT \
    ((const void *)0x00474E40U)
#endif

#ifndef OPEN_CFW_FILE_HEAP_DIAGNOSTIC_FILE
#define OPEN_CFW_FILE_HEAP_DIAGNOSTIC_FILE \
    ((const void *)0x006FC7C4U)
#endif

#ifndef OPEN_CFW_FILE_HEAP_ALLOCATE_FAILURE
#define OPEN_CFW_FILE_HEAP_ALLOCATE_FAILURE \
    ((const char *)0x007646F0U)
#endif

#ifndef OPEN_CFW_FILE_HEAP_FREE_FAILURE
#define OPEN_CFW_FILE_HEAP_FREE_FAILURE \
    ((const char *)0x00764710U)
#endif

#ifndef OPEN_CFW_FILE_HEAP_REALLOCATE_FAILURE
#define OPEN_CFW_FILE_HEAP_REALLOCATE_FAILURE \
    ((const char *)0x00764730U)
#endif

#ifndef OPEN_CFW_FILE_RUNTIME_MUTEX_CREATE
#define OPEN_CFW_FILE_RUNTIME_MUTEX_CREATE(mode) \
    (((open_cfw_file_runtime_mutex_create_fn)0x0044971DU)(mode))
#endif

#ifndef OPEN_CFW_FILE_RUNTIME_STORE_PRIMARY_MUTEX
#define OPEN_CFW_FILE_RUNTIME_STORE_PRIMARY_MUTEX(value) \
    do { \
        (*(void * volatile *)(void *)0x200748F4U) = (value); \
    } while (0)
#endif

#ifndef OPEN_CFW_FILE_RUNTIME_STORE_HEAP_MUTEX
#define OPEN_CFW_FILE_RUNTIME_STORE_HEAP_MUTEX(value) \
    do { \
        (*(void * volatile *)(void *)0x200748F8U) = (value); \
    } while (0)
#endif

#define OPEN_CFW_FILE_RUNTIME_LOG_TAG ((const void *)0x0078BD74U)
#define OPEN_CFW_FILE_RUNTIME_LOG_FILE ((const void *)0x006FC7C4U)
#define OPEN_CFW_FILE_RUNTIME_LOG_FUNCTION ((const void *)0x00788610U)
#define OPEN_CFW_FILE_RUNTIME_INIT_FAILURE ((const void *)0x00742624U)
#define OPEN_CFW_FILE_RUNTIME_INIT_FAILURE_BACKEND \
    ((const void *)0x0072CB94U)
#define OPEN_CFW_FILE_RUNTIME_INIT_SUCCESS ((const void *)0x0074D624U)
#define OPEN_CFW_FILE_RUNTIME_INIT_SUCCESS_BACKEND \
    ((const void *)0x007379C4U)

#ifndef OPEN_CFW_FILE_ERRNO_LOCATION
#define OPEN_CFW_FILE_ERRNO_LOCATION() \
    (((open_cfw_file_errno_location_fn)0x00439CC5U)())
#endif

#ifndef OPEN_CFW_FILE_LOG_FLAGS
#define OPEN_CFW_FILE_LOG_FLAGS() \
    (((open_cfw_file_log_flags_fn)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_FILE_LOG
#define OPEN_CFW_FILE_LOG ((open_cfw_file_log_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_FILE_BACKEND_LOG
#define OPEN_CFW_FILE_BACKEND_LOG \
    ((open_cfw_file_backend_log_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_FILE_LOG_TAG ((const void *)0x0078BD74U)
#define OPEN_CFW_FILE_LOG_FILE ((const void *)0x006FC7C4U)
#define OPEN_CFW_FILE_WRITE_FUNCTION ((const void *)0x0078E45CU)
#define OPEN_CFW_FILE_WRITE_NULL ((const void *)0x0077B0ECU)
#define OPEN_CFW_FILE_WRITE_NULL_BACKEND ((const void *)0x00758EBCU)
#define OPEN_CFW_FILE_WRITE_TIMEOUT ((const void *)0x0074D5D4U)
#define OPEN_CFW_FILE_WRITE_TIMEOUT_BACKEND ((const void *)0x00737934U)
#define OPEN_CFW_FILE_WRITE_ERROR ((const void *)0x00737964U)
#define OPEN_CFW_FILE_WRITE_ERROR_BACKEND ((const void *)0x00722078U)
#define OPEN_CFW_FILE_WRITE_SHORT ((const void *)0x0074D5FCU)
#define OPEN_CFW_FILE_WRITE_SHORT_BACKEND ((const void *)0x00737994U)

static __attribute__((always_inline)) inline int
open_cfw_file_backend_log_enabled(void)
{
    if ((OPEN_CFW_FILE_LOG_FLAGS() & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_FILE_LOG_FLAGS() & 4U) != 0U;
}

static __attribute__((always_inline)) inline int
open_cfw_file_mode_contains(const char *mode, char character)
{
    const char *cursor = mode;

    while (*cursor != '\0') {
        if (*cursor == character) {
            return 1;
        }
        cursor += 1;
    }
    return 0;
}

static __attribute__((always_inline)) inline void
open_cfw_directory_copy_path(char destination[0x100U], const char *source)
{
    unsigned int index;
    int ended = 0;

    for (index = 0U; index < 0xFFU; index += 1U) {
        if (ended) {
            destination[index] = '\0';
        } else {
            char value = source[index];

            destination[index] = value;
            if (value == '\0') {
                ended = 1;
            }
        }
    }
    destination[0xFFU] = '\0';
}

static __attribute__((always_inline)) inline void
open_cfw_file_log_write_null(void)
{
    if ((OPEN_CFW_FILE_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_FILE_LOG(
            1U,
            OPEN_CFW_FILE_LOG_TAG,
            OPEN_CFW_FILE_LOG_FILE,
            OPEN_CFW_FILE_WRITE_FUNCTION,
            0x236U,
            OPEN_CFW_FILE_WRITE_NULL
        );
    }
    if (open_cfw_file_backend_log_enabled()) {
        OPEN_CFW_FILE_BACKEND_LOG(
            0x04000000U,
            OPEN_CFW_FILE_WRITE_NULL_BACKEND,
            OPEN_CFW_FILE_WRITE_NULL_BACKEND
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_file_log_write_timeout(unsigned int wanted)
{
    if ((OPEN_CFW_FILE_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_FILE_LOG(
            1U,
            OPEN_CFW_FILE_LOG_TAG,
            OPEN_CFW_FILE_LOG_FILE,
            OPEN_CFW_FILE_WRITE_FUNCTION,
            0x23CU,
            OPEN_CFW_FILE_WRITE_TIMEOUT,
            wanted
        );
    }
    if (open_cfw_file_backend_log_enabled()) {
        OPEN_CFW_FILE_BACKEND_LOG(
            0x04400000U,
            OPEN_CFW_FILE_WRITE_TIMEOUT_BACKEND,
            OPEN_CFW_FILE_WRITE_TIMEOUT_BACKEND,
            wanted
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_file_log_write_result(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int backend_mask,
    const void *backend_format,
    int result,
    unsigned int wanted
)
{
    if ((OPEN_CFW_FILE_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_FILE_LOG(
            level,
            OPEN_CFW_FILE_LOG_TAG,
            OPEN_CFW_FILE_LOG_FILE,
            OPEN_CFW_FILE_WRITE_FUNCTION,
            line,
            format,
            result,
            wanted
        );
    }
    if (open_cfw_file_backend_log_enabled()) {
        OPEN_CFW_FILE_BACKEND_LOG(
            backend_mask,
            backend_format,
            backend_format,
            result,
            wanted
        );
    }
}

__attribute__((used, noinline))
open_cfw_file *open_cfw_file_open(const void *path, const char *mode)
{
    open_cfw_file *stream = OPEN_CFW_FILE_ALLOCATE(sizeof(*stream));
    unsigned int flags = 0U;
    int result;

    if (stream == (open_cfw_file *)0) {
        return (open_cfw_file *)0;
    }
    stream->driver = OPEN_CFW_FILE_DRIVER;
    if (open_cfw_file_mode_contains(mode, 'r')) {
        flags |= 0x001U;
    }
    if (open_cfw_file_mode_contains(mode, 'w')) {
        flags |= 0x502U;
    }
    if (open_cfw_file_mode_contains(mode, 'a')) {
        flags |= 0x902U;
    }
    if (open_cfw_file_mode_contains(mode, '+')) {
        flags |= 0x003U;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        OPEN_CFW_FILE_FREE(stream);
        return (open_cfw_file *)0;
    }
    result = OPEN_CFW_FILE_BACKEND_OPEN(
        stream->driver,
        stream->state,
        path,
        flags
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        OPEN_CFW_FILE_FREE(stream);
        return (open_cfw_file *)0;
    }
    return stream;
}

__attribute__((used, noinline))
int open_cfw_file_close(open_cfw_file *stream)
{
    int result;

    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_CLOSE(stream->driver, stream->state);
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    OPEN_CFW_FILE_FREE(stream);
    return result < 0 ? -1 : 0;
}

__attribute__((used, noinline))
unsigned int open_cfw_file_read(
    void *buffer,
    unsigned int element_size,
    unsigned int element_count,
    open_cfw_file *stream
)
{
    unsigned int wanted = element_count * element_size;
    int result;

    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        return 0U;
    }
    result = OPEN_CFW_FILE_BACKEND_READ(
        stream->driver,
        stream->state,
        buffer,
        wanted
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        return 0U;
    }
    return (unsigned int)result / element_size;
}

__attribute__((used, noinline))
unsigned int open_cfw_file_write(
    const void *buffer,
    unsigned int element_size,
    unsigned int element_count,
    open_cfw_file *stream
)
{
    unsigned int wanted = element_count * element_size;
    int result;

    if (stream == (open_cfw_file *)0) {
        open_cfw_file_log_write_null();
        return 0U;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        open_cfw_file_log_write_timeout(wanted);
        return 0U;
    }
    result = OPEN_CFW_FILE_BACKEND_WRITE(
        stream->driver,
        stream->state,
        buffer,
        wanted
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        open_cfw_file_log_write_result(
            1U,
            0x24AU,
            OPEN_CFW_FILE_WRITE_ERROR,
            0x04800000U,
            OPEN_CFW_FILE_WRITE_ERROR_BACKEND,
            result,
            wanted
        );
        return 0U;
    }
    if ((unsigned int)result < wanted) {
        open_cfw_file_log_write_result(
            2U,
            0x24EU,
            OPEN_CFW_FILE_WRITE_SHORT,
            0x08800000U,
            OPEN_CFW_FILE_WRITE_SHORT_BACKEND,
            result,
            wanted
        );
    }
    return (unsigned int)result / element_size;
}

__attribute__((used, noinline))
int open_cfw_file_seek(
    open_cfw_file *stream,
    int offset,
    unsigned int origin
)
{
    int result;

    if (origin > 2U) {
        return -1;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_SEEK(
        stream->driver,
        stream->state,
        offset,
        origin
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    return result < 0 ? -1 : 0;
}

__attribute__((used, noinline))
int open_cfw_file_tell(open_cfw_file *stream)
{
    int result;

    if (stream == (open_cfw_file *)0) {
        return -1;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_TELL(stream->driver, stream->state);
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    return result < 0 ? -1 : result;
}

__attribute__((used, noinline))
int open_cfw_file_size(open_cfw_file *stream)
{
    int result;

    if (stream == (open_cfw_file *)0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 9;
        return -1;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_SIZE(stream->driver, stream->state);
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 5;
        return -1;
    }
    return result;
}

__attribute__((used, noinline))
int open_cfw_file_flush(open_cfw_file *stream)
{
    int result;

    if (
        stream == (open_cfw_file *)0
        || stream == (open_cfw_file *)0x200043F8U
        || stream == (open_cfw_file *)0x20004440U
        || stream == (open_cfw_file *)0x200043B0U
    ) {
        return 0;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_FLUSH(stream->driver, stream->state);
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 5;
        return -1;
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_file_remove(const void *path)
{
    int result;

    if (OPEN_CFW_FILE_READY_STATE != 1U) {
        return 0;
    }
    if (path == (const void *)0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x16;
        return -1;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_REMOVE(OPEN_CFW_FILE_DRIVER, path);
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0 && result != -2) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 5;
        return -1;
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_file_rename(const void *old_path, const void *new_path)
{
    int result;

    if (OPEN_CFW_FILE_READY_STATE != 1U) {
        return 0;
    }
    if (
        old_path == (const void *)0
        || new_path == (const void *)0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x16;
        return -1;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_RENAME(
        OPEN_CFW_FILE_DRIVER,
        old_path,
        new_path
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 5;
        return -1;
    }
    return 0;
}

__attribute__((used, noinline))
int open_cfw_file_mkdir(const void *path, unsigned int mode)
{
    int result;

    (void)mode;
    if (OPEN_CFW_FILE_READY_STATE != 1U) {
        return 0;
    }
    if (path == (const void *)0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x16;
        return -1;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_MKDIR(OPEN_CFW_FILE_DRIVER, path);
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result >= 0) {
        return 0;
    }
    if (result == -0x11) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x11;
    } else if (result == -2) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 2;
    } else {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 5;
    }
    return -1;
}

__attribute__((used, noinline))
open_cfw_directory *open_cfw_file_opendir(const char *path)
{
    open_cfw_directory *directory;
    int result;

    if (OPEN_CFW_FILE_READY_STATE != 1U) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 2;
        return (open_cfw_directory *)0;
    }
    if (path == (const char *)0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x16;
        return (open_cfw_directory *)0;
    }
    directory = OPEN_CFW_FILE_ALLOCATE(sizeof(*directory));
    if (directory == (open_cfw_directory *)0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x0C;
        return (open_cfw_directory *)0;
    }
    directory->driver = OPEN_CFW_FILE_DRIVER;
    open_cfw_directory_copy_path(directory->path, path);
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        OPEN_CFW_FILE_FREE(directory);
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return (open_cfw_directory *)0;
    }
    result = OPEN_CFW_FILE_BACKEND_OPENDIR(
        directory->driver,
        directory->state,
        path
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        OPEN_CFW_FILE_FREE(directory);
        *OPEN_CFW_FILE_ERRNO_LOCATION() = result == -2 ? 2 : 5;
        return (open_cfw_directory *)0;
    }
    return directory;
}

#define OPEN_CFW_DIRECTORY_BACKEND_ENTRY_OFFSET 0x34U
#define OPEN_CFW_DIRECTORY_BACKEND_NAME_OFFSET 0x3CU

__attribute__((used, noinline))
open_cfw_dirent *open_cfw_file_readdir(open_cfw_directory *directory)
{
    open_cfw_dirent *entry = OPEN_CFW_FILE_DIRENT;
    unsigned char backend_type;
    int result;

    if (
        OPEN_CFW_FILE_READY_STATE != 1U
        || directory == (open_cfw_directory *)0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 9;
        return (open_cfw_dirent *)0;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return (open_cfw_dirent *)0;
    }
    result = OPEN_CFW_FILE_BACKEND_READDIR(
        directory->driver,
        directory->state,
        &directory->state[OPEN_CFW_DIRECTORY_BACKEND_ENTRY_OFFSET]
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    if (result < 0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 5;
        return (open_cfw_dirent *)0;
    }
    if (result == 0) {
        return (open_cfw_dirent *)0;
    }
    open_cfw_directory_copy_path(
        entry->name,
        (const char *)&directory->state[
            OPEN_CFW_DIRECTORY_BACKEND_NAME_OFFSET
        ]
    );
    backend_type =
        directory->state[OPEN_CFW_DIRECTORY_BACKEND_ENTRY_OFFSET];
    if (backend_type == 2U) {
        entry->type = 4U;
    } else if (backend_type == 1U) {
        entry->type = 8U;
    } else {
        entry->type = 0U;
    }
    return entry;
}

__attribute__((used, noinline))
int open_cfw_file_closedir(open_cfw_directory *directory)
{
    int result;

    if (OPEN_CFW_FILE_READY_STATE != 1U) {
        return 0;
    }
    if (directory == (open_cfw_directory *)0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 9;
        return -1;
    }
    if (
        OPEN_CFW_FILE_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_MUTEX_HANDLE,
            1000U
        ) != 0
    ) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 0x10;
        return -1;
    }
    result = OPEN_CFW_FILE_BACKEND_CLOSEDIR(
        directory->driver,
        directory->state
    );
    OPEN_CFW_FILE_MUTEX_RELEASE(OPEN_CFW_FILE_MUTEX_HANDLE);
    OPEN_CFW_FILE_FREE(directory);
    if (result < 0) {
        *OPEN_CFW_FILE_ERRNO_LOCATION() = 5;
        return -1;
    }
    return 0;
}

static __attribute__((always_inline)) inline void
open_cfw_file_heap_timeout(
    const char *format,
    unsigned int line
)
{
    OPEN_CFW_FILE_HEAP_FORMAT(format);
    OPEN_CFW_FILE_HEAP_DIAGNOSTIC(
        OPEN_CFW_FILE_HEAP_DIAGNOSTIC_CONTEXT,
        OPEN_CFW_FILE_HEAP_DIAGNOSTIC_FILE,
        line
    );
}

__attribute__((used, noinline))
void *open_cfw_file_heap_allocate(unsigned int size)
{
    void *allocation = (void *)0;

    if (
        OPEN_CFW_FILE_HEAP_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_HEAP_MUTEX_HANDLE,
            1000U
        ) == 0
    ) {
        allocation = OPEN_CFW_FILE_HEAP_ALLOCATE_BACKEND(
            OPEN_CFW_FILE_HEAP_HANDLE,
            size
        );
        OPEN_CFW_FILE_HEAP_MUTEX_RELEASE(
            OPEN_CFW_FILE_HEAP_MUTEX_HANDLE
        );
    } else {
        open_cfw_file_heap_timeout(
            OPEN_CFW_FILE_HEAP_ALLOCATE_FAILURE,
            0x432U
        );
    }
    return allocation;
}

__attribute__((used, noinline))
void open_cfw_file_heap_free(void *allocation)
{
    if (
        OPEN_CFW_FILE_HEAP_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_HEAP_MUTEX_HANDLE,
            1000U
        ) == 0
    ) {
        OPEN_CFW_FILE_HEAP_FREE_BACKEND(
            OPEN_CFW_FILE_HEAP_HANDLE,
            allocation
        );
        OPEN_CFW_FILE_HEAP_MUTEX_RELEASE(
            OPEN_CFW_FILE_HEAP_MUTEX_HANDLE
        );
    } else {
        open_cfw_file_heap_timeout(
            OPEN_CFW_FILE_HEAP_FREE_FAILURE,
            0x43EU
        );
    }
}

__attribute__((used, noinline))
void *open_cfw_file_heap_reallocate(
    void *allocation,
    unsigned int size
)
{
    void *result = (void *)0;

    if (
        OPEN_CFW_FILE_HEAP_MUTEX_ACQUIRE(
            OPEN_CFW_FILE_HEAP_MUTEX_HANDLE,
            1000U
        ) == 0
    ) {
        result = OPEN_CFW_FILE_HEAP_REALLOCATE_BACKEND(
            OPEN_CFW_FILE_HEAP_HANDLE,
            allocation,
            size
        );
        OPEN_CFW_FILE_HEAP_MUTEX_RELEASE(
            OPEN_CFW_FILE_HEAP_MUTEX_HANDLE
        );
    } else {
        open_cfw_file_heap_timeout(
            OPEN_CFW_FILE_HEAP_REALLOCATE_FAILURE,
            0x449U
        );
    }
    return result;
}

__attribute__((used, noinline))
int open_cfw_file_runtime_initialize(void)
{
    void *primary_mutex = OPEN_CFW_FILE_RUNTIME_MUTEX_CREATE(0U);
    void *heap_mutex;

    OPEN_CFW_FILE_RUNTIME_STORE_PRIMARY_MUTEX(primary_mutex);
    heap_mutex = OPEN_CFW_FILE_RUNTIME_MUTEX_CREATE(0U);
    OPEN_CFW_FILE_RUNTIME_STORE_HEAP_MUTEX(heap_mutex);
    if (primary_mutex == (void *)0 || heap_mutex == (void *)0) {
        if ((OPEN_CFW_FILE_LOG_FLAGS() & 2U) != 0U) {
            OPEN_CFW_FILE_LOG(
                1U,
                OPEN_CFW_FILE_RUNTIME_LOG_TAG,
                OPEN_CFW_FILE_RUNTIME_LOG_FILE,
                OPEN_CFW_FILE_RUNTIME_LOG_FUNCTION,
                0x47AU,
                OPEN_CFW_FILE_RUNTIME_INIT_FAILURE
            );
        }
        if (open_cfw_file_backend_log_enabled()) {
            OPEN_CFW_FILE_BACKEND_LOG(
                0x04000000U,
                OPEN_CFW_FILE_RUNTIME_INIT_FAILURE_BACKEND,
                OPEN_CFW_FILE_RUNTIME_INIT_FAILURE_BACKEND
            );
        }
        return -1;
    }
    if ((OPEN_CFW_FILE_LOG_FLAGS() & 2U) != 0U) {
        OPEN_CFW_FILE_LOG(
            3U,
            OPEN_CFW_FILE_RUNTIME_LOG_TAG,
            OPEN_CFW_FILE_RUNTIME_LOG_FILE,
            OPEN_CFW_FILE_RUNTIME_LOG_FUNCTION,
            0x47EU,
            OPEN_CFW_FILE_RUNTIME_INIT_SUCCESS
        );
    }
    if (open_cfw_file_backend_log_enabled()) {
        OPEN_CFW_FILE_BACKEND_LOG(
            0x0C000000U,
            OPEN_CFW_FILE_RUNTIME_INIT_SUCCESS_BACKEND,
            OPEN_CFW_FILE_RUNTIME_INIT_SUCCESS_BACKEND
        );
    }
    return 0;
}

#undef OPEN_CFW_FILE_RUNTIME_INIT_SUCCESS_BACKEND
#undef OPEN_CFW_FILE_RUNTIME_INIT_SUCCESS
#undef OPEN_CFW_FILE_RUNTIME_INIT_FAILURE_BACKEND
#undef OPEN_CFW_FILE_RUNTIME_INIT_FAILURE
#undef OPEN_CFW_FILE_RUNTIME_LOG_FUNCTION
#undef OPEN_CFW_FILE_RUNTIME_LOG_FILE
#undef OPEN_CFW_FILE_RUNTIME_LOG_TAG
#undef OPEN_CFW_FILE_RUNTIME_STORE_HEAP_MUTEX
#undef OPEN_CFW_FILE_RUNTIME_STORE_PRIMARY_MUTEX
#undef OPEN_CFW_FILE_RUNTIME_MUTEX_CREATE
#undef OPEN_CFW_FILE_HEAP_REALLOCATE_FAILURE
#undef OPEN_CFW_FILE_HEAP_FREE_FAILURE
#undef OPEN_CFW_FILE_HEAP_ALLOCATE_FAILURE
#undef OPEN_CFW_FILE_HEAP_DIAGNOSTIC_FILE
#undef OPEN_CFW_FILE_HEAP_DIAGNOSTIC_CONTEXT
#undef OPEN_CFW_FILE_HEAP_DIAGNOSTIC
#undef OPEN_CFW_FILE_HEAP_FORMAT
#undef OPEN_CFW_FILE_HEAP_REALLOCATE_BACKEND
#undef OPEN_CFW_FILE_HEAP_FREE_BACKEND
#undef OPEN_CFW_FILE_HEAP_ALLOCATE_BACKEND
#undef OPEN_CFW_FILE_HEAP_MUTEX_RELEASE
#undef OPEN_CFW_FILE_HEAP_MUTEX_ACQUIRE
#undef OPEN_CFW_FILE_HEAP_HANDLE
#undef OPEN_CFW_FILE_HEAP_MUTEX_HANDLE
#undef OPEN_CFW_FILE_BACKEND_CLOSEDIR
#undef OPEN_CFW_DIRECTORY_BACKEND_NAME_OFFSET
#undef OPEN_CFW_DIRECTORY_BACKEND_ENTRY_OFFSET
#undef OPEN_CFW_FILE_DIRENT
#undef OPEN_CFW_FILE_BACKEND_READDIR
#undef OPEN_CFW_FILE_BACKEND_OPENDIR
#undef OPEN_CFW_FILE_BACKEND_MKDIR
#undef OPEN_CFW_FILE_BACKEND_RENAME
#undef OPEN_CFW_FILE_BACKEND_REMOVE
#undef OPEN_CFW_FILE_ERRNO_LOCATION
#undef OPEN_CFW_FILE_BACKEND_FLUSH
#undef OPEN_CFW_FILE_BACKEND_SIZE
#undef OPEN_CFW_FILE_BACKEND_TELL
#undef OPEN_CFW_FILE_BACKEND_SEEK
#undef OPEN_CFW_FILE_WRITE_SHORT_BACKEND
#undef OPEN_CFW_FILE_WRITE_SHORT
#undef OPEN_CFW_FILE_WRITE_ERROR_BACKEND
#undef OPEN_CFW_FILE_WRITE_ERROR
#undef OPEN_CFW_FILE_WRITE_TIMEOUT_BACKEND
#undef OPEN_CFW_FILE_WRITE_TIMEOUT
#undef OPEN_CFW_FILE_WRITE_NULL_BACKEND
#undef OPEN_CFW_FILE_WRITE_NULL
#undef OPEN_CFW_FILE_WRITE_FUNCTION
#undef OPEN_CFW_FILE_LOG_FILE
#undef OPEN_CFW_FILE_LOG_TAG
#undef OPEN_CFW_FILE_BACKEND_LOG
#undef OPEN_CFW_FILE_LOG
#undef OPEN_CFW_FILE_LOG_FLAGS
#undef OPEN_CFW_FILE_BACKEND_WRITE
#undef OPEN_CFW_FILE_BACKEND_READ
#undef OPEN_CFW_FILE_BACKEND_CLOSE
#undef OPEN_CFW_FILE_BACKEND_OPEN
#undef OPEN_CFW_FILE_MUTEX_RELEASE
#undef OPEN_CFW_FILE_MUTEX_ACQUIRE
#undef OPEN_CFW_FILE_FREE
#undef OPEN_CFW_FILE_ALLOCATE
#undef OPEN_CFW_FILE_READY_STATE
#undef OPEN_CFW_FILE_MUTEX_HANDLE
#undef OPEN_CFW_FILE_DRIVER
