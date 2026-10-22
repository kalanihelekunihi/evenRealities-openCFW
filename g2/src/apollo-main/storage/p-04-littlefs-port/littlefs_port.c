/* LittleFS port for the MX25U25643G external NOR, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\littlefs\port\littlefs_mx25u25643g_porting.c.
 * Native 0x475fe8..0x476453 plus the sync stub at 0x4764dc; literal pool
 * 0x476454..0x4764db. lfs_config lives in ROM at 0x6e83a4.
 *
 * The filesystem occupies NOR 0x01400000.., 3008 blocks of 4 KiB (block n is at
 * 0x01400000 + n * 0x1000). The block callbacks report failures through the
 * plain printf-style transport (0x4733ee) and return LFS_ERR_IO. The prog,
 * erase and sync callbacks are not rows of g2/symbols/apollo_main.tsv. */
#include <stdint.h>
#include <stddef.h>

enum {
    LFS_ERR_OK = 0,
    LFS_ERR_IO = -5,
    LFS_ERR_NOENT = -2,
    LFS_ERR_EXIST = -17,
};
#define LFS_O_RDWR 0x3u
#define LFS_O_CREAT 0x100u
#define LITTLEFS_NOR_BASE 0x01400000u
#define LITTLEFS_BLOCK_SHIFT 12u
#define LITTLEFS_RESULT_FAILED 9 /* returned by littlefs_format/littlefs_init */

/* struct lfs_config of the pinned littlefs v2.10.1 (no LFS_THREADSAFE). */
typedef struct g2_lfs_config {
    void *context;                                                     /* +0x00 */
    int (*read)(const struct g2_lfs_config *, uint32_t, uint32_t, void *, uint32_t);  /* +0x04 */
    int (*prog)(const struct g2_lfs_config *, uint32_t, uint32_t, const void *, uint32_t); /* +0x08 */
    int (*erase)(const struct g2_lfs_config *, uint32_t);              /* +0x0c */
    int (*sync)(const struct g2_lfs_config *);                         /* +0x10 */
    uint32_t read_size;                                                /* +0x14 */
    uint32_t prog_size;                                                /* +0x18 */
    uint32_t block_size;                                               /* +0x1c */
    uint32_t block_count;                                              /* +0x20 */
    int32_t block_cycles;                                              /* +0x24 */
    uint32_t cache_size;                                               /* +0x28 */
    uint32_t lookahead_size;                                           /* +0x2c */
    uint32_t compact_thresh;                                           /* +0x30 */
    void *read_buffer;                                                 /* +0x34 */
    void *prog_buffer;                                                 /* +0x38 */
    void *lookahead_buffer;                                            /* +0x3c */
    uint32_t name_max;                                                 /* +0x40 */
    uint32_t file_max;                                                 /* +0x44 */
    uint32_t attr_max;                                                 /* +0x48 */
    uint32_t metadata_max;                                             /* +0x4c */
    uint32_t inline_max;                                               /* +0x50 */
} g2_lfs_config_t;
_Static_assert(sizeof(g2_lfs_config_t) == 0x54, "stock lfs_config is 84 bytes");

/* lfs_dir_t of littlefs v2.10.1: 52 bytes, kept on the stack. */
typedef struct {
    uint32_t words[13];
} g2_lfs_dir_t;
_Static_assert(sizeof(g2_lfs_dir_t) == 0x34, "stock lfs_dir_t is 52 bytes");

extern uint8_t audio_file_lfs_context[];              /* RAM 0x20071ac8, lfs_t */
extern uint8_t g2_littlefs_boot_count_file[];         /* RAM 0x200728a0, lfs_file_t */
extern uint32_t audio_file_ready_200746a8;            /* RAM 0x200746a8, 1 once mounted */

