/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the bounded littlefs startup cluster.
 */

unsigned int open_cfw_test_file_system_log_level(void);
void open_cfw_test_file_system_log(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
void open_cfw_test_file_system_trace(
    unsigned int,
    const void *,
    const void *,
    ...
);
int open_cfw_test_file_system_directory_open(
    void *,
    void *,
    const char *
);
int open_cfw_test_file_system_directory_close(void *, void *);
int open_cfw_test_file_system_mkdir(void *, const char *);
int open_cfw_test_file_system_unmount(void *);
int open_cfw_test_file_system_format(void *, const void *);
int open_cfw_test_file_system_mount(void *, const void *);
int open_cfw_test_file_system_file_open(
    void *,
    void *,
    const char *,
    unsigned int
);
int open_cfw_test_file_system_file_read(
    void *,
    void *,
    void *,
    unsigned int
);
int open_cfw_test_file_system_file_rewind(void *, void *);
int open_cfw_test_file_system_file_write(
    void *,
    void *,
    const void *,
    unsigned int
);
int open_cfw_test_file_system_file_close(void *, void *);
int open_cfw_test_file_system_flash_read(
    unsigned int,
    void *,
    unsigned int
);
int open_cfw_test_file_system_flash_program(
    unsigned int,
    const void *,
    unsigned int
);
int open_cfw_test_file_system_flash_erase(unsigned int);
unsigned int open_cfw_test_file_system_read_log(const char *, ...);

#define OPEN_CFW_FILE_SYSTEM_CONTEXT ((void *)0x11110000U)
#define OPEN_CFW_FILE_SYSTEM_CONFIG ((const void *)0x22220000U)
#define OPEN_CFW_FILE_SYSTEM_READY_BYTE \
    open_cfw_test_file_system_ready_byte
#define OPEN_CFW_FILE_SYSTEM_BOOT_FILE ((void *)0x33330000U)
#define OPEN_CFW_FILE_SYSTEM_LOG_LEVEL() \
    open_cfw_test_file_system_log_level()
#define OPEN_CFW_FILE_SYSTEM_LOG(...) \
    open_cfw_test_file_system_log(__VA_ARGS__)
#define OPEN_CFW_FILE_SYSTEM_TRACE(...) \
    open_cfw_test_file_system_trace(__VA_ARGS__)
#define OPEN_CFW_FILE_SYSTEM_DIRECTORY_OPEN(fs, directory, path) \
    open_cfw_test_file_system_directory_open((fs), (directory), (path))
#define OPEN_CFW_FILE_SYSTEM_DIRECTORY_CLOSE(fs, directory) \
    open_cfw_test_file_system_directory_close((fs), (directory))
#define OPEN_CFW_FILE_SYSTEM_MKDIR(fs, path) \
    open_cfw_test_file_system_mkdir((fs), (path))
#define OPEN_CFW_FILE_SYSTEM_UNMOUNT(fs) \
    open_cfw_test_file_system_unmount((fs))
#define OPEN_CFW_FILE_SYSTEM_FORMAT(fs, config) \
    open_cfw_test_file_system_format((fs), (config))
#define OPEN_CFW_FILE_SYSTEM_MOUNT(fs, config) \
    open_cfw_test_file_system_mount((fs), (config))
#define OPEN_CFW_FILE_SYSTEM_FILE_OPEN(fs, file, path, flags) \
    open_cfw_test_file_system_file_open((fs), (file), (path), (flags))
#define OPEN_CFW_FILE_SYSTEM_FILE_READ(fs, file, buffer, size) \
    open_cfw_test_file_system_file_read((fs), (file), (buffer), (size))
#define OPEN_CFW_FILE_SYSTEM_FILE_REWIND(fs, file) \
    open_cfw_test_file_system_file_rewind((fs), (file))
#define OPEN_CFW_FILE_SYSTEM_FILE_WRITE(fs, file, buffer, size) \
    open_cfw_test_file_system_file_write((fs), (file), (buffer), (size))
#define OPEN_CFW_FILE_SYSTEM_FILE_CLOSE(fs, file) \
    open_cfw_test_file_system_file_close((fs), (file))
#define OPEN_CFW_FILE_SYSTEM_FLASH_READ(address, buffer, size) \
    open_cfw_test_file_system_flash_read((address), (buffer), (size))
#define OPEN_CFW_FILE_SYSTEM_FLASH_PROGRAM(address, buffer, size) \
    open_cfw_test_file_system_flash_program((address), (buffer), (size))
#define OPEN_CFW_FILE_SYSTEM_FLASH_ERASE(address) \
    open_cfw_test_file_system_flash_erase((address))
#define OPEN_CFW_FILE_SYSTEM_READ_LOG(...) \
    open_cfw_test_file_system_read_log(__VA_ARGS__)

unsigned int open_cfw_test_file_system_events[128];
unsigned int open_cfw_test_file_system_event_count;
unsigned int open_cfw_test_file_system_levels[128];
unsigned int open_cfw_test_file_system_level_count;
unsigned int open_cfw_test_file_system_level_index;
__UINTPTR_TYPE__ open_cfw_test_file_system_log_records[16][8];
unsigned int open_cfw_test_file_system_log_count;
__UINTPTR_TYPE__ open_cfw_test_file_system_trace_records[16][5];
unsigned int open_cfw_test_file_system_trace_count;
int open_cfw_test_file_system_directory_open_results[16];
unsigned int open_cfw_test_file_system_directory_open_calls;
__UINTPTR_TYPE__ open_cfw_test_file_system_directory_paths[16];
__UINTPTR_TYPE__ open_cfw_test_file_system_directory_objects[16];
int open_cfw_test_file_system_mkdir_results[16];
unsigned int open_cfw_test_file_system_mkdir_calls;
__UINTPTR_TYPE__ open_cfw_test_file_system_mkdir_paths[16];
unsigned int open_cfw_test_file_system_directory_close_calls;
int open_cfw_test_file_system_unmount_result;
unsigned int open_cfw_test_file_system_unmount_calls;
int open_cfw_test_file_system_format_result;
unsigned int open_cfw_test_file_system_format_calls;
int open_cfw_test_file_system_mount_results[8];
unsigned int open_cfw_test_file_system_mount_calls;
unsigned char open_cfw_test_file_system_ready_byte;
unsigned int open_cfw_test_file_system_file_open_calls;
__UINTPTR_TYPE__ open_cfw_test_file_system_file_open_path;
unsigned int open_cfw_test_file_system_file_open_flags;
unsigned int open_cfw_test_file_system_file_read_calls;
int open_cfw_test_file_system_boot_count_seed;
unsigned int open_cfw_test_file_system_file_rewind_calls;
unsigned int open_cfw_test_file_system_file_write_calls;
int open_cfw_test_file_system_boot_count_written;
unsigned int open_cfw_test_file_system_file_close_calls;
int open_cfw_test_file_system_flash_read_result;
unsigned int open_cfw_test_file_system_flash_read_calls;
unsigned int open_cfw_test_file_system_flash_read_address;
__UINTPTR_TYPE__ open_cfw_test_file_system_flash_read_buffer;
unsigned int open_cfw_test_file_system_flash_read_size;
int open_cfw_test_file_system_flash_program_result;
unsigned int open_cfw_test_file_system_flash_program_calls;
unsigned int open_cfw_test_file_system_flash_program_address;
__UINTPTR_TYPE__ open_cfw_test_file_system_flash_program_buffer;
unsigned int open_cfw_test_file_system_flash_program_size;
int open_cfw_test_file_system_flash_erase_result;
unsigned int open_cfw_test_file_system_flash_erase_calls;
unsigned int open_cfw_test_file_system_flash_erase_address;
unsigned int open_cfw_test_file_system_read_log_calls;
__UINTPTR_TYPE__ open_cfw_test_file_system_read_log_arguments[6];

static void open_cfw_test_file_system_record(unsigned int event)
{
    open_cfw_test_file_system_events[
        open_cfw_test_file_system_event_count++
    ] = event;
}

void open_cfw_test_file_system_reset(void)
{
    unsigned int first;
    unsigned int second;

    for (first = 0U; first < 128U; ++first) {
        open_cfw_test_file_system_events[first] = 0U;
        open_cfw_test_file_system_levels[first] = 0U;
    }
    for (first = 0U; first < 16U; ++first) {
        open_cfw_test_file_system_directory_open_results[first] = 0;
        open_cfw_test_file_system_directory_paths[first] = 0U;
        open_cfw_test_file_system_directory_objects[first] = 0U;
        open_cfw_test_file_system_mkdir_results[first] = 0;
        open_cfw_test_file_system_mkdir_paths[first] = 0U;
        for (second = 0U; second < 8U; ++second) {
            open_cfw_test_file_system_log_records[first][second] = 0U;
        }
        for (second = 0U; second < 5U; ++second) {
            open_cfw_test_file_system_trace_records[first][second] = 0U;
        }
    }
    for (first = 0U; first < 8U; ++first) {
        open_cfw_test_file_system_mount_results[first] = 0;
    }
    for (first = 0U; first < 6U; ++first) {
        open_cfw_test_file_system_read_log_arguments[first] = 0U;
    }

    open_cfw_test_file_system_event_count = 0U;
    open_cfw_test_file_system_level_count = 0U;
    open_cfw_test_file_system_level_index = 0U;
    open_cfw_test_file_system_log_count = 0U;
    open_cfw_test_file_system_trace_count = 0U;
    open_cfw_test_file_system_directory_open_calls = 0U;
    open_cfw_test_file_system_mkdir_calls = 0U;
    open_cfw_test_file_system_directory_close_calls = 0U;
    open_cfw_test_file_system_unmount_result = 0;
    open_cfw_test_file_system_unmount_calls = 0U;
    open_cfw_test_file_system_format_result = 0;
    open_cfw_test_file_system_format_calls = 0U;
    open_cfw_test_file_system_mount_calls = 0U;
    open_cfw_test_file_system_ready_byte = 0U;
    open_cfw_test_file_system_file_open_calls = 0U;
    open_cfw_test_file_system_file_open_path = 0U;
    open_cfw_test_file_system_file_open_flags = 0U;
    open_cfw_test_file_system_file_read_calls = 0U;
    open_cfw_test_file_system_boot_count_seed = 0;
    open_cfw_test_file_system_file_rewind_calls = 0U;
    open_cfw_test_file_system_file_write_calls = 0U;
    open_cfw_test_file_system_boot_count_written = 0;
    open_cfw_test_file_system_file_close_calls = 0U;
    open_cfw_test_file_system_flash_read_result = 0;
    open_cfw_test_file_system_flash_read_calls = 0U;
    open_cfw_test_file_system_flash_read_address = 0U;
    open_cfw_test_file_system_flash_read_buffer = 0U;
    open_cfw_test_file_system_flash_read_size = 0U;
    open_cfw_test_file_system_flash_program_result = 0;
    open_cfw_test_file_system_flash_program_calls = 0U;
    open_cfw_test_file_system_flash_program_address = 0U;
    open_cfw_test_file_system_flash_program_buffer = 0U;
    open_cfw_test_file_system_flash_program_size = 0U;
    open_cfw_test_file_system_flash_erase_result = 0;
    open_cfw_test_file_system_flash_erase_calls = 0U;
    open_cfw_test_file_system_flash_erase_address = 0U;
    open_cfw_test_file_system_read_log_calls = 0U;
}

unsigned int open_cfw_test_file_system_log_level(void)
{
    unsigned int value = 0U;

    if (
        open_cfw_test_file_system_level_index
        < open_cfw_test_file_system_level_count
    ) {
        value = open_cfw_test_file_system_levels[
            open_cfw_test_file_system_level_index
        ];
    }
    ++open_cfw_test_file_system_level_index;
    open_cfw_test_file_system_record(1U);
    return value;
}

static unsigned int open_cfw_test_file_system_log_argument_count(
    unsigned int line
)
{
    if (line == 0x6FU || line == 0x86U) {
        return 0U;
    }
    if (line == 0x55U || line == 0x5CU) {
        return 2U;
    }
    return 1U;
}

void open_cfw_test_file_system_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    __builtin_va_list arguments;
    __UINTPTR_TYPE__ *record =
        open_cfw_test_file_system_log_records[
            open_cfw_test_file_system_log_count++
        ];
    unsigned int count =
        open_cfw_test_file_system_log_argument_count(line);

    record[0] = level;
    record[1] = (__UINTPTR_TYPE__)module;
    record[2] = (__UINTPTR_TYPE__)file;
    record[3] = (__UINTPTR_TYPE__)function;
    record[4] = line;
    record[5] = (__UINTPTR_TYPE__)message;
    __builtin_va_start(arguments, message);
    if (count != 0U) {
        if (line == 0x6BU || line == 0x7FU || line == 0x9AU) {
            record[6] = (unsigned int)__builtin_va_arg(arguments, int);
        }
        else {
            record[6] = (__UINTPTR_TYPE__)
                __builtin_va_arg(arguments, const void *);
        }
    }
    if (count == 2U) {
        record[7] = (unsigned int)__builtin_va_arg(arguments, int);
    }
    __builtin_va_end(arguments);
    open_cfw_test_file_system_record(2U);
}

