/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader LittleFS initializer. */

typedef __INT32_TYPE__ open_cfw_littlefs_init_i32;
typedef __UINT32_TYPE__ open_cfw_littlefs_init_u32;
typedef __UINT8_TYPE__ open_cfw_littlefs_init_u8;
typedef __UINTPTR_TYPE__ open_cfw_littlefs_init_word;

enum {
    OPEN_CFW_LITTLEFS_INIT_LFS_ADDRESS = 0x20026878U,
    OPEN_CFW_LITTLEFS_INIT_CONFIG_ADDRESS = 0x00431070U,
    OPEN_CFW_LITTLEFS_INIT_READY_ADDRESS = 0x2002711CU,
    OPEN_CFW_LITTLEFS_INIT_FILE_ADDRESS = 0x20026C0CU,
    OPEN_CFW_LITTLEFS_INIT_FORMAT_THUMB = 0x00415129U,
    OPEN_CFW_LITTLEFS_INIT_MOUNT_THUMB = 0x00415133U,
    OPEN_CFW_LITTLEFS_INIT_FILE_OPEN_THUMB = 0x00415147U,
    OPEN_CFW_LITTLEFS_INIT_FILE_READ_THUMB = 0x004151C1U,
    OPEN_CFW_LITTLEFS_INIT_FILE_WRITE_THUMB = 0x004151FDU,
    OPEN_CFW_LITTLEFS_INIT_FILE_CLOSE_THUMB = 0x00415181U,
    OPEN_CFW_LITTLEFS_INIT_FILE_REWIND_THUMB = 0x00415275U,
    OPEN_CFW_LITTLEFS_INIT_OPEN_FLAGS = 0x103U,
    OPEN_CFW_LITTLEFS_INIT_ERROR = 9
};

enum open_cfw_littlefs_init_log_kind {
    OPEN_CFW_LITTLEFS_INIT_LOG_MOUNT_FAILED = 1,
    OPEN_CFW_LITTLEFS_INIT_LOG_DIRECTORIES_FAILED = 2,
    OPEN_CFW_LITTLEFS_INIT_LOG_BOOT_COUNT = 3
};

typedef open_cfw_littlefs_init_i32 (*open_cfw_littlefs_init_config_fn)(
    void *, const void *);
typedef open_cfw_littlefs_init_i32 (*open_cfw_littlefs_init_file_open_fn)(
    void *, void *, const char *, open_cfw_littlefs_init_u32);
typedef open_cfw_littlefs_init_i32 (*open_cfw_littlefs_init_file_io_fn)(
    void *, void *, void *, open_cfw_littlefs_init_u32);
typedef open_cfw_littlefs_init_i32 (*open_cfw_littlefs_init_file_const_io_fn)(
    void *, void *, const void *, open_cfw_littlefs_init_u32);
typedef open_cfw_littlefs_init_i32 (*open_cfw_littlefs_init_file_fn)(
    void *, void *);

open_cfw_littlefs_init_i32
open_cfw_bootloader_check_and_create_directories_4210c8(void);

open_cfw_littlefs_init_i32
open_cfw_littlefs_bootloader_format_4211b0(void);

void open_cfw_bootloader_easylogger_output_4176ce(
    open_cfw_littlefs_init_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...);

#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_mount(void);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_format(void);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_directories(void);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_recovery(void);
void open_cfw_littlefs_init_host_ready(void);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_open(
    open_cfw_littlefs_init_u32);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_read(
    open_cfw_littlefs_init_i32 *, open_cfw_littlefs_init_u32);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_rewind(void);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_write(
    const open_cfw_littlefs_init_i32 *, open_cfw_littlefs_init_u32);
open_cfw_littlefs_init_i32 open_cfw_littlefs_init_host_file_close(void);
void open_cfw_littlefs_init_host_log(
    open_cfw_littlefs_init_i32, open_cfw_littlefs_init_i32);
#endif

static __attribute__((always_inline)) inline void *open_cfw_littlefs_init_lfs(void)
{
    return (void *)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_LFS_ADDRESS;
}

