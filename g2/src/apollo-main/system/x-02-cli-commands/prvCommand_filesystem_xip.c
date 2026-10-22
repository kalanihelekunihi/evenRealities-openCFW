/* Product FreeRTOS-Plus-CLI filesystem module, rename and XIP commands.
 * Stock source: D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\
 *               prvCommand\prvCommand_filesystem.c
 * Native: rename 0x57f68c..0x57f8b1, xip 0x57f8bc..0x57f937 (inline "/"
 * 0x57f93c), file2xip 0x57f980..0x57fc53 (inline "\r\n" 0x57fc58, pool
 * 0x57fc5c..0x57fcab), xip2file 0x57fcac..0x57ff0b (pool
 * 0x57ff10..0x57ff3f, inline "\r\n" 0x57ffa0, shared pool
 * 0x57ffa8..0x5800c3). The other commands of this file are in
 * system/u-07/prvCommand_filesystem.c and
 * a-59-cli-commands/prvCommand_filesystem_free.c.
 *
 * XIP addresses 0x80000000..0x81ffffff map the 32 MiB external NOR
 * (flash offset = address - 0x80000000). file2xip erases 4 KiB sectors
 * lazily (skipping the last sector it erased, cell RAM 0x20003324,
 * initial 0xffffffff), programs 4 KiB chunks and reads each one back for
 * verification; xip2file copies mapped flash into a littlefs file. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define FS_NAME_BYTES 256u
#define FS_PARAM_MAX 255
#define XIP_PATH_BYTES 128u
#define XIP_NUMBER_BYTES 16u
#define XIP_CHUNK_BYTES 0x1000u
#define XIP_SECTOR_MASK 0xfffff000u
#define XIP_BASE 0x80000000u
#define XIP_SIZE 0x02000000u
#define XIP_DUMP_WORDS_MAX 32u
#define LFS_O_RDONLY 1u
#define LFS_O_WRONLY_CREAT_TRUNC 0x502u /* LFS_O_WRONLY | LFS_O_CREAT | LFS_O_TRUNC */

typedef struct {
    uint8_t type;            /* +0x00 */
    uint32_t size;           /* +0x04 */
    char name[256];          /* +0x08 */
} g2_lfs_info_t;
_Static_assert(sizeof(g2_lfs_info_t) == 264, "lfs_info is 264 bytes");

typedef struct { uint32_t words[21]; } g2_lfs_file_t; /* lfs_file_t, 84 bytes */

extern uint32_t audio_file_ready_200746a8;  /* RAM 0x200746a8: 1 when littlefs is mounted */
extern uint8_t audio_file_lfs_context[];    /* RAM 0x20071ac8: lfs_t */
extern char g2_cli_cwd[128];                /* RAM 0x200031b4 */
extern void *g2_codec_heap_pool;            /* RAM 0x20074abc: tlsf_t of the file/codec heap */
extern uint32_t g2_xip_last_erased_sector_20003324; /* RAM 0x20003324, initial 0xffffffff */

extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern char *g2_strcpy_48d540(char *dst, const char *src);
extern uint32_t g2_log_module_length(const char *text);      /* 0x44a43c strlen */
extern uint8_t *g2_strcat(uint8_t *dst, const uint8_t *src); /* 0x567c80 strcat */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t len); /* 0x4751c8 memcmp */
extern uint32_t strtoul_48d874(const char *text, char **end, int32_t base);
extern int32_t fs_normalize_path_57eaa8(char *out, const char *in);
extern int32_t lfs_rename_4cfa80(void *lfs, const char *old_path, const char *new_path);
extern int32_t lfs_stat_4cfa8a(void *lfs, const char *path, void *info);
extern int32_t audio_file_lfs_open(void *lfs, void *file, const char *path, uint32_t flags); /* 0x4cfa94 */
extern int32_t audio_file_lfs_close_4cfad0(void *lfs, void *file);
extern int32_t audio_file_lfs_read(void *lfs, void *file, void *buf, uint32_t size);   /* 0x4cfb40 */
extern int32_t audio_file_lfs_write_4cfb7c(void *lfs, void *file, const void *buf, uint32_t size);
extern int32_t lfs_file_size_4cfc2e(void *lfs, void *file);
extern void *g2_file_pool_allocate(void *pool, uint32_t bytes); /* 0x4d0722 tlsf_malloc */
extern void g2_file_pool_free(void *pool, void *block);         /* 0x4d0808 tlsf_free */
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern uint32_t g2_norflash_erase_lower_47075c(uint32_t address); /* 4 KiB sector */
extern int32_t norflash_write_4709c0(int32_t address, const uint8_t *buffer, uint32_t size);
extern int32_t g2_norflash_read_lower_4709c8(int32_t address, uint8_t *buffer, uint32_t size);
extern void elog_start_43d19a(void);
extern void elog_stop_43d1fc(void);

