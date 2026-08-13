#include <stdarg.h>

unsigned int open_cfw_test_file_storage[24];
unsigned char open_cfw_test_directory_storage[0x240];
unsigned char open_cfw_test_dirent_storage[0x101];
void *open_cfw_test_file_allocate_result;
unsigned int open_cfw_test_file_allocate_calls;
unsigned int open_cfw_test_file_allocate_size;
unsigned int open_cfw_test_file_free_calls;
void *open_cfw_test_file_free_allocation;
void *open_cfw_test_file_mutex_handle;
unsigned int open_cfw_test_file_ready_state;
int open_cfw_test_file_mutex_acquire_result;
unsigned int open_cfw_test_file_mutex_acquire_calls;
void *open_cfw_test_file_mutex_acquire_mutex;
unsigned int open_cfw_test_file_mutex_acquire_timeout;
unsigned int open_cfw_test_file_mutex_release_calls;
void *open_cfw_test_file_mutex_release_mutex;
int open_cfw_test_file_backend_open_result;
unsigned int open_cfw_test_file_backend_open_calls;
unsigned int open_cfw_test_file_backend_open_driver;
void *open_cfw_test_file_backend_open_state;
const void *open_cfw_test_file_backend_open_path;
unsigned int open_cfw_test_file_backend_open_flags;
int open_cfw_test_file_backend_close_result;
unsigned int open_cfw_test_file_backend_close_calls;
unsigned int open_cfw_test_file_backend_close_driver;
void *open_cfw_test_file_backend_close_state;
int open_cfw_test_file_backend_read_result;
unsigned int open_cfw_test_file_backend_read_calls;
unsigned int open_cfw_test_file_backend_read_driver;
void *open_cfw_test_file_backend_read_state;
void *open_cfw_test_file_backend_read_buffer;
unsigned int open_cfw_test_file_backend_read_size;
int open_cfw_test_file_backend_write_result;
unsigned int open_cfw_test_file_backend_write_calls;
unsigned int open_cfw_test_file_backend_write_driver;
void *open_cfw_test_file_backend_write_state;
const void *open_cfw_test_file_backend_write_buffer;
unsigned int open_cfw_test_file_backend_write_size;
int open_cfw_test_file_backend_seek_result;
unsigned int open_cfw_test_file_backend_seek_calls;
unsigned int open_cfw_test_file_backend_seek_driver;
void *open_cfw_test_file_backend_seek_state;
int open_cfw_test_file_backend_seek_offset;
unsigned int open_cfw_test_file_backend_seek_origin;
int open_cfw_test_file_backend_tell_result;
unsigned int open_cfw_test_file_backend_tell_calls;
unsigned int open_cfw_test_file_backend_tell_driver;
void *open_cfw_test_file_backend_tell_state;
int open_cfw_test_file_backend_size_result;
unsigned int open_cfw_test_file_backend_size_calls;
unsigned int open_cfw_test_file_backend_size_driver;
void *open_cfw_test_file_backend_size_state;
int open_cfw_test_file_backend_flush_result;
unsigned int open_cfw_test_file_backend_flush_calls;
unsigned int open_cfw_test_file_backend_flush_driver;
void *open_cfw_test_file_backend_flush_state;
int open_cfw_test_file_backend_remove_result;
unsigned int open_cfw_test_file_backend_remove_calls;
unsigned int open_cfw_test_file_backend_remove_driver;
const void *open_cfw_test_file_backend_remove_path;
int open_cfw_test_file_backend_rename_result;
unsigned int open_cfw_test_file_backend_rename_calls;
unsigned int open_cfw_test_file_backend_rename_driver;
const void *open_cfw_test_file_backend_rename_old_path;
const void *open_cfw_test_file_backend_rename_new_path;
int open_cfw_test_file_backend_mkdir_result;
unsigned int open_cfw_test_file_backend_mkdir_calls;
unsigned int open_cfw_test_file_backend_mkdir_driver;
const void *open_cfw_test_file_backend_mkdir_path;
int open_cfw_test_file_backend_opendir_result;
unsigned int open_cfw_test_file_backend_opendir_calls;
unsigned int open_cfw_test_file_backend_opendir_driver;
void *open_cfw_test_file_backend_opendir_state;
const void *open_cfw_test_file_backend_opendir_path;
int open_cfw_test_file_backend_readdir_result;
unsigned int open_cfw_test_file_backend_readdir_calls;
unsigned int open_cfw_test_file_backend_readdir_driver;
void *open_cfw_test_file_backend_readdir_state;
void *open_cfw_test_file_backend_readdir_entry;
int open_cfw_test_file_backend_closedir_result;
unsigned int open_cfw_test_file_backend_closedir_calls;
unsigned int open_cfw_test_file_backend_closedir_driver;
void *open_cfw_test_file_backend_closedir_state;
void *open_cfw_test_file_heap_mutex_handle;
void *open_cfw_test_file_heap_handle;
void *open_cfw_test_file_heap_allocate_result;
unsigned int open_cfw_test_file_heap_allocate_calls;
void *open_cfw_test_file_heap_allocate_heap;
unsigned int open_cfw_test_file_heap_allocate_size;
unsigned int open_cfw_test_file_heap_free_calls;
void *open_cfw_test_file_heap_free_heap;
void *open_cfw_test_file_heap_free_allocation;
void *open_cfw_test_file_heap_reallocate_result;
unsigned int open_cfw_test_file_heap_reallocate_calls;
void *open_cfw_test_file_heap_reallocate_heap;
void *open_cfw_test_file_heap_reallocate_allocation;
unsigned int open_cfw_test_file_heap_reallocate_size;
unsigned int open_cfw_test_file_heap_format_calls;
const void *open_cfw_test_file_heap_format_string;
unsigned int open_cfw_test_file_heap_diagnostic_calls;
const void *open_cfw_test_file_heap_diagnostic_context;
const void *open_cfw_test_file_heap_diagnostic_file;
unsigned int open_cfw_test_file_heap_diagnostic_line;
void *open_cfw_test_file_runtime_mutex_create_results[2];
unsigned int open_cfw_test_file_runtime_mutex_create_result_count;
unsigned int open_cfw_test_file_runtime_mutex_create_calls;
unsigned int open_cfw_test_file_runtime_mutex_create_modes[2];
int open_cfw_test_file_errno_value;
unsigned int open_cfw_test_file_errno_location_calls;
unsigned int open_cfw_test_file_flag_values[8];
unsigned int open_cfw_test_file_flag_value_count;
unsigned int open_cfw_test_file_flag_calls;
unsigned int open_cfw_test_file_log_calls;
unsigned int open_cfw_test_file_log_level;
const void *open_cfw_test_file_log_tag;
const void *open_cfw_test_file_log_file;
const void *open_cfw_test_file_log_function;
unsigned int open_cfw_test_file_log_line;
const void *open_cfw_test_file_log_format;
unsigned int open_cfw_test_file_log_argument_count;
int open_cfw_test_file_log_argument0;
unsigned int open_cfw_test_file_log_argument1;
unsigned int open_cfw_test_file_backend_log_calls;
unsigned int open_cfw_test_file_backend_log_mask;
const void *open_cfw_test_file_backend_log_format;
const void *open_cfw_test_file_backend_log_duplicate_format;
unsigned int open_cfw_test_file_backend_log_argument_count;
int open_cfw_test_file_backend_log_argument0;
unsigned int open_cfw_test_file_backend_log_argument1;
unsigned int open_cfw_test_file_trace_count;
unsigned int open_cfw_test_file_trace[32];