static __attribute__((always_inline)) inline void *open_cfw_littlefs_init_file(void)
{
    return (void *)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_FILE_ADDRESS;
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_mount(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_mount();
#else
    return ((open_cfw_littlefs_init_config_fn)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_MOUNT_THUMB)(
            open_cfw_littlefs_init_lfs(),
            (const void *)(open_cfw_littlefs_init_word)
                OPEN_CFW_LITTLEFS_INIT_CONFIG_ADDRESS);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_format(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_format();
#else
    return ((open_cfw_littlefs_init_config_fn)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_FORMAT_THUMB)(
            open_cfw_littlefs_init_lfs(),
            (const void *)(open_cfw_littlefs_init_word)
                OPEN_CFW_LITTLEFS_INIT_CONFIG_ADDRESS);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_directories(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_directories();
#else
    return open_cfw_bootloader_check_and_create_directories_4210c8();
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_recovery(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_recovery();
#else
    return open_cfw_littlefs_bootloader_format_4211b0();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_littlefs_init_ready(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    open_cfw_littlefs_init_host_ready();
#else
    *(volatile open_cfw_littlefs_init_u32 *)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_READY_ADDRESS = 1U;
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_file_open(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_file_open(
        OPEN_CFW_LITTLEFS_INIT_OPEN_FLAGS);
#else
    return ((open_cfw_littlefs_init_file_open_fn)
        (open_cfw_littlefs_init_word)OPEN_CFW_LITTLEFS_INIT_FILE_OPEN_THUMB)(
            open_cfw_littlefs_init_lfs(), open_cfw_littlefs_init_file(),
            (const char *)(open_cfw_littlefs_init_word)0x00433FC8U,
            OPEN_CFW_LITTLEFS_INIT_OPEN_FLAGS);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_file_read(open_cfw_littlefs_init_i32 *count)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_file_read(count, 4U);
#else
    return ((open_cfw_littlefs_init_file_io_fn)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_FILE_READ_THUMB)(
            open_cfw_littlefs_init_lfs(), open_cfw_littlefs_init_file(),
            count, 4U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_file_rewind(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_file_rewind();
#else
    return ((open_cfw_littlefs_init_file_fn)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_FILE_REWIND_THUMB)(
            open_cfw_littlefs_init_lfs(), open_cfw_littlefs_init_file());
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_file_write(const open_cfw_littlefs_init_i32 *count)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_file_write(count, 4U);
#else
    return ((open_cfw_littlefs_init_file_const_io_fn)
        (open_cfw_littlefs_init_word)OPEN_CFW_LITTLEFS_INIT_FILE_WRITE_THUMB)(
            open_cfw_littlefs_init_lfs(), open_cfw_littlefs_init_file(),
            count, 4U);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_init_i32
open_cfw_littlefs_init_file_close(void)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    return open_cfw_littlefs_init_host_file_close();
#else
    return ((open_cfw_littlefs_init_file_fn)(open_cfw_littlefs_init_word)
        OPEN_CFW_LITTLEFS_INIT_FILE_CLOSE_THUMB)(
            open_cfw_littlefs_init_lfs(), open_cfw_littlefs_init_file());
#endif
}

static __attribute__((always_inline)) inline void open_cfw_littlefs_init_log(
    enum open_cfw_littlefs_init_log_kind kind,
    open_cfw_littlefs_init_i32 value)
{
#if defined(OPEN_CFW_LITTLEFS_INIT_HOST)
    open_cfw_littlefs_init_host_log((open_cfw_littlefs_init_i32)kind, value);
#else
    const char *tag =
        (const char *)(open_cfw_littlefs_init_word)0x00433FBCU;
    const char *file =
        (const char *)(open_cfw_littlefs_init_word)0x00430E60U;
    const char *function =
        (const char *)(open_cfw_littlefs_init_word)0x00433E38U;

    if (kind == OPEN_CFW_LITTLEFS_INIT_LOG_MOUNT_FAILED) {
        open_cfw_bootloader_easylogger_output_4176ce(
            2U, tag, file, function, 0x7FL,
            (const char *)(open_cfw_littlefs_init_word)0x0043397CU, value);
    } else if (kind == OPEN_CFW_LITTLEFS_INIT_LOG_DIRECTORIES_FAILED) {
        open_cfw_bootloader_easylogger_output_4176ce(
            2U, tag, file, function, 0x86L,
            (const char *)(open_cfw_littlefs_init_word)0x0043178CU);
    } else {
        open_cfw_bootloader_easylogger_output_4176ce(
            4U, tag, file, function, 0x9AL,
            (const char *)(open_cfw_littlefs_init_word)0x00433E48U, value);
    }
#endif
}

__attribute__((used, noinline))
open_cfw_littlefs_init_i32 open_cfw_littlefs_bootloader_init_421210(void)
{
    open_cfw_littlefs_init_i32 boot_count = 0;
    open_cfw_littlefs_init_i32 status = open_cfw_littlefs_init_mount();

    if (status != 0) {
        (void)open_cfw_littlefs_init_format();
        status = open_cfw_littlefs_init_mount();
        if (status != 0) {
            open_cfw_littlefs_init_log(
                OPEN_CFW_LITTLEFS_INIT_LOG_MOUNT_FAILED, status);
            return OPEN_CFW_LITTLEFS_INIT_ERROR;
        }
    }

    if (open_cfw_littlefs_init_directories() != 0) {
        open_cfw_littlefs_init_log(
            OPEN_CFW_LITTLEFS_INIT_LOG_DIRECTORIES_FAILED, 0);
        (void)open_cfw_littlefs_init_recovery();
    }

    open_cfw_littlefs_init_ready();
    (void)open_cfw_littlefs_init_file_open();
    (void)open_cfw_littlefs_init_file_read(&boot_count);
    ++boot_count;
    (void)open_cfw_littlefs_init_file_rewind();
    (void)open_cfw_littlefs_init_file_write(&boot_count);
    (void)open_cfw_littlefs_init_file_close();
    open_cfw_littlefs_init_log(
        OPEN_CFW_LITTLEFS_INIT_LOG_BOOT_COUNT, boot_count);
    return 0;
}