/* LittleFS public API (pinned lfs.c wrappers). */
extern int32_t lfs_format_4cfa58(void *lfs, const g2_lfs_config_t *cfg);
extern int32_t lfs_mount_4cfa62(void *lfs, const g2_lfs_config_t *cfg);
extern int32_t lfs_unmount_4cfa6c(void *lfs);
extern int32_t audio_file_lfs_open(void *lfs, void *file, const char *path, uint32_t flags); /* 0x4cfa94 */
extern int32_t audio_file_lfs_close_4cfad0(void *lfs, void *file);
extern int32_t audio_file_lfs_read(void *lfs, void *file, void *buffer, uint32_t size); /* 0x4cfb40 */
extern int32_t audio_file_lfs_write_4cfb7c(void *lfs, void *file, const void *buffer, uint32_t size);
extern int32_t lfs_file_rewind_4cfc24(void *lfs, void *file);
extern int32_t audio_file_lfs_mkdir_4cfc5c(void *lfs, const char *path);
extern int32_t audio_file_lfs_dir_open_4cfc66(void *lfs, void *dir, const char *path);
extern int32_t audio_file_lfs_dir_close_4cfcf8(void *lfs, void *dir);

/* MX25U25643G MSPI driver: 0 on success, AM_HAL status otherwise. */
extern uint32_t g2_norflash_read_471020(uint32_t address, void *buffer, uint32_t size);
extern int32_t g2_norflash_write_lower_4708a8(int32_t address, const uint8_t *buffer, uint32_t size);
extern uint32_t g2_norflash_erase_lower_47075c(uint32_t address);
extern int32_t audio_ble_hci_boot_log_4733ee(const char *format, ...); /* printf-style transport */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "file_system"; /* ROM 0x78abc8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\port\\littlefs_mx25u25643g_porting.c"; /* ROM 0x6dd654 */
static const char check_fn[] = "check_and_create_directories"; /* ROM 0x760530 */
static const char format_fn[] = "littlefs_format";               /* ROM 0x7861d0 */
static const char init_fn[] = "littlefs_init";                   /* ROM 0x7861e0 */

static const char dir_firmware[] = "/firmware"; /* ROM 0x78abbc */
static const char dir_ota[] = "/ota";           /* ROM 0x78d7f4 */
static const char dir_user[] = "/user";         /* ROM 0x78d7fc */
static const char dir_log[] = "/log";           /* ROM 0x78d804 */
static const char boot_count_path[] = "boot_count"; /* ROM 0x78abd4 */

static const char created[] = "Created directory: %s"; /* ROM 0x777cfc */
static const char created_short[] = "[file_system]Created directory: %s"; /* ROM 0x754f08 */
static const char already[] = "Directory already exists: %s"; /* ROM 0x760550 */
static const char already_short[] = "[file_system]Directory already exists: %s"; /* ROM 0x73f294 */
static const char create_failed[] = "Failed to create directory %s: %d"; /* ROM 0x754f2c */
static const char create_failed_short[] = "[file_system]Failed to create directory %s: %d"; /* ROM 0x734b74 */
static const char exists[] = "Directory exists: %s"; /* ROM 0x777d14 */
static const char exists_short[] = "[file_system]Directory exists: %s"; /* ROM 0x754f50 */
static const char check_failed[] = "Error checking directory %s: %d"; /* ROM 0x760570 */
static const char check_failed_short[] = "[file_system]Error checking directory %s: %d"; /* ROM 0x734ba4 */
static const char mount_failed[] = "lfs_mount faild: %d\n"; /* ROM 0x777d2c */
static const char mount_failed_short[] = "[file_system]lfs_mount faild: %d\n"; /* ROM 0x754f74 */
static const char dirs_failed[] = "check_and_create_directories faild\n"; /* ROM 0x754f98 */
static const char dirs_failed_short[] = "[file_system]check_and_create_directories faild\n"; /* ROM 0x72a224 */
static const char format_failed[] = "lfs_format faild: %d\n"; /* ROM 0x777d44 */
static const char format_failed_short[] = "[file_system]lfs_format faild: %d\n"; /* ROM 0x754fbc */
static const char dirs_reformat[] =
    "check_and_create_directories faild, format and create again\n"; /* ROM 0x70c3e4 */