static const char s_slash[] = "/";     /* ROM 0x57f93c */
static const char s_crlf[] = "\r\n";   /* ROM 0x57fc58 / 0x57ffa0 */
static const char s_join[] = "%s/%s";  /* ROM 0x78e13c */
static const char s_rename_missing[] = "rename: missing operand\r\n";              /* ROM 0x76ff7c */
static const char s_rename_usage[] = "Usage: rename <old_name> <new_name>\r\n";    /* ROM 0x74cd3c */
static const char s_rename_p1_long[] = "rename: parameter1 too long\r\n";          /* ROM 0x763cf0 */
static const char s_rename_p2_long[] = "rename: parameter2 too long\r\n";          /* ROM 0x763d10 */
static const char s_rename_bad_src[] = "rename: invalid source path\r\n";          /* ROM 0x763d30 */
static const char s_rename_bad_dst[] = "rename: invalid destination path\r\n";     /* ROM 0x758454 */
static const char s_rename_not_found[] =
    "rename: source file/directory not found (error: %d)\r\n";                     /* ROM 0x7219b0 */
static const char s_rename_looking[] = "rename: looking for file: '%s'\r\n";       /* ROM 0x758478 */
static const char s_rename_exists[] = "rename: destination already exists\r\n";    /* ROM 0x74cd64 */
static const char s_rename_failed[] = "rename: operation failed (error code: %d)\r\n"; /* ROM 0x741c00 */
static const char s_xip_error[] = "xip: address or length error\r\n";              /* ROM 0x763d50 */
static const char s_xip_word[] = "0X%08X: 0x%08x \r\n";                            /* ROM 0x7827a4 */
static const char s_f2x_unmounted[] = "file2xip: filesystem not mounted\r\n";      /* ROM 0x75849c */
static const char s_f2x_usage[] =
    "file2xip: invalid parameters\r\nUsage: file2xip <filepath> <xip_address>\r\n"; /* ROM 0x6f560c */
static const char s_f2x_example[] = "Example: file2xip s200_font.bin 0x80100000\r\n"; /* ROM 0x736d94 */
static const char s_f2x_path_long[] = "file2xip: filepath too long\r\n";           /* ROM 0x763d70 */
static const char s_f2x_addr_long[] = "file2xip: xip address too long\r\n";        /* ROM 0x7584c0 */
static const char s_f2x_bad_addr[] =
    "file2xip: invalid XIP address 0x%08X\r\nValid range: 0x80000000 - 0x81FFFFFF\r\n"; /* ROM 0x6ef1d8 */
static const char s_f2x_open_failed[] = "file2xip: failed to open file '%s', error: %d\r\n"; /* ROM 0x736dc4 */
static const char s_f2x_empty[] = "file2xip: file '%s' is empty\r\n";              /* ROM 0x763d90 */
static const char s_f2x_writing[] =
    "file2xip: writing file '%s' (%d bytes) to XIP address 0x%08X (flash 0x%08X)\r\n"; /* ROM 0x6ef228 */