static void open_cfw_test_file_record(unsigned int event)
{
    unsigned int index = open_cfw_test_file_trace_count++;

    if (index < 32U) {
        open_cfw_test_file_trace[index] = event;
    }
}

void *open_cfw_test_file_allocate(unsigned int size)
{
    open_cfw_test_file_record(1U);
    open_cfw_test_file_allocate_calls += 1U;
    open_cfw_test_file_allocate_size = size;
    return open_cfw_test_file_allocate_result;
}

void open_cfw_test_file_free(void *allocation)
{
    open_cfw_test_file_record(2U);
    open_cfw_test_file_free_calls += 1U;
    open_cfw_test_file_free_allocation = allocation;
}

int open_cfw_test_file_mutex_acquire(void *mutex, unsigned int timeout)
{
    open_cfw_test_file_record(3U);
    open_cfw_test_file_mutex_acquire_calls += 1U;
    open_cfw_test_file_mutex_acquire_mutex = mutex;
    open_cfw_test_file_mutex_acquire_timeout = timeout;
    return open_cfw_test_file_mutex_acquire_result;
}

void open_cfw_test_file_mutex_release(void *mutex)
{
    open_cfw_test_file_record(4U);
    open_cfw_test_file_mutex_release_calls += 1U;
    open_cfw_test_file_mutex_release_mutex = mutex;
}

