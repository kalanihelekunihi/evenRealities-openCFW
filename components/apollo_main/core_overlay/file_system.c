/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded littlefs directory-check, format, initialization, and read-callback
 * reimplementation matched to stock entries 0x00475FE8 through 0x004763EF.
 */

typedef __UINTPTR_TYPE__ open_cfw_file_system_uintptr;

typedef unsigned int (*open_cfw_file_system_log_level_function)(void);
typedef void (*open_cfw_file_system_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_file_system_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_FILE_SYSTEM_CONTEXT
#define OPEN_CFW_FILE_SYSTEM_CONTEXT ((void *)0x20071AC8U)
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_CONFIG
#define OPEN_CFW_FILE_SYSTEM_CONFIG ((const void *)0x006E83A4U)
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_READY_BYTE
#define OPEN_CFW_FILE_SYSTEM_READY_BYTE \
    (*(volatile unsigned char *)0x200746A8U)
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_BOOT_FILE
#define OPEN_CFW_FILE_SYSTEM_BOOT_FILE ((void *)0x200728A0U)
#endif

#ifndef OPEN_CFW_FILE_SYSTEM_LOG_LEVEL
#define OPEN_CFW_FILE_SYSTEM_LOG_LEVEL() \
    (((open_cfw_file_system_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_LOG
#define OPEN_CFW_FILE_SYSTEM_LOG(...) \
    (((open_cfw_file_system_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_TRACE
#define OPEN_CFW_FILE_SYSTEM_TRACE(...) \
    (((open_cfw_file_system_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif

typedef int (*open_cfw_file_system_directory_open_function)(
    void *,
    void *,
    const char *
);
typedef int (*open_cfw_file_system_directory_close_function)(
    void *,
    void *
);
typedef int (*open_cfw_file_system_mkdir_function)(void *, const char *);
typedef int (*open_cfw_file_system_one_argument_function)(void *);
typedef int (*open_cfw_file_system_two_argument_function)(
    void *,
    const void *
);
typedef int (*open_cfw_file_system_file_open_function)(
    void *,
    void *,
    const char *,
    unsigned int
);
typedef int (*open_cfw_file_system_file_transfer_function)(
    void *,
    void *,
    void *,
    unsigned int
);
typedef int (*open_cfw_file_system_file_write_function)(
    void *,
    void *,
    const void *,
    unsigned int
);
typedef int (*open_cfw_file_system_file_action_function)(void *, void *);
typedef int (*open_cfw_file_system_flash_read_function)(
    unsigned int,
    void *,
    unsigned int
);
typedef int (*open_cfw_file_system_flash_program_function)(
    unsigned int,
    const void *,
    unsigned int
);
typedef int (*open_cfw_file_system_flash_erase_function)(unsigned int);

#ifndef OPEN_CFW_FILE_SYSTEM_DIRECTORY_OPEN
#define OPEN_CFW_FILE_SYSTEM_DIRECTORY_OPEN(fs, directory, path) \
    (((open_cfw_file_system_directory_open_function)0x004CFC67U)( \
        (fs), (directory), (path) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_DIRECTORY_CLOSE
#define OPEN_CFW_FILE_SYSTEM_DIRECTORY_CLOSE(fs, directory) \
    (((open_cfw_file_system_directory_close_function)0x004CFCF9U)( \
        (fs), (directory) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_MKDIR
#define OPEN_CFW_FILE_SYSTEM_MKDIR(fs, path) \
    (((open_cfw_file_system_mkdir_function)0x004CFC5DU)((fs), (path)))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_UNMOUNT
#define OPEN_CFW_FILE_SYSTEM_UNMOUNT(fs) \
    (((open_cfw_file_system_one_argument_function)0x004CFA6DU)((fs)))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FORMAT
#define OPEN_CFW_FILE_SYSTEM_FORMAT(fs, config) \
    (((open_cfw_file_system_two_argument_function)0x004CFA59U)( \
        (fs), (config) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_MOUNT
#define OPEN_CFW_FILE_SYSTEM_MOUNT(fs, config) \
    (((open_cfw_file_system_two_argument_function)0x004CFA63U)( \
        (fs), (config) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FILE_OPEN
#define OPEN_CFW_FILE_SYSTEM_FILE_OPEN(fs, file, path, flags) \
    (((open_cfw_file_system_file_open_function)0x004CFA95U)( \
        (fs), (file), (path), (flags) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FILE_READ
#define OPEN_CFW_FILE_SYSTEM_FILE_READ(fs, file, buffer, size) \
    (((open_cfw_file_system_file_transfer_function)0x004CFB41U)( \
        (fs), (file), (buffer), (size) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FILE_REWIND
#define OPEN_CFW_FILE_SYSTEM_FILE_REWIND(fs, file) \
    (((open_cfw_file_system_file_action_function)0x004CFC25U)( \
        (fs), (file) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FILE_WRITE
#define OPEN_CFW_FILE_SYSTEM_FILE_WRITE(fs, file, buffer, size) \
    (((open_cfw_file_system_file_write_function)0x004CFB7DU)( \
        (fs), (file), (buffer), (size) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FILE_CLOSE
#define OPEN_CFW_FILE_SYSTEM_FILE_CLOSE(fs, file) \
    (((open_cfw_file_system_file_action_function)0x004CFAD1U)( \
        (fs), (file) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FLASH_READ
#define OPEN_CFW_FILE_SYSTEM_FLASH_READ(address, buffer, size) \
    (((open_cfw_file_system_flash_read_function)0x00471021U)( \
        (address), (buffer), (size) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FLASH_PROGRAM
#define OPEN_CFW_FILE_SYSTEM_FLASH_PROGRAM(address, buffer, size) \
    (((open_cfw_file_system_flash_program_function)0x004708A9U)( \
        (address), (buffer), (size) \
    ))
#endif
#ifndef OPEN_CFW_FILE_SYSTEM_FLASH_ERASE
#define OPEN_CFW_FILE_SYSTEM_FLASH_ERASE(address) \
    (((open_cfw_file_system_flash_erase_function)0x0047075DU)( \
        (address) \
    ))
#endif

#ifndef OPEN_CFW_FILE_SYSTEM_READ_LOG
unsigned int open_cfw_log_format_dispatch(const char *format, ...);
#define OPEN_CFW_FILE_SYSTEM_READ_LOG(...) \
    open_cfw_log_format_dispatch(__VA_ARGS__)
#endif

static __attribute__((always_inline)) inline int
open_cfw_file_system_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_FILE_SYSTEM_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_FILE_SYSTEM_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline const char *
open_cfw_file_system_path(unsigned int index)
{
    switch (index) {
        case 0U:
            return "/firmware";
        case 1U:
            return "/ota";
        case 2U:
            return "/user";
        default:
            return "/log";
    }
}

static __attribute__((always_inline)) inline void
open_cfw_file_system_path_diagnostic(
    unsigned int structured_level,
    unsigned int line,
    const void *function,
    const void *message,
    unsigned int trace_level,
    const void *trace,
    const char *path,
    int result,
    unsigned int argument_count
)
{
    if ((OPEN_CFW_FILE_SYSTEM_LOG_LEVEL() & 2U) != 0U) {
        if (argument_count == 0U) {
            OPEN_CFW_FILE_SYSTEM_LOG(
                structured_level,
                (const void *)
                    (open_cfw_file_system_uintptr)0x0078ABC8U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x006DD654U,
                function,
                line,
                message
            );
        }
        else if (argument_count == 1U) {
            OPEN_CFW_FILE_SYSTEM_LOG(
                structured_level,
                (const void *)
                    (open_cfw_file_system_uintptr)0x0078ABC8U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x006DD654U,
                function,
                line,
                message,
                path
            );
        }
        else if (argument_count == 2U) {
            OPEN_CFW_FILE_SYSTEM_LOG(
                structured_level,
                (const void *)
                    (open_cfw_file_system_uintptr)0x0078ABC8U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x006DD654U,
                function,
                line,
                message,
                path,
                result
            );
        }
        else {
            OPEN_CFW_FILE_SYSTEM_LOG(
                structured_level,
                (const void *)
                    (open_cfw_file_system_uintptr)0x0078ABC8U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x006DD654U,
                function,
                line,
                message,
                result
            );
        }
    }

    if (open_cfw_file_system_trace_enabled() != 0) {
        if (argument_count == 0U) {
            OPEN_CFW_FILE_SYSTEM_TRACE(trace_level, trace, trace);
        }
        else if (argument_count == 1U) {
            OPEN_CFW_FILE_SYSTEM_TRACE(
                trace_level,
                trace,
                trace,
                path
            );
        }
        else if (argument_count == 2U) {
            OPEN_CFW_FILE_SYSTEM_TRACE(
                trace_level,
                trace,
                trace,
                path,
                result
            );
        }
        else {
            OPEN_CFW_FILE_SYSTEM_TRACE(
                trace_level,
                trace,
                trace,
                result
            );
        }
    }
}

__attribute__((used, noinline))
int open_cfw_file_system_check_directories(void)
{
    unsigned char directory[52];
    unsigned int index;
    int result;

    for (index = 0U; index < 4U; ++index) {
        const char *path = open_cfw_file_system_path(index);

        result = OPEN_CFW_FILE_SYSTEM_DIRECTORY_OPEN(
            OPEN_CFW_FILE_SYSTEM_CONTEXT,
            directory,
            path
        );
        if (result == -2) {
            result = OPEN_CFW_FILE_SYSTEM_MKDIR(
                OPEN_CFW_FILE_SYSTEM_CONTEXT,
                path
            );
            if (result == 0) {
                open_cfw_file_system_path_diagnostic(
                    4U,
                    0x51U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00760530U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00777CFCU,
                    0x10400000U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00754F08U,
                    path,
                    0,
                    1U
                );
            }
            else if (result == -17) {
                open_cfw_file_system_path_diagnostic(
                    4U,
                    0x53U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00760530U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00760550U,
                    0x10400000U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x0073F294U,
                    path,
                    0,
                    1U
                );
            }
            else {
                open_cfw_file_system_path_diagnostic(
                    2U,
                    0x55U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00760530U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00754F2CU,
                    0x08800000U,
                    (const void *)
                        (open_cfw_file_system_uintptr)0x00734B74U,
                    path,
                    result,
                    2U
                );
            }
        }
        else if (result == 0) {
            (void)OPEN_CFW_FILE_SYSTEM_DIRECTORY_CLOSE(
                OPEN_CFW_FILE_SYSTEM_CONTEXT,
                directory
            );
            open_cfw_file_system_path_diagnostic(
                4U,
                0x5AU,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00760530U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00777D14U,
                0x10400000U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00754F50U,
                path,
                0,
                1U
            );
        }
        else {
            open_cfw_file_system_path_diagnostic(
                2U,
                0x5CU,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00760530U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00760570U,
                0x08800000U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00734BA4U,
                path,
                result,
                2U
            );
            return -1;
        }
    }

    return 0;
}

__attribute__((used, noinline))
int open_cfw_file_system_format(void)
{
    int result;

    (void)OPEN_CFW_FILE_SYSTEM_UNMOUNT(
        OPEN_CFW_FILE_SYSTEM_CONTEXT
    );
    (void)OPEN_CFW_FILE_SYSTEM_FORMAT(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_CONFIG
    );
    result = OPEN_CFW_FILE_SYSTEM_MOUNT(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_CONFIG
    );
    if (result != 0) {
        open_cfw_file_system_path_diagnostic(
            2U,
            0x6BU,
            (const void *)
                (open_cfw_file_system_uintptr)0x007861D0U,
            (const void *)
                (open_cfw_file_system_uintptr)0x00777D2CU,
            0x08400000U,
            (const void *)
                (open_cfw_file_system_uintptr)0x00754F74U,
            (const char *)0,
            result,
            3U
        );
        return 9;
    }

    if (open_cfw_file_system_check_directories() != 0) {
        open_cfw_file_system_path_diagnostic(
            2U,
            0x6FU,
            (const void *)
                (open_cfw_file_system_uintptr)0x007861D0U,
            (const void *)
                (open_cfw_file_system_uintptr)0x00754F98U,
            0x08000000U,
            (const void *)
                (open_cfw_file_system_uintptr)0x0072A224U,
            (const char *)0,
            0,
            0U
        );
        return 9;
    }

    return 0;
}

__attribute__((used, noinline))
int open_cfw_file_system_initialize(void)
{
    int boot_count = 0;
    int result;

    result = OPEN_CFW_FILE_SYSTEM_MOUNT(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_CONFIG
    );
    if (result != 0) {
        (void)OPEN_CFW_FILE_SYSTEM_FORMAT(
            OPEN_CFW_FILE_SYSTEM_CONTEXT,
            OPEN_CFW_FILE_SYSTEM_CONFIG
        );
        result = OPEN_CFW_FILE_SYSTEM_MOUNT(
            OPEN_CFW_FILE_SYSTEM_CONTEXT,
            OPEN_CFW_FILE_SYSTEM_CONFIG
        );
        if (result != 0) {
            open_cfw_file_system_path_diagnostic(
                2U,
                0x7FU,
                (const void *)
                    (open_cfw_file_system_uintptr)0x007861E0U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00777D44U,
                0x08400000U,
                (const void *)
                    (open_cfw_file_system_uintptr)0x00754FBCU,
                (const char *)0,
                result,
                3U
            );
            return 9;
        }
    }

    if (open_cfw_file_system_check_directories() != 0) {
        open_cfw_file_system_path_diagnostic(
            2U,
            0x86U,
            (const void *)
                (open_cfw_file_system_uintptr)0x007861E0U,
            (const void *)
                (open_cfw_file_system_uintptr)0x0070C3E4U,
            0x08000000U,
            (const void *)
                (open_cfw_file_system_uintptr)0x006F3F30U,
            (const char *)0,
            0,
            0U
        );
        (void)open_cfw_file_system_format();
    }

    OPEN_CFW_FILE_SYSTEM_READY_BYTE = 1U;
    (void)OPEN_CFW_FILE_SYSTEM_FILE_OPEN(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_BOOT_FILE,
        "boot_count",
        0x103U
    );
    (void)OPEN_CFW_FILE_SYSTEM_FILE_READ(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_BOOT_FILE,
        &boot_count,
        4U
    );
    ++boot_count;
    (void)OPEN_CFW_FILE_SYSTEM_FILE_REWIND(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_BOOT_FILE
    );
    (void)OPEN_CFW_FILE_SYSTEM_FILE_WRITE(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_BOOT_FILE,
        &boot_count,
        4U
    );
    (void)OPEN_CFW_FILE_SYSTEM_FILE_CLOSE(
        OPEN_CFW_FILE_SYSTEM_CONTEXT,
        OPEN_CFW_FILE_SYSTEM_BOOT_FILE
    );
    open_cfw_file_system_path_diagnostic(
        4U,
        0x9AU,
        (const void *)
            (open_cfw_file_system_uintptr)0x007861E0U,
        (const void *)
            (open_cfw_file_system_uintptr)0x007861F0U,
        0x10400000U,
        (const void *)
            (open_cfw_file_system_uintptr)0x0076C1CCU,
        (const char *)0,
        boot_count,
        3U
    );
    return 0;
}

__attribute__((used, noinline))
int open_cfw_file_system_read(
    const void *configuration,
    unsigned int block,
    unsigned int offset,
    void *buffer,
    unsigned int size
)
{
    unsigned int address =
        0x01400000U + block * 0x1000U + offset;
    int result;

    (void)configuration;
    result = OPEN_CFW_FILE_SYSTEM_FLASH_READ(address, buffer, size);
    if (result == 0) {
        return 0;
    }

    OPEN_CFW_FILE_SYSTEM_READ_LOG(
        (const char *)(open_cfw_file_system_uintptr)0x0070C424U,
        block,
        offset,
        size,
        address,
        result
    );
    return -5;
}

__attribute__((used, noinline))
int open_cfw_file_system_program(
    const void *configuration,
    unsigned int block,
    unsigned int offset,
    const void *buffer,
    unsigned int size
)
{
    unsigned int address =
        0x01400000U + block * 0x1000U + offset;
    int result;

    (void)configuration;
    result = OPEN_CFW_FILE_SYSTEM_FLASH_PROGRAM(
        address,
        buffer,
        size
    );
    if (result == 0) {
        return 0;
    }

    OPEN_CFW_FILE_SYSTEM_READ_LOG(
        (const char *)(open_cfw_file_system_uintptr)0x0070C464U,
        block,
        offset,
        size,
        address,
        result
    );
    return -5;
}

__attribute__((used, noinline))
int open_cfw_file_system_erase(
    const void *configuration,
    unsigned int block
)
{
    unsigned int address = 0x01400000U + block * 0x1000U;
    int result;

    (void)configuration;
    result = OPEN_CFW_FILE_SYSTEM_FLASH_ERASE(address);
    if (result == 0) {
        return 0;
    }

    OPEN_CFW_FILE_SYSTEM_READ_LOG(
        (const char *)(open_cfw_file_system_uintptr)0x00734BD4U,
        block,
        address,
        result
    );
    return -5;
}

__attribute__((used, noinline))
int open_cfw_file_system_sync(const void *configuration)
{
    (void)configuration;
    return 0;
}