void open_cfw_test_file_system_trace(
    unsigned int level,
    const void *format,
    const void *argument,
    ...
)
{
    __builtin_va_list arguments;
    __UINTPTR_TYPE__ *record =
        open_cfw_test_file_system_trace_records[
            open_cfw_test_file_system_trace_count++
        ];
    unsigned int count = 0U;

    record[0] = level;
    record[1] = (__UINTPTR_TYPE__)format;
    record[2] = (__UINTPTR_TYPE__)argument;
    if (
        format != (const void *)0x0072A224U
        && format != (const void *)0x006F3F30U
    ) {
        count = (
            format == (const void *)0x00734B74U
            || format == (const void *)0x00734BA4U
        ) ? 2U : 1U;
    }
    __builtin_va_start(arguments, argument);
    if (count != 0U) {
        if (
            format == (const void *)0x00754F74U
            || format == (const void *)0x00754FBCU
            || format == (const void *)0x0076C1CCU
        ) {
            record[3] = (unsigned int)__builtin_va_arg(arguments, int);
        }
        else {
            record[3] = (__UINTPTR_TYPE__)
                __builtin_va_arg(arguments, const void *);
        }
    }
    if (count == 2U) {
        record[4] = (unsigned int)__builtin_va_arg(arguments, int);
    }
    __builtin_va_end(arguments);
    open_cfw_test_file_system_record(3U);
}

