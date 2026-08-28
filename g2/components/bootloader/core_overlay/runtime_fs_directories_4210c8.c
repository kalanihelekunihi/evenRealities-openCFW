/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 LittleFS directory bootstrap service. */

typedef __INT32_TYPE__ open_cfw_fs_directories_i32;
typedef __UINT8_TYPE__ open_cfw_fs_directories_u8;
typedef __UINT32_TYPE__ open_cfw_fs_directories_u32;
typedef __UINTPTR_TYPE__ open_cfw_fs_directories_word;

enum {
    OPEN_CFW_FS_DIRECTORIES_COUNT = 4U,
    OPEN_CFW_FS_DIRECTORIES_LFS_ADDRESS = 0x20026878U,
    OPEN_CFW_FS_DIRECTORIES_PATHS_ADDRESS = 0x00433E58U,
    OPEN_CFW_FS_DIRECTORIES_DIR_OPEN_THUMB = 0x00415289U,
    OPEN_CFW_FS_DIRECTORIES_MKDIR_THUMB = 0x0041527FU,
    OPEN_CFW_FS_DIRECTORIES_DIR_CLOSE_THUMB = 0x0041531DU,
    OPEN_CFW_FS_DIRECTORIES_NO_ENTRY = -2,
    OPEN_CFW_FS_DIRECTORIES_EXISTS = -17,
    OPEN_CFW_FS_DIRECTORIES_FATAL = -1
};

enum open_cfw_fs_directories_log_kind {
    OPEN_CFW_FS_DIRECTORIES_LOG_CREATED = 1,
    OPEN_CFW_FS_DIRECTORIES_LOG_PRESENT = 2,
    OPEN_CFW_FS_DIRECTORIES_LOG_ALREADY_EXISTS = 3,
    OPEN_CFW_FS_DIRECTORIES_LOG_CREATE_FAILED = 4,
    OPEN_CFW_FS_DIRECTORIES_LOG_CHECK_FAILED = 5
};

/* The authenticated caller reserves 52 bytes for the LittleFS dir handle. */
typedef struct {
    open_cfw_fs_directories_u32 words[13];
} open_cfw_fs_directories_dir;

_Static_assert(sizeof(open_cfw_fs_directories_dir) == 52U,
    "G2 LittleFS directory handle ABI changed");

typedef open_cfw_fs_directories_i32 (*open_cfw_fs_directories_open_fn)(
    void *, open_cfw_fs_directories_dir *, const char *);
typedef open_cfw_fs_directories_i32 (*open_cfw_fs_directories_mkdir_fn)(
    void *, const char *);
typedef open_cfw_fs_directories_i32 (*open_cfw_fs_directories_close_fn)(
    void *, open_cfw_fs_directories_dir *);

void open_cfw_bootloader_easylogger_output_4176ce(
    open_cfw_fs_directories_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...);

#if defined(OPEN_CFW_FS_DIRECTORIES_HOST)
const char *open_cfw_fs_directories_host_path(open_cfw_fs_directories_u32);
open_cfw_fs_directories_i32 open_cfw_fs_directories_host_open(
    open_cfw_fs_directories_dir *, const char *);
open_cfw_fs_directories_i32 open_cfw_fs_directories_host_mkdir(const char *);
open_cfw_fs_directories_i32 open_cfw_fs_directories_host_close(
    open_cfw_fs_directories_dir *);
void open_cfw_fs_directories_host_log(
    open_cfw_fs_directories_u32, const char *, open_cfw_fs_directories_i32);
#endif

static __attribute__((always_inline)) inline const char *
open_cfw_fs_directories_path(open_cfw_fs_directories_u32 index)
{
#if defined(OPEN_CFW_FS_DIRECTORIES_HOST)
    return open_cfw_fs_directories_host_path(index);
#else
    const volatile open_cfw_fs_directories_u32 *paths =
        (const volatile open_cfw_fs_directories_u32 *)
            (open_cfw_fs_directories_word)
                OPEN_CFW_FS_DIRECTORIES_PATHS_ADDRESS;
    return (const char *)(open_cfw_fs_directories_word)paths[index];
#endif
}

static __attribute__((always_inline)) inline open_cfw_fs_directories_i32
open_cfw_fs_directories_open(
    open_cfw_fs_directories_dir *directory, const char *path)
{
#if defined(OPEN_CFW_FS_DIRECTORIES_HOST)
    return open_cfw_fs_directories_host_open(directory, path);
#else
    return ((open_cfw_fs_directories_open_fn)(open_cfw_fs_directories_word)
        OPEN_CFW_FS_DIRECTORIES_DIR_OPEN_THUMB)(
            (void *)(open_cfw_fs_directories_word)
                OPEN_CFW_FS_DIRECTORIES_LFS_ADDRESS,
            directory, path);
#endif
}