int open_cfw_test_file_backend_open(
    unsigned int driver,
    void *state,
    const void *path,
    unsigned int flags
)
{
    open_cfw_test_file_record(5U);
    open_cfw_test_file_backend_open_calls += 1U;
    open_cfw_test_file_backend_open_driver = driver;
    open_cfw_test_file_backend_open_state = state;
    open_cfw_test_file_backend_open_path = path;
    open_cfw_test_file_backend_open_flags = flags;
    return open_cfw_test_file_backend_open_result;
}

int open_cfw_test_file_backend_close(unsigned int driver, void *state)
{
    open_cfw_test_file_record(6U);
    open_cfw_test_file_backend_close_calls += 1U;
    open_cfw_test_file_backend_close_driver = driver;
    open_cfw_test_file_backend_close_state = state;
    return open_cfw_test_file_backend_close_result;
}

int open_cfw_test_file_backend_read(
    unsigned int driver,
    void *state,
    void *buffer,
    unsigned int size
)
{
    open_cfw_test_file_record(7U);
    open_cfw_test_file_backend_read_calls += 1U;
    open_cfw_test_file_backend_read_driver = driver;
    open_cfw_test_file_backend_read_state = state;
    open_cfw_test_file_backend_read_buffer = buffer;
    open_cfw_test_file_backend_read_size = size;
    return open_cfw_test_file_backend_read_result;
}

int open_cfw_test_file_backend_write(
    unsigned int driver,
    void *state,
    const void *buffer,
    unsigned int size
)
{
    open_cfw_test_file_record(8U);
    open_cfw_test_file_backend_write_calls += 1U;
    open_cfw_test_file_backend_write_driver = driver;
    open_cfw_test_file_backend_write_state = state;
    open_cfw_test_file_backend_write_buffer = buffer;
    open_cfw_test_file_backend_write_size = size;
    return open_cfw_test_file_backend_write_result;
}

int open_cfw_test_file_backend_seek(
    unsigned int driver,
    void *state,
    int offset,
    unsigned int origin
)
{
    open_cfw_test_file_record(12U);
    open_cfw_test_file_backend_seek_calls += 1U;
    open_cfw_test_file_backend_seek_driver = driver;
    open_cfw_test_file_backend_seek_state = state;
    open_cfw_test_file_backend_seek_offset = offset;
    open_cfw_test_file_backend_seek_origin = origin;
    return open_cfw_test_file_backend_seek_result;
}

int open_cfw_test_file_backend_tell(unsigned int driver, void *state)
{
    open_cfw_test_file_record(13U);
    open_cfw_test_file_backend_tell_calls += 1U;
    open_cfw_test_file_backend_tell_driver = driver;
    open_cfw_test_file_backend_tell_state = state;
    return open_cfw_test_file_backend_tell_result;
}

int open_cfw_test_file_backend_size(unsigned int driver, void *state)
{
    open_cfw_test_file_record(14U);
    open_cfw_test_file_backend_size_calls += 1U;
    open_cfw_test_file_backend_size_driver = driver;
    open_cfw_test_file_backend_size_state = state;
    return open_cfw_test_file_backend_size_result;
}

int open_cfw_test_file_backend_flush(unsigned int driver, void *state)
{
    open_cfw_test_file_record(16U);
    open_cfw_test_file_backend_flush_calls += 1U;
    open_cfw_test_file_backend_flush_driver = driver;
    open_cfw_test_file_backend_flush_state = state;
    return open_cfw_test_file_backend_flush_result;
}

int open_cfw_test_file_backend_remove(
    unsigned int driver,
    const void *path
)
{
    open_cfw_test_file_record(17U);
    open_cfw_test_file_backend_remove_calls += 1U;
    open_cfw_test_file_backend_remove_driver = driver;
    open_cfw_test_file_backend_remove_path = path;
    return open_cfw_test_file_backend_remove_result;
}