static const char s_f2x_no_buffer[] = "file2xip: failed to allocate read buffer\r\n"; /* ROM 0x741c2c */
static const char s_f2x_progress[] = "\rfile2xip: progress %d%% (%d/%d bytes)";   /* ROM 0x74cd8c */
static const char s_f2x_read_failed[] = "file2xip: failed to read from file, error: %d\r\n"; /* ROM 0x736df4 */
static const char s_f2x_erase_failed[] = "file2xip: erase failed at 0x%08X, error: %d\r\n"; /* ROM 0x736e24 */
static const char s_f2x_write_failed[] =
    "file2xip: failed to write to flash at 0x%08X, error: %d\r\n";                 /* ROM 0x717c08 */
static const char s_f2x_verify_failed[] = "file2xip: data verification failed at 0x%08X\r\n"; /* ROM 0x736e54 */
static const char s_f2x_done[] =
    "file2xip: successfully written %d bytes to XIP address 0x%08X\r\n";           /* ROM 0x70df64 */
static const char s_f2x_incomplete[] = "file2xip: write incomplete, %d/%d bytes written\r\n"; /* ROM 0x72c0d0 */
static const char s_x2f_unmounted[] = "xip2file: filesystem not mounted\r\n";      /* ROM 0x7584e4 */
static const char s_x2f_usage[] =
    "xip2file: invalid parameters\r\nUsage: xip2file <filepath> <xip_address> <length>\r\n"; /* ROM 0x6e9508 */
static const char s_x2f_example[] = "Example: xip2file s200_font.bin 0x80100000 65536\r\n"; /* ROM 0x72c104 */
static const char s_x2f_path_long[] = "xip2file: filepath too long\r\n";           /* ROM 0x763db0 */
static const char s_x2f_addr_long[] = "xip2file: xip address too long\r\n";        /* ROM 0x758508 */
static const char s_x2f_len_long[] = "xip2file: length too long\r\n";              /* ROM 0x76ff98 */
static const char s_x2f_len_zero[] = "xip2file: length must be > 0\r\n";           /* ROM 0x763dd0 */
static const char s_x2f_bad_addr[] =
    "xip2file: invalid XIP address 0x%08X\r\nValid range: 0x80000000 - 0x81FFFFFF\r\n"; /* ROM 0x6ef278 */
static const char s_x2f_overflow[] = "xip2file: read range overflow (0x%08X + %u)\r\n"; /* ROM 0x736e84 */
static const char s_x2f_open_failed[] = "xip2file: failed to open file '%s', error: %d\r\n"; /* ROM 0x736eb4 */
static const char s_x2f_reading[] =
    "xip2file: reading %d bytes from XIP address 0x%08X to file '%s'\r\n";         /* ROM 0x704a34 */
static const char s_x2f_no_buffer[] = "xip2file: failed to allocate read buffer\r\n"; /* ROM 0x741c58 */
static const char s_x2f_progress[] = "\rxip2file: progress %d%% (%d/%d bytes)";   /* ROM 0x74cdb4 */
static const char s_x2f_write_failed[] = "xip2file: failed to write file, error: %d\r\n"; /* ROM 0x741c84 */
static const char s_x2f_done[] =
    "xip2file: successfully read %d bytes from XIP address 0x%08X\r\n";            /* ROM 0x70dfa4 */
static const char s_x2f_incomplete[] = "xip2file: read incomplete, %d/%d bytes read\r\n"; /* ROM 0x736ee4 */