int open_cfw_test_file_system_directory_open(
    void *fs,
    void *directory,
    const char *path
)
{
    unsigned int index =
        open_cfw_test_file_system_directory_open_calls++;

    if (fs != OPEN_CFW_FILE_SYSTEM_CONTEXT) {
        return -99;
    }
    open_cfw_test_file_system_directory_paths[index] =
        (__UINTPTR_TYPE__)path;
    open_cfw_test_file_system_directory_objects[index] =
        (__UINTPTR_TYPE__)directory;
    open_cfw_test_file_system_record(4U);
    return open_cfw_test_file_system_directory_open_results[index];
}

int open_cfw_test_file_system_directory_close(void *fs, void *directory)
{
    (void)fs;
    (void)directory;
    ++open_cfw_test_file_system_directory_close_calls;
    open_cfw_test_file_system_record(6U);
    return 0;
}

int open_cfw_test_file_system_mkdir(void *fs, const char *path)
{
    unsigned int index = open_cfw_test_file_system_mkdir_calls++;

    (void)fs;
    open_cfw_test_file_system_mkdir_paths[index] =
        (__UINTPTR_TYPE__)path;
    open_cfw_test_file_system_record(5U);
    return open_cfw_test_file_system_mkdir_results[index];
}

int open_cfw_test_file_system_unmount(void *fs)
{
    (void)fs;
    ++open_cfw_test_file_system_unmount_calls;
    open_cfw_test_file_system_record(7U);
    return open_cfw_test_file_system_unmount_result;
}

