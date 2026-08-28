/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 LittleFS format/bootstrap service. */

typedef __INT32_TYPE__ open_cfw_littlefs_format_i32;
typedef __UINT8_TYPE__ open_cfw_littlefs_format_u8;
typedef __UINTPTR_TYPE__ open_cfw_littlefs_format_word;

enum {
    OPEN_CFW_LITTLEFS_FORMAT_LFS_ADDRESS = 0x20026878U,
    OPEN_CFW_LITTLEFS_FORMAT_CONFIG_ADDRESS = 0x00431070U,
    OPEN_CFW_LITTLEFS_FORMAT_UNMOUNT_THUMB = 0x0041513DU,
    OPEN_CFW_LITTLEFS_FORMAT_FORMAT_THUMB = 0x00415129U,
    OPEN_CFW_LITTLEFS_FORMAT_MOUNT_THUMB = 0x00415133U,
    OPEN_CFW_LITTLEFS_FORMAT_ERROR = 9
};

enum open_cfw_littlefs_format_log_kind {
    OPEN_CFW_LITTLEFS_FORMAT_LOG_MOUNT_FAILED = 1,
    OPEN_CFW_LITTLEFS_FORMAT_LOG_DIRECTORIES_FAILED = 2
};

typedef open_cfw_littlefs_format_i32 (*open_cfw_littlefs_format_unmount_fn)(
    void *);
typedef open_cfw_littlefs_format_i32 (*open_cfw_littlefs_format_config_fn)(
    void *, const void *);

open_cfw_littlefs_format_i32
open_cfw_bootloader_check_and_create_directories_4210c8(void);

void open_cfw_bootloader_easylogger_output_4176ce(
    open_cfw_littlefs_format_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...);

#if defined(OPEN_CFW_LITTLEFS_FORMAT_HOST)
open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_unmount(void);
open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_format(void);
open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_mount(void);
open_cfw_littlefs_format_i32 open_cfw_littlefs_format_host_directories(void);
void open_cfw_littlefs_format_host_log(
    open_cfw_littlefs_format_i32, open_cfw_littlefs_format_i32);
#endif

static __attribute__((always_inline)) inline open_cfw_littlefs_format_i32
open_cfw_littlefs_format_unmount(void)
{
#if defined(OPEN_CFW_LITTLEFS_FORMAT_HOST)
    return open_cfw_littlefs_format_host_unmount();
#else
    return ((open_cfw_littlefs_format_unmount_fn)
        (open_cfw_littlefs_format_word)
            OPEN_CFW_LITTLEFS_FORMAT_UNMOUNT_THUMB)(
                (void *)(open_cfw_littlefs_format_word)
                    OPEN_CFW_LITTLEFS_FORMAT_LFS_ADDRESS);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_format_i32
open_cfw_littlefs_format_format(void)
{
#if defined(OPEN_CFW_LITTLEFS_FORMAT_HOST)
    return open_cfw_littlefs_format_host_format();
#else
    return ((open_cfw_littlefs_format_config_fn)
        (open_cfw_littlefs_format_word)OPEN_CFW_LITTLEFS_FORMAT_FORMAT_THUMB)(
            (void *)(open_cfw_littlefs_format_word)
                OPEN_CFW_LITTLEFS_FORMAT_LFS_ADDRESS,
            (const void *)(open_cfw_littlefs_format_word)
                OPEN_CFW_LITTLEFS_FORMAT_CONFIG_ADDRESS);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_format_i32
open_cfw_littlefs_format_mount(void)
{
#if defined(OPEN_CFW_LITTLEFS_FORMAT_HOST)
    return open_cfw_littlefs_format_host_mount();
#else
    return ((open_cfw_littlefs_format_config_fn)
        (open_cfw_littlefs_format_word)OPEN_CFW_LITTLEFS_FORMAT_MOUNT_THUMB)(
            (void *)(open_cfw_littlefs_format_word)
                OPEN_CFW_LITTLEFS_FORMAT_LFS_ADDRESS,
            (const void *)(open_cfw_littlefs_format_word)
                OPEN_CFW_LITTLEFS_FORMAT_CONFIG_ADDRESS);
#endif
}

static __attribute__((always_inline)) inline open_cfw_littlefs_format_i32
open_cfw_littlefs_format_directories(void)
{
#if defined(OPEN_CFW_LITTLEFS_FORMAT_HOST)
    return open_cfw_littlefs_format_host_directories();
#else
    return open_cfw_bootloader_check_and_create_directories_4210c8();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_littlefs_format_log(
    enum open_cfw_littlefs_format_log_kind kind,
    open_cfw_littlefs_format_i32 status)
{
#if defined(OPEN_CFW_LITTLEFS_FORMAT_HOST)
    open_cfw_littlefs_format_host_log((open_cfw_littlefs_format_i32)kind,
        status);
#else
    const char *tag =
        (const char *)(open_cfw_littlefs_format_word)0x00433FBCU;
    const char *file =
        (const char *)(open_cfw_littlefs_format_word)0x00430E60U;
    const char *function =
        (const char *)(open_cfw_littlefs_format_word)0x00433E28U;

    if (kind == OPEN_CFW_LITTLEFS_FORMAT_LOG_MOUNT_FAILED) {
        open_cfw_bootloader_easylogger_output_4176ce(
            2U, tag, file, function, 0x6BL,
            (const char *)(open_cfw_littlefs_format_word)0x00433964U,
            status);
    } else {
        open_cfw_bootloader_easylogger_output_4176ce(
            2U, tag, file, function, 0x6FL,
            (const char *)(open_cfw_littlefs_format_word)0x00433000U);
    }
#endif
}

__attribute__((used, noinline))
open_cfw_littlefs_format_i32
open_cfw_littlefs_bootloader_format_4211b0(void)
{
    open_cfw_littlefs_format_i32 status;

    (void)open_cfw_littlefs_format_unmount();
    (void)open_cfw_littlefs_format_format();

    status = open_cfw_littlefs_format_mount();
    if (status != 0) {
        open_cfw_littlefs_format_log(
            OPEN_CFW_LITTLEFS_FORMAT_LOG_MOUNT_FAILED, status);
        return OPEN_CFW_LITTLEFS_FORMAT_ERROR;
    }

    status = open_cfw_littlefs_format_directories();
    if (status != 0) {
        open_cfw_littlefs_format_log(
            OPEN_CFW_LITTLEFS_FORMAT_LOG_DIRECTORIES_FAILED, status);
        return OPEN_CFW_LITTLEFS_FORMAT_ERROR;
    }

    return 0;
}