int open_cfw_test_file_backend_rename(
    unsigned int driver,
    const void *old_path,
    const void *new_path
)
{
    open_cfw_test_file_record(18U);
    open_cfw_test_file_backend_rename_calls += 1U;
    open_cfw_test_file_backend_rename_driver = driver;
    open_cfw_test_file_backend_rename_old_path = old_path;
    open_cfw_test_file_backend_rename_new_path = new_path;
    return open_cfw_test_file_backend_rename_result;
}

int open_cfw_test_file_backend_mkdir(
    unsigned int driver,
    const void *path
)
{
    open_cfw_test_file_record(19U);
    open_cfw_test_file_backend_mkdir_calls += 1U;
    open_cfw_test_file_backend_mkdir_driver = driver;
    open_cfw_test_file_backend_mkdir_path = path;
    return open_cfw_test_file_backend_mkdir_result;
}

int open_cfw_test_file_backend_opendir(
    unsigned int driver,
    void *state,
    const void *path
)
{
    open_cfw_test_file_record(20U);
    open_cfw_test_file_backend_opendir_calls += 1U;
    open_cfw_test_file_backend_opendir_driver = driver;
    open_cfw_test_file_backend_opendir_state = state;
    open_cfw_test_file_backend_opendir_path = path;
    return open_cfw_test_file_backend_opendir_result;
}

int open_cfw_test_file_backend_readdir(
    unsigned int driver,
    void *state,
    void *entry
)
{
    open_cfw_test_file_record(21U);
    open_cfw_test_file_backend_readdir_calls += 1U;
    open_cfw_test_file_backend_readdir_driver = driver;
    open_cfw_test_file_backend_readdir_state = state;
    open_cfw_test_file_backend_readdir_entry = entry;
    return open_cfw_test_file_backend_readdir_result;
}

int open_cfw_test_file_backend_closedir(unsigned int driver, void *state)
{
    open_cfw_test_file_record(22U);
    open_cfw_test_file_backend_closedir_calls += 1U;
    open_cfw_test_file_backend_closedir_driver = driver;
    open_cfw_test_file_backend_closedir_state = state;
    return open_cfw_test_file_backend_closedir_result;
}

void *open_cfw_test_file_heap_allocate_backend(
    void *heap,
    unsigned int size
)
{
    open_cfw_test_file_record(23U);
    open_cfw_test_file_heap_allocate_calls += 1U;
    open_cfw_test_file_heap_allocate_heap = heap;
    open_cfw_test_file_heap_allocate_size = size;
    return open_cfw_test_file_heap_allocate_result;
}

void open_cfw_test_file_heap_free_backend(
    void *heap,
    void *allocation
)
{
    open_cfw_test_file_record(24U);
    open_cfw_test_file_heap_free_calls += 1U;
    open_cfw_test_file_heap_free_heap = heap;
    open_cfw_test_file_heap_free_allocation = allocation;
}

void *open_cfw_test_file_heap_reallocate_backend(
    void *heap,
    void *allocation,
    unsigned int size
)
{
    open_cfw_test_file_record(25U);
    open_cfw_test_file_heap_reallocate_calls += 1U;
    open_cfw_test_file_heap_reallocate_heap = heap;
    open_cfw_test_file_heap_reallocate_allocation = allocation;
    open_cfw_test_file_heap_reallocate_size = size;
    return open_cfw_test_file_heap_reallocate_result;
}

unsigned int open_cfw_test_file_heap_format(const char *format, ...)
{
    open_cfw_test_file_record(26U);
    open_cfw_test_file_heap_format_calls += 1U;
    open_cfw_test_file_heap_format_string = format;
    return 0U;
}

void open_cfw_test_file_heap_diagnostic(
    const void *context,
    const void *file,
    unsigned int line
)
{
    open_cfw_test_file_record(27U);
    open_cfw_test_file_heap_diagnostic_calls += 1U;
    open_cfw_test_file_heap_diagnostic_context = context;
    open_cfw_test_file_heap_diagnostic_file = file;
    open_cfw_test_file_heap_diagnostic_line = line;
}