int open_cfw_test_file_system_format(void *fs, const void *config)
{
    (void)fs;
    (void)config;
    ++open_cfw_test_file_system_format_calls;
    open_cfw_test_file_system_record(8U);
    return open_cfw_test_file_system_format_result;
}

int open_cfw_test_file_system_mount(void *fs, const void *config)
{
    unsigned int index = open_cfw_test_file_system_mount_calls++;

    (void)fs;
    (void)config;
    open_cfw_test_file_system_record(9U);
    return open_cfw_test_file_system_mount_results[index];
}

int open_cfw_test_file_system_file_open(
    void *fs,
    void *file,
    const char *path,
    unsigned int flags
)
{
    (void)fs;
    (void)file;
    ++open_cfw_test_file_system_file_open_calls;
    open_cfw_test_file_system_file_open_path =
        (__UINTPTR_TYPE__)path;
    open_cfw_test_file_system_file_open_flags = flags;
    open_cfw_test_file_system_record(10U);
    return 0;
}

int open_cfw_test_file_system_file_read(
    void *fs,
    void *file,
    void *buffer,
    unsigned int size
)
{
    (void)fs;
    (void)file;
    ++open_cfw_test_file_system_file_read_calls;
    if (size == 4U) {
        *(int *)buffer = open_cfw_test_file_system_boot_count_seed;
    }
    open_cfw_test_file_system_record(11U);
    return (int)size;
}