static __attribute__((always_inline)) inline open_cfw_fs_directories_i32
open_cfw_fs_directories_mkdir(const char *path)
{
#if defined(OPEN_CFW_FS_DIRECTORIES_HOST)
    return open_cfw_fs_directories_host_mkdir(path);
#else
    return ((open_cfw_fs_directories_mkdir_fn)(open_cfw_fs_directories_word)
        OPEN_CFW_FS_DIRECTORIES_MKDIR_THUMB)(
            (void *)(open_cfw_fs_directories_word)
                OPEN_CFW_FS_DIRECTORIES_LFS_ADDRESS,
            path);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_fs_directories_close(
    open_cfw_fs_directories_dir *directory)
{
#if defined(OPEN_CFW_FS_DIRECTORIES_HOST)
    (void)open_cfw_fs_directories_host_close(directory);
#else
    (void)((open_cfw_fs_directories_close_fn)(open_cfw_fs_directories_word)
        OPEN_CFW_FS_DIRECTORIES_DIR_CLOSE_THUMB)(
            (void *)(open_cfw_fs_directories_word)
                OPEN_CFW_FS_DIRECTORIES_LFS_ADDRESS,
            directory);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_fs_directories_log(
    open_cfw_fs_directories_u32 kind,
    const char *path,
    open_cfw_fs_directories_i32 status)
{
#if defined(OPEN_CFW_FS_DIRECTORIES_HOST)
    open_cfw_fs_directories_host_log(kind, path, status);
#else
    const char *tag = (const char *)(open_cfw_fs_directories_word)0x00433FBCU;
    const char *file = (const char *)(open_cfw_fs_directories_word)0x00430E60U;
    const char *function =
        (const char *)(open_cfw_fs_directories_word)0x00433300U;

    switch (kind) {
    case OPEN_CFW_FS_DIRECTORIES_LOG_CREATED:
        open_cfw_bootloader_easylogger_output_4176ce(
            4U, tag, file, function, 0x51L,
            (const char *)(open_cfw_fs_directories_word)0x00433934U, path);
        break;
    case OPEN_CFW_FS_DIRECTORIES_LOG_PRESENT:
        open_cfw_bootloader_easylogger_output_4176ce(
            4U, tag, file, function, 0x5AL,
            (const char *)(open_cfw_fs_directories_word)0x0043394CU, path);
        break;
    case OPEN_CFW_FS_DIRECTORIES_LOG_ALREADY_EXISTS:
        open_cfw_bootloader_easylogger_output_4176ce(
            4U, tag, file, function, 0x53L,
            (const char *)(open_cfw_fs_directories_word)0x00433320U, path);
        break;
    case OPEN_CFW_FS_DIRECTORIES_LOG_CREATE_FAILED:
        open_cfw_bootloader_easylogger_output_4176ce(
            2U, tag, file, function, 0x55L,
            (const char *)(open_cfw_fs_directories_word)0x00432FDCU,
            path, status);
        break;
    default:
        open_cfw_bootloader_easylogger_output_4176ce(
            2U, tag, file, function, 0x5CL,
            (const char *)(open_cfw_fs_directories_word)0x00433340U,
            path, status);
        break;
    }
#endif
}

__attribute__((used, noinline))
open_cfw_fs_directories_i32
open_cfw_bootloader_check_and_create_directories_4210c8(void)
{
    open_cfw_fs_directories_dir directory;
    open_cfw_fs_directories_u32 index;

    for (index = 0U; index < OPEN_CFW_FS_DIRECTORIES_COUNT; ++index) {
        const char *path = open_cfw_fs_directories_path(index);
        open_cfw_fs_directories_i32 status =
            open_cfw_fs_directories_open(&directory, path);

        if (status == OPEN_CFW_FS_DIRECTORIES_NO_ENTRY) {
            status = open_cfw_fs_directories_mkdir(path);
            if (status == 0) {
                open_cfw_fs_directories_log(
                    OPEN_CFW_FS_DIRECTORIES_LOG_CREATED, path, status);
            } else if (status == OPEN_CFW_FS_DIRECTORIES_EXISTS) {
                open_cfw_fs_directories_log(
                    OPEN_CFW_FS_DIRECTORIES_LOG_ALREADY_EXISTS, path, status);
            } else {
                open_cfw_fs_directories_log(
                    OPEN_CFW_FS_DIRECTORIES_LOG_CREATE_FAILED, path, status);
            }
            continue;
        }

        if (status == 0) {
            open_cfw_fs_directories_close(&directory);
            open_cfw_fs_directories_log(
                OPEN_CFW_FS_DIRECTORIES_LOG_PRESENT, path, status);
            continue;
        }

        open_cfw_fs_directories_log(
            OPEN_CFW_FS_DIRECTORIES_LOG_CHECK_FAILED, path, status);
        return OPEN_CFW_FS_DIRECTORIES_FATAL;
    }

    return 0;
}