void *open_cfw_test_file_runtime_mutex_create(unsigned int mode)
{
    unsigned int index = open_cfw_test_file_runtime_mutex_create_calls++;

    open_cfw_test_file_record(28U);
    if (index < 2U) {
        open_cfw_test_file_runtime_mutex_create_modes[index] = mode;
    }
    if (open_cfw_test_file_runtime_mutex_create_result_count == 0U) {
        return (void *)0;
    }
    if (index >= open_cfw_test_file_runtime_mutex_create_result_count) {
        index = open_cfw_test_file_runtime_mutex_create_result_count - 1U;
    }
    return open_cfw_test_file_runtime_mutex_create_results[index];
}

int *open_cfw_test_file_errno_location(void)
{
    open_cfw_test_file_record(15U);
    open_cfw_test_file_errno_location_calls += 1U;
    return &open_cfw_test_file_errno_value;
}

unsigned int open_cfw_test_file_log_flags(void)
{
    unsigned int index = open_cfw_test_file_flag_calls++;

    open_cfw_test_file_record(9U);
    if (open_cfw_test_file_flag_value_count == 0U) {
        return 0U;
    }
    if (index >= open_cfw_test_file_flag_value_count) {
        index = open_cfw_test_file_flag_value_count - 1U;
    }
    return open_cfw_test_file_flag_values[index];
}

void open_cfw_test_file_log(
    unsigned int level,
    const void *tag,
    const void *file,
    const void *function,
    unsigned int line,
    const void *format,
    ...
)
{
    va_list arguments;

    open_cfw_test_file_record(10U);
    open_cfw_test_file_log_calls += 1U;
    open_cfw_test_file_log_level = level;
    open_cfw_test_file_log_tag = tag;
    open_cfw_test_file_log_file = file;
    open_cfw_test_file_log_function = function;
    open_cfw_test_file_log_line = line;
    open_cfw_test_file_log_format = format;
    open_cfw_test_file_log_argument_count = 0U;
    va_start(arguments, format);
    if (line == 0x23CU) {
        open_cfw_test_file_log_argument_count = 1U;
        open_cfw_test_file_log_argument0 =
            (int)va_arg(arguments, unsigned int);
    } else if (line == 0x24AU || line == 0x24EU) {
        open_cfw_test_file_log_argument_count = 2U;
        open_cfw_test_file_log_argument0 = va_arg(arguments, int);
        open_cfw_test_file_log_argument1 =
            va_arg(arguments, unsigned int);
    }
    va_end(arguments);
}

void open_cfw_test_file_backend_log(
    unsigned int mask,
    const void *format,
    const void *duplicate_format,
    ...
)
{
    va_list arguments;

    open_cfw_test_file_record(11U);
    open_cfw_test_file_backend_log_calls += 1U;
    open_cfw_test_file_backend_log_mask = mask;
    open_cfw_test_file_backend_log_format = format;
    open_cfw_test_file_backend_log_duplicate_format = duplicate_format;
    open_cfw_test_file_backend_log_argument_count = 0U;
    va_start(arguments, duplicate_format);
    if (mask == 0x04400000U) {
        open_cfw_test_file_backend_log_argument_count = 1U;
        open_cfw_test_file_backend_log_argument0 =
            (int)va_arg(arguments, unsigned int);
    } else if (mask == 0x04800000U || mask == 0x08800000U) {
        open_cfw_test_file_backend_log_argument_count = 2U;
        open_cfw_test_file_backend_log_argument0 = va_arg(arguments, int);
        open_cfw_test_file_backend_log_argument1 =
            va_arg(arguments, unsigned int);
    }
    va_end(arguments);
}

#define OPEN_CFW_FILE_DRIVER 0x20071AC8U
#define OPEN_CFW_FILE_MUTEX_HANDLE open_cfw_test_file_mutex_handle
#define OPEN_CFW_FILE_READY_STATE open_cfw_test_file_ready_state
#define OPEN_CFW_FILE_ALLOCATE(size) open_cfw_test_file_allocate(size)
#define OPEN_CFW_FILE_FREE(allocation) open_cfw_test_file_free(allocation)
#define OPEN_CFW_FILE_MUTEX_ACQUIRE(mutex, timeout) \
    open_cfw_test_file_mutex_acquire((mutex), (timeout))
#define OPEN_CFW_FILE_MUTEX_RELEASE(mutex) \
    open_cfw_test_file_mutex_release(mutex)
#define OPEN_CFW_FILE_BACKEND_OPEN(driver, state, path, flags) \
    open_cfw_test_file_backend_open((driver), (state), (path), (flags))