static const char dirs_reformat_short[] =
    "[file_system]check_and_create_directories faild, format and create again\n"; /* ROM 0x6f3f30 */
static const char boot_count_msg[] = "boot_count: %d"; /* ROM 0x7861f0 */
static const char boot_count_short[] = "[file_system]boot_count: %d"; /* ROM 0x76c1cc */
static const char read_failed[] =
    "lfs READ fail: block=%u, off=%u, size=%u, addr=0x%08X, st=%d\n"; /* ROM 0x70c424 */
static const char prog_failed[] =
    "lfs PROG fail: block=%u, off=%u, size=%u, addr=0x%08X, st=%d\n"; /* ROM 0x70c464 */
static const char erase_failed[] = "lfs ERASE fail: block=%u, addr=0x%08X, st=%d\n"; /* ROM 0x734bd4 */

#define FS_LOG(level, mask, fn, line, fmt, short_fmt, ...)                                   \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                            \
            (void)compress_log_output((mask), (short_fmt), (short_fmt), ##__VA_ARGS__);      \
    } while (0)

int littlefs_block_read_4763b8(const g2_lfs_config_t *cfg, uint32_t block, uint32_t off,
                               void *buffer, uint32_t size)
{
    (void)cfg;
    uint32_t address = off + (block << LITTLEFS_BLOCK_SHIFT) + LITTLEFS_NOR_BASE;
    uint32_t status = g2_norflash_read_471020(address, buffer, size);
    if (status != 0u) {
        (void)audio_ble_hci_boot_log_4733ee(read_failed, block, off, size, address, status);
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

/* Stock 0x4763f0, not a TSV row. */
int littlefs_block_prog_4763f0(const g2_lfs_config_t *cfg, uint32_t block, uint32_t off,
                               const void *buffer, uint32_t size)
{
    (void)cfg;
    uint32_t address = off + (block << LITTLEFS_BLOCK_SHIFT) + LITTLEFS_NOR_BASE;
    int32_t status = g2_norflash_write_lower_4708a8((int32_t)address, (const uint8_t *)buffer, size);
    if (status != 0) {
        (void)audio_ble_hci_boot_log_4733ee(prog_failed, block, off, size, address, status);
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

/* Stock 0x476428, not a TSV row. */
int littlefs_block_erase_476428(const g2_lfs_config_t *cfg, uint32_t block)
{
    (void)cfg;
    uint32_t address = (block << LITTLEFS_BLOCK_SHIFT) + LITTLEFS_NOR_BASE;
    uint32_t status = g2_norflash_erase_lower_47075c(address);
    if (status != 0u) {
        (void)audio_ble_hci_boot_log_4733ee(erase_failed, block, address, status);
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

/* Stock 0x4764dc (movs r0,#0; bx lr inside the literal pool), not a TSV row. */
int littlefs_block_sync_4764dc(const g2_lfs_config_t *cfg)
{
    (void)cfg;
    return LFS_ERR_OK;
}

/* ROM 0x6e83a4. */
const g2_lfs_config_t g2_littlefs_config = {
    .context = 0,
    .read = littlefs_block_read_4763b8,
    .prog = littlefs_block_prog_4763f0,
    .erase = littlefs_block_erase_476428,
    .sync = littlefs_block_sync_4764dc,
    .read_size = 16u,
    .prog_size = 256u,
    .block_size = 4096u,
    .block_count = 3008u,
    .block_cycles = 500,
    .cache_size = 4096u,
    .lookahead_size = 256u,
};

/* Opens each top-level directory, creating missing ones. Returns -1 only when
 * lfs_dir_open fails with something other than LFS_ERR_NOENT; mkdir failures
 * are logged and skipped. */
int check_and_create_directories_475fe8(void)
{
    const char *directories[4] = { dir_firmware, dir_ota, dir_user, dir_log }; /* ROM template 0x786200 */
    g2_lfs_dir_t dir;

    for (int i = 0; i < 4; i++) {
        int32_t err = audio_file_lfs_dir_open_4cfc66(audio_file_lfs_context, &dir, directories[i]);
        if (err == LFS_ERR_NOENT) {
            err = audio_file_lfs_mkdir_4cfc5c(audio_file_lfs_context, directories[i]);
            if (err == 0) {
                FS_LOG(4u, 0x10400000u, check_fn, 0x51u, created, created_short, directories[i]);
            } else if (err == LFS_ERR_EXIST) {
                FS_LOG(4u, 0x10400000u, check_fn, 0x53u, already, already_short, directories[i]);
            } else {
                FS_LOG(2u, 0x08800000u, check_fn, 0x55u, create_failed, create_failed_short,
                       directories[i], err);
            }
        } else if (err == 0) {
            (void)audio_file_lfs_dir_close_4cfcf8(audio_file_lfs_context, &dir);
            FS_LOG(4u, 0x10400000u, check_fn, 0x5au, exists, exists_short, directories[i]);
        } else {
            FS_LOG(2u, 0x08800000u, check_fn, 0x5cu, check_failed, check_failed_short,
                   directories[i], err);
            return -1;
        }
    }
    return 0;
}

int littlefs_format_4761d2(void)
{
    (void)lfs_unmount_4cfa6c(audio_file_lfs_context);
    (void)lfs_format_4cfa58(audio_file_lfs_context, &g2_littlefs_config);
    int32_t err = lfs_mount_4cfa62(audio_file_lfs_context, &g2_littlefs_config);
    if (err != 0) {
        FS_LOG(2u, 0x08400000u, format_fn, 0x6bu, mount_failed, mount_failed_short, err);
        return LITTLEFS_RESULT_FAILED;
    }
    if (check_and_create_directories_475fe8() != 0) {
        FS_LOG(2u, 0x08000000u, format_fn, 0x6fu, dirs_failed, dirs_failed_short);
        return LITTLEFS_RESULT_FAILED;
    }
    return 0;
}

/* Mounts (formatting once on failure), ensures the directory set, marks the
 * filesystem ready and increments the persistent boot_count file. */
int littlefs_init_47627e(void)
{
    if (lfs_mount_4cfa62(audio_file_lfs_context, &g2_littlefs_config) != 0) {
        (void)lfs_format_4cfa58(audio_file_lfs_context, &g2_littlefs_config);
        int32_t err = lfs_mount_4cfa62(audio_file_lfs_context, &g2_littlefs_config);
        if (err != 0) {
            /* The stock message says lfs_format, but the value is the mount result. */
            FS_LOG(2u, 0x08400000u, init_fn, 0x7fu, format_failed, format_failed_short, err);
            return LITTLEFS_RESULT_FAILED;
        }
    }
    if (check_and_create_directories_475fe8() != 0) {
        FS_LOG(2u, 0x08000000u, init_fn, 0x86u, dirs_reformat, dirs_reformat_short);
        (void)littlefs_format_4761d2();
    }
    audio_file_ready_200746a8 = 1u;

    uint32_t boot_count = 0u;
    (void)audio_file_lfs_open(audio_file_lfs_context, g2_littlefs_boot_count_file, boot_count_path,
                              LFS_O_RDWR | LFS_O_CREAT);
    (void)audio_file_lfs_read(audio_file_lfs_context, g2_littlefs_boot_count_file, &boot_count, 4u);
    boot_count++;
    (void)lfs_file_rewind_4cfc24(audio_file_lfs_context, g2_littlefs_boot_count_file);
    (void)audio_file_lfs_write_4cfb7c(audio_file_lfs_context, g2_littlefs_boot_count_file, &boot_count, 4u);
    (void)audio_file_lfs_close_4cfad0(audio_file_lfs_context, g2_littlefs_boot_count_file);
    FS_LOG(4u, 0x10400000u, init_fn, 0x9au, boot_count_msg, boot_count_short, boot_count);
    return 0;
}