int32_t cli_cmd_rename_57f68c(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_xip_57f8bc(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_file2xip_57f980(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_xip2file_57fcac(char *write_buffer, size_t write_buffer_len, const char *command_string);

/* Absolute names are kept (strncpy 254); relative ones are joined to the
 * working directory with a single '/'. */
static void rename_join_path(char *out, const char *name)
{
    (void)aeabi_memset_43c0e4(out, FS_PARAM_MAX, 0);
    if (name[0] == '/') {
        (void)audio_settings_copy_text(out, name, FS_PARAM_MAX - 1);
        return;
    }
    (void)g2_strcpy_48d540(out, g2_cli_cwd);
    if (g2_cli_cwd[g2_log_module_length(g2_cli_cwd) - 1u] != '/' && name[0] != '/')
        (void)g2_strcat((uint8_t *)out, (const uint8_t *)s_slash);
    (void)g2_strcat((uint8_t *)out, (const uint8_t *)name);
}

int32_t cli_cmd_rename_57f68c(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t new_length;
    int32_t old_length;
    g2_lfs_info_t dst_info;
    g2_lfs_info_t src_info;
    char dst_norm[FS_NAME_BYTES];
    char src_norm[FS_NAME_BYTES];
    char dst_path[FS_NAME_BYTES];
    char src_path[FS_NAME_BYTES];
    char new_name[FS_NAME_BYTES];
    char old_name[FS_NAME_BYTES];
    const char *old_text;
    const char *new_text;
    int32_t err;

    (void)write_buffer;
    (void)write_buffer_len;
    if (audio_file_ready_200746a8 != 1u)
        return 0;
    old_text = freertos_cli_get_parameter_5848fc(command_string, 1u, &old_length);
    new_text = freertos_cli_get_parameter_5848fc(command_string, 2u, &new_length);
    if (old_text == NULL || new_text == NULL) {
        audio_ble_hci_boot_log_4733ee(s_rename_missing);
        audio_ble_hci_boot_log_4733ee(s_rename_usage);
        return 0;
    }
    if (old_length >= FS_PARAM_MAX) {
        audio_ble_hci_boot_log_4733ee(s_rename_p1_long);
        return 0;
    }
    (void)audio_queue_copy_bytes(old_name, old_text, (uint32_t)old_length);
    old_name[old_length] = '\0';
    if (new_length >= FS_PARAM_MAX) {
        audio_ble_hci_boot_log_4733ee(s_rename_p2_long);
        return 0;
    }
    (void)audio_queue_copy_bytes(new_name, new_text, (uint32_t)new_length);
    new_name[new_length] = '\0';

    rename_join_path(src_path, old_name);
    rename_join_path(dst_path, new_name);
    if (fs_normalize_path_57eaa8(src_norm, src_path) != 0) {
        audio_ble_hci_boot_log_4733ee(s_rename_bad_src);
        return 0;
    }
    if (fs_normalize_path_57eaa8(dst_norm, dst_path) != 0) {
        audio_ble_hci_boot_log_4733ee(s_rename_bad_dst);
        return 0;
    }
    err = lfs_stat_4cfa8a(audio_file_lfs_context, src_norm, &src_info);
    if (err != 0) {
        audio_ble_hci_boot_log_4733ee(s_rename_not_found, err);
        audio_ble_hci_boot_log_4733ee(s_rename_looking, src_norm);
        return 0;
    }
    if (lfs_stat_4cfa8a(audio_file_lfs_context, dst_norm, &dst_info) == 0) {
        audio_ble_hci_boot_log_4733ee(s_rename_exists);
        return 0;
    }
    err = lfs_rename_4cfa80(audio_file_lfs_context, src_norm, dst_norm);
    if (err != 0)
        audio_ble_hci_boot_log_4733ee(s_rename_failed, err);
    return 0;
}

/* "xip <hex address> <words>": dump up to 32 words of mapped flash. The
 * range test admits 0x80000000..0x82000000 inclusive. */
int32_t cli_cmd_xip_57f8bc(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length_count;
    int32_t length_addr;
    const char *addr_text;
    const char *count_text;
    const volatile uint32_t *words;
    uint32_t address;
    uint32_t count;
    uint32_t i;

    (void)write_buffer;
    (void)write_buffer_len;
    addr_text = freertos_cli_get_parameter_5848fc(command_string, 1u, &length_addr);
    count_text = freertos_cli_get_parameter_5848fc(command_string, 2u, &length_count);
    address = strtoul_48d874(addr_text, NULL, 16);
    count = strtoul_48d874(count_text, NULL, 10);
    if (address + XIP_BASE >= XIP_SIZE + 1u || count > XIP_DUMP_WORDS_MAX) {
        audio_ble_hci_boot_log_4733ee(s_xip_error);
        return 0;
    }
    g2_norflash_lock_46f65e();
    words = (const volatile uint32_t *)(uintptr_t)address;
    for (i = 0u; i < count; i++)
        audio_ble_hci_boot_log_4733ee(s_xip_word, (uint32_t)(uintptr_t)&words[i], words[i]);
    audio_ble_hci_boot_log_4733ee(s_crlf);
    g2_norflash_unlock_46f674();
    return 0;
}

/* Copy a CLI token into a NUL-terminated local buffer. */
static void xip_copy_token(char *out, const char *text, int32_t length)
{
    (void)audio_queue_copy_bytes(out, text, (uint32_t)length);
    out[length] = '\0';
}

static void xip_build_path(char *path, const char *name)
{
    if (name[0] == '/')
        (void)audio_settings_copy_text(path, name, XIP_PATH_BYTES - 1u);
    else
        (void)g2_audio_dump_snprintf(path, XIP_PATH_BYTES, s_join, g2_cli_cwd, name);
    path[XIP_PATH_BYTES - 1u] = '\0';
}

/* Erase every 4 KiB sector of [flash, flash + length) except the one
 * erased last; 0 on success. */
static uint32_t file2xip_erase(uint32_t flash, uint32_t length)
{
    uint32_t sector = flash & XIP_SECTOR_MASK;
    uint32_t last = (length + flash - 1u) & XIP_SECTOR_MASK;
    uint32_t err;

    for (; sector <= last; sector += XIP_CHUNK_BYTES) {
        if (sector == g2_xip_last_erased_sector_20003324)
            continue;
        err = g2_norflash_erase_lower_47075c(sector);
        if (err != 0u) {
            audio_ble_hci_boot_log_4733ee(s_f2x_erase_failed, sector, err);
            return err;
        }
        g2_xip_last_erased_sector_20003324 = sector;
    }
    return 0u;
}

int32_t cli_cmd_file2xip_57f980(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length_addr;
    int32_t length_path;
    uint32_t chunk = XIP_CHUNK_BYTES;
    uint32_t xip_address;
    char addr_text[XIP_NUMBER_BYTES];
    char path[XIP_PATH_BYTES];
    char name[XIP_PATH_BYTES];
    g2_lfs_file_t file;
    const char *name_text;
    const char *addr_param;
    uint8_t *buffer;
    uint8_t *verify;
    uint32_t written = 0u;
    uint32_t size;
    uint32_t flash;
    int32_t got;
    int32_t err;

    (void)write_buffer;
    (void)write_buffer_len;
    if (audio_file_ready_200746a8 != 1u) {
        audio_ble_hci_boot_log_4733ee(s_f2x_unmounted);
        return 0;
    }
    name_text = freertos_cli_get_parameter_5848fc(command_string, 1u, &length_path);
    addr_param = freertos_cli_get_parameter_5848fc(command_string, 2u, &length_addr);
    if (name_text == NULL || addr_param == NULL) {
        audio_ble_hci_boot_log_4733ee(s_f2x_usage);
        audio_ble_hci_boot_log_4733ee(s_f2x_example);
        return 0;
    }
    if ((uint32_t)length_path >= XIP_PATH_BYTES) {
        audio_ble_hci_boot_log_4733ee(s_f2x_path_long);
        return 0;
    }
    xip_copy_token(name, name_text, length_path);
    if ((uint32_t)length_addr >= XIP_NUMBER_BYTES) {
        audio_ble_hci_boot_log_4733ee(s_f2x_addr_long);
        return 0;
    }
    xip_copy_token(addr_text, addr_param, length_addr);
    xip_address = strtoul_48d874(addr_text, NULL, 16);
    if (xip_address + XIP_BASE >= XIP_SIZE) {
        audio_ble_hci_boot_log_4733ee(s_f2x_bad_addr, xip_address);
        return 0;
    }
    flash = xip_address + XIP_BASE;
    xip_build_path(path, name);

    err = audio_file_lfs_open(audio_file_lfs_context, &file, path, LFS_O_RDONLY);
    if (err < 0) {
        audio_ble_hci_boot_log_4733ee(s_f2x_open_failed, path, err);
        return 0;
    }
    size = (uint32_t)lfs_file_size_4cfc2e(audio_file_lfs_context, &file);
    if (size == 0u) {
        audio_ble_hci_boot_log_4733ee(s_f2x_empty, path);
        (void)audio_file_lfs_close_4cfad0(audio_file_lfs_context, &file);
        return 0;
    }
    audio_ble_hci_boot_log_4733ee(s_f2x_writing, path, size, xip_address, flash);
    buffer = g2_file_pool_allocate(g2_codec_heap_pool, chunk);
    if (buffer == NULL) {
        audio_ble_hci_boot_log_4733ee(s_f2x_no_buffer);
        (void)audio_file_lfs_close_4cfad0(audio_file_lfs_context, &file);
        return 0;
    }
    elog_stop_43d1fc();
    while (written < size) {
        /* Stock treats only a 0 return as a read failure. */
        got = audio_file_lfs_read(audio_file_lfs_context, &file, buffer,
                                  chunk < size - written ? chunk : size - written);
        if (got == 0) {
            audio_ble_hci_boot_log_4733ee(s_f2x_read_failed, got);
            break;
        }
        if (file2xip_erase(flash, (uint32_t)got) != 0u)
            break;
        err = norflash_write_4709c0((int32_t)flash, buffer, (uint32_t)got);
        if (err != 0) {
            audio_ble_hci_boot_log_4733ee(s_f2x_write_failed, flash, err);
            break;
        }
        verify = g2_file_pool_allocate(g2_codec_heap_pool, (uint32_t)got);
        if (verify != NULL) {
            if (g2_norflash_read_lower_4709c8((int32_t)flash, verify, (uint32_t)got) == 0 &&
                g2_lfs_memcmp(verify, buffer, (uint32_t)got) != 0) {
                audio_ble_hci_boot_log_4733ee(s_f2x_verify_failed, flash);
                g2_file_pool_free(g2_codec_heap_pool, verify);
                break;
            }
            g2_file_pool_free(g2_codec_heap_pool, verify);
        }
        written += (uint32_t)got;
        flash += (uint32_t)got;
        audio_ble_hci_boot_log_4733ee(s_f2x_progress, (100u * written) / size, written, size);
    }
    if (buffer != NULL)
        g2_file_pool_free(g2_codec_heap_pool, buffer);
    (void)audio_file_lfs_close_4cfad0(audio_file_lfs_context, &file);
    audio_ble_hci_boot_log_4733ee(s_crlf);
    elog_start_43d19a();
    if (written == size)
        audio_ble_hci_boot_log_4733ee(s_f2x_done, written, xip_address);
    else
        audio_ble_hci_boot_log_4733ee(s_f2x_incomplete, written, size);
    return 0;
}

int32_t cli_cmd_xip2file_57fcac(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length_len;
    int32_t length_addr;
    int32_t length_path;
    uint32_t chunk_max = XIP_CHUNK_BYTES;
    char len_text[XIP_NUMBER_BYTES];
    char addr_text[XIP_NUMBER_BYTES];
    char path[XIP_PATH_BYTES];
    char name[XIP_PATH_BYTES];
    g2_lfs_file_t file;
    const char *name_param;
    const char *addr_param;
    const char *len_param;
    uint8_t *buffer;
    uint32_t xip_address;
    uint32_t length;
    uint32_t done = 0u;
    uint32_t source;
    uint32_t chunk;
    int32_t err;

    (void)write_buffer;
    (void)write_buffer_len;
    if (audio_file_ready_200746a8 != 1u) {
        audio_ble_hci_boot_log_4733ee(s_x2f_unmounted);
        return 0;
    }
    name_param = freertos_cli_get_parameter_5848fc(command_string, 1u, &length_path);
    addr_param = freertos_cli_get_parameter_5848fc(command_string, 2u, &length_addr);
    len_param = freertos_cli_get_parameter_5848fc(command_string, 3u, &length_len);
    if (name_param == NULL || addr_param == NULL || len_param == NULL) {
        audio_ble_hci_boot_log_4733ee(s_x2f_usage);
        audio_ble_hci_boot_log_4733ee(s_x2f_example);
        return 0;
    }
    if ((uint32_t)length_path >= XIP_PATH_BYTES) {
        audio_ble_hci_boot_log_4733ee(s_x2f_path_long);
        return 0;
    }
    xip_copy_token(name, name_param, length_path);
    if ((uint32_t)length_addr >= XIP_NUMBER_BYTES) {
        audio_ble_hci_boot_log_4733ee(s_x2f_addr_long);
        return 0;
    }
    xip_copy_token(addr_text, addr_param, length_addr);
    if ((uint32_t)length_len >= XIP_NUMBER_BYTES) {
        audio_ble_hci_boot_log_4733ee(s_x2f_len_long);
        return 0;
    }
    xip_copy_token(len_text, len_param, length_len);
    xip_address = strtoul_48d874(addr_text, NULL, 16);
    length = strtoul_48d874(len_text, NULL, 10);
    if (length == 0u) {
        audio_ble_hci_boot_log_4733ee(s_x2f_len_zero);
        return 0;
    }
    if (xip_address + XIP_BASE >= XIP_SIZE) {
        audio_ble_hci_boot_log_4733ee(s_x2f_bad_addr, xip_address);
        return 0;
    }
    if (length + xip_address >= XIP_BASE + XIP_SIZE + 1u) {
        audio_ble_hci_boot_log_4733ee(s_x2f_overflow, xip_address, length);
        return 0;
    }
    xip_build_path(path, name);

    err = audio_file_lfs_open(audio_file_lfs_context, &file, path, LFS_O_WRONLY_CREAT_TRUNC);
    if (err < 0) {
        audio_ble_hci_boot_log_4733ee(s_x2f_open_failed, path, err);
        return 0;
    }
    audio_ble_hci_boot_log_4733ee(s_x2f_reading, length, xip_address, path);
    buffer = g2_file_pool_allocate(g2_codec_heap_pool, chunk_max);
    if (buffer == NULL) {
        audio_ble_hci_boot_log_4733ee(s_x2f_no_buffer);
        (void)audio_file_lfs_close_4cfad0(audio_file_lfs_context, &file);
        return 0;
    }
    source = xip_address;
    elog_stop_43d1fc();
    while (done < length) {
        chunk = chunk_max < length - done ? chunk_max : length - done;
        g2_norflash_lock_46f65e();
        (void)audio_queue_copy_bytes(buffer, (const void *)(uintptr_t)source, chunk);
        g2_norflash_unlock_46f674();
        err = audio_file_lfs_write_4cfb7c(audio_file_lfs_context, &file, buffer, chunk);
        if (err < 0 || (uint32_t)err != chunk) {
            audio_ble_hci_boot_log_4733ee(s_x2f_write_failed, err);
            break;
        }
        done += chunk;
        source += chunk;
        audio_ble_hci_boot_log_4733ee(s_x2f_progress, (100u * done) / length, done, length);
    }
    if (buffer != NULL)
        g2_file_pool_free(g2_codec_heap_pool, buffer);
    (void)audio_file_lfs_close_4cfad0(audio_file_lfs_context, &file);
    audio_ble_hci_boot_log_4733ee(s_crlf);
    elog_start_43d19a();
    if (done == length)
        audio_ble_hci_boot_log_4733ee(s_x2f_done, done, xip_address);
    else
        audio_ble_hci_boot_log_4733ee(s_x2f_incomplete, done, length);
    return 0;
}