int open_cfw_test_file_system_file_rewind(void *fs, void *file)
{
    (void)fs;
    (void)file;
    ++open_cfw_test_file_system_file_rewind_calls;
    open_cfw_test_file_system_record(12U);
    return 0;
}

int open_cfw_test_file_system_file_write(
    void *fs,
    void *file,
    const void *buffer,
    unsigned int size
)
{
    (void)fs;
    (void)file;
    ++open_cfw_test_file_system_file_write_calls;
    if (size == 4U) {
        open_cfw_test_file_system_boot_count_written =
            *(const int *)buffer;
    }
    open_cfw_test_file_system_record(13U);
    return (int)size;
}

int open_cfw_test_file_system_file_close(void *fs, void *file)
{
    (void)fs;
    (void)file;
    ++open_cfw_test_file_system_file_close_calls;
    open_cfw_test_file_system_record(14U);
    return 0;
}

int open_cfw_test_file_system_flash_read(
    unsigned int address,
    void *buffer,
    unsigned int size
)
{
    ++open_cfw_test_file_system_flash_read_calls;
    open_cfw_test_file_system_flash_read_address = address;
    open_cfw_test_file_system_flash_read_buffer =
        (__UINTPTR_TYPE__)buffer;
    open_cfw_test_file_system_flash_read_size = size;
    open_cfw_test_file_system_record(15U);
    return open_cfw_test_file_system_flash_read_result;
}

int open_cfw_test_file_system_flash_program(
    unsigned int address,
    const void *buffer,
    unsigned int size
)
{
    ++open_cfw_test_file_system_flash_program_calls;
    open_cfw_test_file_system_flash_program_address = address;
    open_cfw_test_file_system_flash_program_buffer =
        (__UINTPTR_TYPE__)buffer;
    open_cfw_test_file_system_flash_program_size = size;
    open_cfw_test_file_system_record(17U);
    return open_cfw_test_file_system_flash_program_result;
}

int open_cfw_test_file_system_flash_erase(unsigned int address)
{
    ++open_cfw_test_file_system_flash_erase_calls;
    open_cfw_test_file_system_flash_erase_address = address;
    open_cfw_test_file_system_record(18U);
    return open_cfw_test_file_system_flash_erase_result;
}

unsigned int open_cfw_test_file_system_read_log(const char *format, ...)
{
    __builtin_va_list arguments;
    unsigned int count =
        format == (const char *)0x00734BD4U ? 3U : 5U;
    unsigned int index;

    ++open_cfw_test_file_system_read_log_calls;
    open_cfw_test_file_system_read_log_arguments[0] =
        (__UINTPTR_TYPE__)format;
    __builtin_va_start(arguments, format);
    for (index = 1U; index <= count; ++index) {
        open_cfw_test_file_system_read_log_arguments[index] =
            (unsigned int)__builtin_va_arg(arguments, int);
    }
    __builtin_va_end(arguments);
    open_cfw_test_file_system_record(16U);
    return 0U;
}

#include "../../components/apollo_main/core_overlay/file_system.c"