#define OPEN_CFW_FILE_BACKEND_CLOSE(driver, state) \
    open_cfw_test_file_backend_close((driver), (state))
#define OPEN_CFW_FILE_BACKEND_READ(driver, state, buffer, size) \
    open_cfw_test_file_backend_read((driver), (state), (buffer), (size))
#define OPEN_CFW_FILE_BACKEND_WRITE(driver, state, buffer, size) \
    open_cfw_test_file_backend_write((driver), (state), (buffer), (size))
#define OPEN_CFW_FILE_BACKEND_SEEK(driver, state, offset, origin) \
    open_cfw_test_file_backend_seek((driver), (state), (offset), (origin))
#define OPEN_CFW_FILE_BACKEND_TELL(driver, state) \
    open_cfw_test_file_backend_tell((driver), (state))
#define OPEN_CFW_FILE_BACKEND_SIZE(driver, state) \
    open_cfw_test_file_backend_size((driver), (state))
#define OPEN_CFW_FILE_BACKEND_FLUSH(driver, state) \
    open_cfw_test_file_backend_flush((driver), (state))
#define OPEN_CFW_FILE_BACKEND_REMOVE(driver, path) \
    open_cfw_test_file_backend_remove((driver), (path))
#define OPEN_CFW_FILE_BACKEND_RENAME(driver, old_path, new_path) \
    open_cfw_test_file_backend_rename((driver), (old_path), (new_path))
#define OPEN_CFW_FILE_BACKEND_MKDIR(driver, path) \
    open_cfw_test_file_backend_mkdir((driver), (path))
#define OPEN_CFW_FILE_BACKEND_OPENDIR(driver, state, path) \
    open_cfw_test_file_backend_opendir((driver), (state), (path))
#define OPEN_CFW_FILE_BACKEND_READDIR(driver, state, entry) \
    open_cfw_test_file_backend_readdir((driver), (state), (entry))
#define OPEN_CFW_FILE_BACKEND_CLOSEDIR(driver, state) \
    open_cfw_test_file_backend_closedir((driver), (state))
#define OPEN_CFW_FILE_DIRENT \
    ((open_cfw_dirent *)(void *)open_cfw_test_dirent_storage)
#define OPEN_CFW_FILE_HEAP_MUTEX_HANDLE \
    open_cfw_test_file_heap_mutex_handle
#define OPEN_CFW_FILE_HEAP_HANDLE open_cfw_test_file_heap_handle
#define OPEN_CFW_FILE_HEAP_ALLOCATE_BACKEND(heap, size) \
    open_cfw_test_file_heap_allocate_backend((heap), (size))
#define OPEN_CFW_FILE_HEAP_FREE_BACKEND(heap, allocation) \
    open_cfw_test_file_heap_free_backend((heap), (allocation))
#define OPEN_CFW_FILE_HEAP_REALLOCATE_BACKEND(heap, allocation, size) \
    open_cfw_test_file_heap_reallocate_backend( \
        (heap), \
        (allocation), \
        (size) \
    )
#define OPEN_CFW_FILE_HEAP_FORMAT open_cfw_test_file_heap_format
#define OPEN_CFW_FILE_HEAP_DIAGNOSTIC \
    open_cfw_test_file_heap_diagnostic
#define OPEN_CFW_FILE_RUNTIME_MUTEX_CREATE(mode) \
    open_cfw_test_file_runtime_mutex_create(mode)
#define OPEN_CFW_FILE_RUNTIME_STORE_PRIMARY_MUTEX(value) \
    do { \
        open_cfw_test_file_mutex_handle = (value); \
    } while (0)
#define OPEN_CFW_FILE_RUNTIME_STORE_HEAP_MUTEX(value) \
    do { \
        open_cfw_test_file_heap_mutex_handle = (value); \
    } while (0)
#define OPEN_CFW_FILE_ERRNO_LOCATION() open_cfw_test_file_errno_location()
#define OPEN_CFW_FILE_LOG_FLAGS() open_cfw_test_file_log_flags()
#define OPEN_CFW_FILE_LOG open_cfw_test_file_log
#define OPEN_CFW_FILE_BACKEND_LOG open_cfw_test_file_backend_log

#include "../../components/apollo_main/core_overlay/file_runtime.c"
