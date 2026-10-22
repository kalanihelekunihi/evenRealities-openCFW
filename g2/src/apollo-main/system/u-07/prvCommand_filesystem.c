/* Product FreeRTOS-Plus-CLI filesystem commands over littlefs.
 * Stock source: D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\
 *               prvCommand\prvCommand_filesystem.c
 * Native 0x57e898..0x57f550 (ls, cat, rm, path normalizer, cd, mkdir, touch,
 * pwd, mv, md5, df) plus the TLSF walker callback 0x57f530 used by the
 * memory command that follows at 0x57f550.
 *
 * The command handlers have the FreeRTOS-Plus-CLI interpreter signature
 * (write buffer, buffer length, command string). They never write the buffer;
 * all output goes through the console printf at 0x4733ee and every handler
 * returns 0 (pdFALSE, no more output) except ls, which returns littlefs
 * errors. In stock they are reached only through the CLI command table in
 * compressed initialized data.
 *
 * Shared state: the filesystem-ready word (RAM 0x200746a8), the mounted
 * lfs_t (RAM 0x20071ac8) and the 128-byte current working directory
 * (RAM 0x200031b4). littlefs is built without LFS_THREADSAFE, so
 * lfs->cfg (+0x68) has block_size at +0x1c and block_count at +0x20. */
#include <stdint.h>
#include <stddef.h>

/* littlefs 2.x ABI pieces used here. */
#define LFS_TYPE_DIR 2u
#define LFS_O_RDONLY 1u
#define LFS_O_WRONLY_CREAT 0x102u /* LFS_O_WRONLY | LFS_O_CREAT */

typedef struct {
    uint8_t type;     /* +0x00 LFS_TYPE_REG 1 / LFS_TYPE_DIR 2 */
    uint32_t size;    /* +0x04 */
    char name[256];   /* +0x08 LFS_NAME_MAX 255 */
} g2_lfs_info_t;
_Static_assert(sizeof(g2_lfs_info_t) == 264, "lfs_info is 264 bytes");

typedef struct { uint32_t words[13]; } g2_lfs_dir_t;  /* lfs_dir_t, 52 bytes */
typedef struct { uint32_t words[21]; } g2_lfs_file_t; /* lfs_file_t, 84 bytes */
typedef struct { uint32_t words[38]; } g2_md5_ctx_t;  /* 152-byte stack slot */

typedef struct {
    uint8_t opaque[0x1c];
    uint32_t block_size;  /* +0x1c */
    uint32_t block_count; /* +0x20 */
} g2_lfs_config_view_t;

/* TLSF walker totals filled by cli_heap_walker_57f530. */
typedef struct {
    uint32_t free_bytes;  /* +0x0 */
    uint32_t used_bytes;  /* +0x4 */
    uint32_t blocks;      /* +0x8 */
    uint32_t free_blocks; /* +0xc */
} g2_heap_walk_totals_t;

extern uint32_t audio_file_ready_200746a8;  /* RAM 0x200746a8: 1 when littlefs is mounted */
extern uint8_t audio_file_lfs_context[];    /* RAM 0x20071ac8: lfs_t */
extern char g2_cli_cwd[128];                /* RAM 0x200031b4: current working directory */

extern const char *freertos_cli_get_parameter_5848fc(const char *command, uint32_t index,
                                                     int32_t *length); /* 0x5848fc FreeRTOS_CLIGetParameter */
extern int32_t g2_log_transport_queue_failure(const char *format, ...); /* 0x4733ee console printf */
extern uint32_t g2_log_module_length(const char *s);                  /* 0x44a43c strlen */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 memset (dst, n, c) */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern uint8_t *g2_strcat(uint8_t *dst, const uint8_t *src);          /* 0x567c80 strcat */
extern uint8_t *g2_strrchr(const uint8_t *s, int32_t c);              /* 0x567c64 strrchr */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern char *g2_strcpy_48d540(char *dst, const char *src);            /* 0x48d540 strcpy */
extern char *g2_strtok_594884(char *s, const char *delim);            /* 0x594884 strtok */
extern int32_t audio_uart_font_path_compare(const char *a, const char *b); /* 0x46cacc strcmp */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t cap, const char *format, ...); /* 0x44b728 */
extern void cli_putchar_5415d8(int32_t c);                            /* 0x5415d8: one byte to UART1 */

extern int32_t audio_file_lfs_open(void *lfs, void *file, const char *path, uint32_t flags); /* 0x4cfa94 */
extern int32_t audio_file_lfs_read(void *lfs, void *file, void *buf, uint32_t size);      /* 0x4cfb40 */
extern int32_t audio_file_lfs_close_4cfad0(void *lfs, void *file);
extern int32_t audio_file_lfs_dir_open_4cfc66(void *lfs, void *dir, const char *path);
extern int32_t audio_file_lfs_dir_read_4cfd02(void *lfs, void *dir, void *info);
extern int32_t audio_file_lfs_dir_close_4cfcf8(void *lfs, void *dir);
extern int32_t audio_file_lfs_remove_4cfa76(void *lfs, const char *path);
extern int32_t audio_file_lfs_mkdir_4cfc5c(void *lfs, const char *path);
extern int32_t lfs_rename_4cfa80(void *lfs, const char *old_path, const char *new_path);
extern int32_t lfs_stat_4cfa8a(void *lfs, const char *path, void *info);
extern int32_t lfs_fs_size_4cfd0c(void *lfs);

extern void md5_init_59544e(void *ctx);
extern void md5_update_595578(void *ctx, const void *data, uint32_t len);
extern void md5_final_595608(uint8_t digest[16], void *ctx);

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *tag, const char *path, const char *function,
                               uint32_t line, const char *format, ...);
extern uint32_t compressed_log_output(uint32_t id, const char *format, const char *copy, ...);

static const char s_dot[] = ".";                        /* ROM 0x57eb84 */
static const char s_dotdot[] = "..";                    /* ROM 0x57eb88 */
static const char s_slash[] = "/";                      /* ROM 0x57eb8c (copies at 0x57ee08, 0x57f26c) */
static const char s_empty[] = "";                       /* ROM 0x57eb90 */
static const char s_percent_s[] = "%s";                 /* ROM 0x57ee04 */
static const char s_crlf[] = "\r\n";                    /* ROM 0x57f684 */
static const char s_ls_line[] = "%s%s\r\n";             /* ROM 0x78e134 */
static const char s_join[] = "%s/%s";                   /* ROM 0x78e13c */
static const char s_line[] = "%s\r\n";                  /* ROM 0x78e144 */
static const char s_error_path[] = "error path name\r\n";          /* ROM 0x78272c */
static const char s_invalid_path[] = "invaild path !\r\n";         /* ROM 0x782740 */
static const char s_mkdir_failed[] = "Directory creation failed\r\n"; /* ROM 0x76fdd8 */

static const char s_tag[] = "prvCommand_filesystem";    /* ROM 0x77aa14 */
static const char s_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\kernel\\FreeRTOS-Plus-CLI\\prvCommand\\prvCommand_filesystem.c"; /* ROM 0x6de434 */
static const char s_fn_mv[] = "prvCommand_mv";          /* ROM 0x788140 */
static const char s_fn_df[] = "prvCommand_df";          /* ROM 0x788170 */

static const char s_mv_missing[] = "mv: missing operand\r\n";                 /* ROM 0x77a9fc */
static const char s_mv_too_long[] = "mv: parameter too long\r\n";             /* ROM 0x76fdf4 */
static const char s_param1[] = "param1: %s";                                  /* ROM 0x78b90c */
static const char s_param1_c[] = "[prvCommand_filesystem]param1: %s";         /* ROM 0x75837c */
static const char s_param2[] = "param2: %s";                                  /* ROM 0x78b918 */
static const char s_param2_c[] = "[prvCommand_filesystem]param2: %s";         /* ROM 0x7583a0 */
static const char s_src[] = "src_path: %s";                                   /* ROM 0x788150 */
static const char s_src_c[] = "[prvCommand_filesystem]src_path: %s";          /* ROM 0x7583c4 */
static const char s_dst[] = "dst_path: %s";                                   /* ROM 0x788160 */
static const char s_dst_c[] = "[prvCommand_filesystem]dst_path: %s";          /* ROM 0x7583e8 */
static const char s_final[] = "final_dst_path: %s";                           /* ROM 0x782754 */
static const char s_final_c[] = "[prvCommand_filesystem]final_dst_path: %s";  /* ROM 0x741b7c */
static const char s_mv_bad_src[] = "mv: invalid source path\r\n";             /* ROM 0x76fe10 */
static const char s_mv_bad_dst[] = "mv: invalid destination path\r\n";        /* ROM 0x763c30 */
static const char s_mv_no_src[] = "mv: source file/directory not found\r\n";  /* ROM 0x74cbd4 */
static const char s_mv_file_exists[] = "mv: destination file already exists\r\n"; /* ROM 0x74cbfc */
static const char s_mv_exists[] = "mv: destination already exists\r\n";       /* ROM 0x75840c */
static const char s_mv_failed[] = "mv: move/rename failed\r\n";               /* ROM 0x76fe2c */

static const char s_md5_missing[] = "md5: missing file operand\r\n";          /* ROM 0x76fe48 */
static const char s_md5_bad_path[] = "md5: invalid file path\r\n";            /* ROM 0x76fe64 */
static const char s_md5_not_found[] = "md5: file not found\r\n";              /* ROM 0x77aa2c */
static const char s_md5_dir[] = "md5: cannot calculate hash for directory\r\n"; /* ROM 0x741ba8 */
static const char s_md5_open[] = "md5: cannot open file\r\n";                 /* ROM 0x77aa44 */
static const char s_md5_read[] = "md5: file read error\r\n";                  /* ROM 0x77aa5c */
static const char s_md5_head[] = "MD5(%s) = ";                                /* ROM 0x78b924 */
static const char s_hex2[] = "%02x";                                          /* ROM 0x78e14c */

static const char s_not_mounted[] = "Filesystem not mounted\r\n";             /* ROM 0x76fe80 */
static const char s_unknown[] = "unknown";                                    /* ROM 0x78e154 */
static const char s_err_io[] = "LFS_ERR_IO (-5) device IO";                   /* ROM 0x76fe9c */
static const char s_err_corrupt[] = "LFS_ERR_CORRUPT (-84) metadata/data link broken"; /* ROM 0x736d34 */
static const char s_err_noent[] = "LFS_ERR_NOENT (-2)";                       /* ROM 0x782768 */
static const char s_err_nomem[] = "LFS_ERR_NOMEM (-12)";                      /* ROM 0x78277c */
static const char s_err_inval[] = "LFS_ERR_INVAL (-22)";                      /* ROM 0x782790 */
static const char s_df_failed[] = "df: lfs_fs_size failed err=%ld (%s)\r\n";  /* ROM 0x74cc24 */
static const char s_df_head[] =
    "Filesystem     1K-blocks      Used Available Use%% Mounted on\r\n";     /* ROM 0x70df24 */
static const char s_df_row[] = "littlefs   %10lu %9lu %9lu %3d%% /\r\n";     /* ROM 0x74cc4c */
static const char s_df_summary[] = "=== Disk Space Summary ===\r\n";          /* ROM 0x763c50 */
static const char s_df_total[] = "Total Capacity:    %lu KB\r\n";             /* ROM 0x76feb8 */
static const char s_df_used[] = "Used Space:        %lu KB (%d%%)\r\n";       /* ROM 0x758430 */
static const char s_df_avail[] = "Available Space:   %lu KB\r\n";             /* ROM 0x76fed4 */
static const char s_df_rule[] = "==========================\r\n";             /* ROM 0x763c70 */
static const char s_df_block[] = "Block info: size=%lu, total=%lu, used=%ld"; /* ROM 0x741bd4 */
static const char s_df_block_c[] =
    "[prvCommand_filesystem]Block info: size=%lu, total=%lu, used=%ld";      /* ROM 0x7049ac */

#define G2_LFS ((void *)audio_file_lfs_context)

/* elog_i(...) as expanded in stock: level 4 extended log when flag bit 1 is
 * set, compressed copy when flag bit 0 or bit 2 is set. */
#define FS_LOG_I(fn, line, fmt, cfmt, id, ...)                                           \
    do {                                                                                 \
        if ((audio_log_flags() & 2u) != 0u)                                              \
            audio_log_extended(4u, s_tag, s_path, (fn), (line), (fmt), __VA_ARGS__);     \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)            \
            (void)compressed_log_output((id), (cfmt), (cfmt), __VA_ARGS__);              \
    } while (0)

/* strlen(parameter) + strlen(cwd) < limit, evaluated in stock order. */
static int fs_lengths_below(const char *name, uint32_t limit)
{
    uint32_t name_length = g2_log_module_length(name);
    uint32_t cwd_length = g2_log_module_length(g2_cli_cwd);
    return cwd_length + name_length < limit;
}

/* cwd + "/" (unless either side already supplies it) + name, into a zeroed
 * buffer of `size` bytes; the caller has already bounded the lengths. */
static char *fs_join_cwd(char *out, uint32_t size, const char *name)
{
    audio_uart_buffer_zero(out, size, 0u);
    audio_uart_checksum_copy(out, g2_cli_cwd, g2_log_module_length(g2_cli_cwd));
    if (g2_cli_cwd[g2_log_module_length(g2_cli_cwd) - 1u] != '/' && *name != '/')
        g2_strcat((uint8_t *)out, (const uint8_t *)s_slash);
    return (char *)g2_strcat((uint8_t *)out, (const uint8_t *)name);
}

/* Stock 0x57e898: "ls" - list the current directory, skipping "." and "..". */
int32_t prvCommand_ls_57e898(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length; (void)command;
    void *lfs = G2_LFS;
    g2_lfs_dir_t dir;
    g2_lfs_info_t info;
    int32_t rc;

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    rc = audio_file_lfs_dir_open_4cfc66(lfs, &dir, g2_cli_cwd);
    if (rc < 0)
        return rc;
    while ((rc = audio_file_lfs_dir_read_4cfd02(lfs, &dir, &info)) >= 0) {
        if (rc == 0) {
            (void)audio_file_lfs_dir_close_4cfcf8(lfs, &dir);
            return 0;
        }
        if (audio_uart_font_path_compare(info.name, s_dot) != 0 &&
            audio_uart_font_path_compare(info.name, s_dotdot) != 0)
            (void)g2_log_transport_queue_failure(s_ls_line, info.name,
                                                 info.type == LFS_TYPE_DIR ? s_slash : s_empty);
    }
    (void)audio_file_lfs_dir_close_4cfcf8(lfs, &dir);
    return rc;
}

/* Stock 0x57e920: "cat <file>" - stream a file to the console in 64-byte
 * reads. Paths are limited to 128 bytes including the cwd. */
int32_t prvCommand_cat_57e920(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length;
    int32_t param_length;
    uint8_t chunk[64];
    char path[128];
    g2_lfs_file_t file;

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    const char *name = freertos_cli_get_parameter_5848fc(command, 1u, &param_length);
    if (!fs_lengths_below(name, 0x81u)) {
        (void)g2_log_transport_queue_failure(s_error_path);
        return 0;
    }
    char *full = fs_join_cwd(path, sizeof path, name);
    void *lfs = G2_LFS;
    if (audio_file_lfs_open(lfs, &file, full, LFS_O_RDONLY) == 0) {
        for (;;) {
            audio_uart_buffer_zero(chunk, sizeof chunk, 0u);
            int32_t n = audio_file_lfs_read(lfs, &file, chunk, sizeof chunk);
            if (n < 0 || n == 0)
                break;
            for (int32_t i = 0; i < n; i++)
                cli_putchar_5415d8(chunk[i]);
        }
        (void)audio_file_lfs_close_4cfad0(lfs, &file);
    }
    return 0;
}

/* Stock 0x57ea0a: "rm <path>" - remove a file or empty directory; errors
 * are not reported. */
int32_t prvCommand_rm_57ea0a(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length;
    int32_t param_length;
    char path[256];

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    const char *name = freertos_cli_get_parameter_5848fc(command, 1u, &param_length);
    if (!fs_lengths_below(name, 0x101u)) {
        (void)g2_log_transport_queue_failure(s_error_path);
        return 0;
    }
    (void)audio_file_lfs_remove_4cfa76(G2_LFS, fs_join_cwd(path, sizeof path, name));
    return 0;
}

/* Stock 0x57eaa8: canonicalize an absolute or cwd-joined path: split on '/',
 * drop empty and "." parts, let ".." pop one part, rebuild as "/a/b".
 * Returns 0, or -1 when the result is 255 bytes or longer. When the
 * filesystem is not ready it returns 0 without touching `out`. */
int32_t fs_normalize_path_57eaa8(char *out, const char *in)
{
    char buffer[256];
    char *parts[255];
    int32_t count = 0;

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    (void)audio_settings_copy_text(buffer, in, 0xffu);
    buffer[0xfe] = '\0';
    char *token = g2_strtok_594884(buffer, s_slash);
    while (token != NULL && count < 0xff) {
        if (g2_log_module_length(token) == 0u) {
            token = g2_strtok_594884(NULL, s_slash);
            continue;
        }
        if (audio_uart_font_path_compare(token, s_dot) != 0) {
            if (audio_uart_font_path_compare(token, s_dotdot) == 0) {
                if (count > 0)
                    count--;
            } else {
                parts[count++] = token;
            }
        }
        token = g2_strtok_594884(NULL, s_slash);
    }
    *out = '\0';
    g2_strcat((uint8_t *)out, (const uint8_t *)s_slash);
    for (int32_t i = 0; i < count; i++) {
        g2_strcat((uint8_t *)out, (const uint8_t *)parts[i]);
        if (i != count - 1)
            g2_strcat((uint8_t *)out, (const uint8_t *)s_slash);
    }
    if (count == 0)
        (void)g2_strcpy_48d540(out, s_slash);
    return g2_log_module_length(out) < 0xffu ? 0 : -1;
}

/* Stock 0x57eb94: "cd <dir>" - change the cwd after the normalized target
 * opens as a directory. strlen() runs on the parameter before its NULL
 * check, as in stock. */
int32_t prvCommand_cd_57eb94(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length;
    int32_t param_length;
    char path[256];
    char normalized[256];
    g2_lfs_dir_t dir;

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    const char *name = freertos_cli_get_parameter_5848fc(command, 1u, &param_length);
    if (!fs_lengths_below(name, 0x100u)) {
        (void)g2_log_transport_queue_failure(s_error_path);
        return 0;
    }
    audio_uart_buffer_zero(path, 0xffu, 0u);
    if (name == NULL || g2_log_module_length(name) > 0xfeu) {
        (void)g2_log_transport_queue_failure(s_invalid_path);
        return 0;
    }
    if (*name == '/')
        (void)g2_audio_dump_snprintf(path, 0xffu, s_percent_s, name);
    else
        (void)g2_audio_dump_snprintf(path, 0xffu, s_join, g2_cli_cwd, name);
    if (fs_normalize_path_57eaa8(normalized, path) != 0) {
        (void)g2_log_transport_queue_failure(s_invalid_path);
        return 0;
    }
    void *lfs = G2_LFS;
    if (audio_file_lfs_dir_open_4cfc66(lfs, &dir, normalized) != 0) {
        (void)g2_log_transport_queue_failure(s_invalid_path);
        return 0;
    }
    (void)audio_file_lfs_dir_close_4cfcf8(lfs, &dir);
    (void)audio_settings_copy_text(g2_cli_cwd, normalized, 0x80u);
    g2_cli_cwd[0x7f] = '\0';
    return 0;
}

/* Stock 0x57ec7c: "mkdir <dir>". */
int32_t prvCommand_mkdir_57ec7c(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length;
    int32_t param_length;
    char path[256];

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    const char *name = freertos_cli_get_parameter_5848fc(command, 1u, &param_length);
    if (!fs_lengths_below(name, 0x101u)) {
        (void)g2_log_transport_queue_failure(s_error_path);
        return 0;
    }
    if (audio_file_lfs_mkdir_4cfc5c(G2_LFS, fs_join_cwd(path, sizeof path, name)) != 0)
        (void)g2_log_transport_queue_failure(s_mkdir_failed);
    return 0;
}

/* Stock 0x57ed26: "touch <file>" - create with O_WRONLY|O_CREAT and close.
 * The failure text is the mkdir message, as in stock. */
int32_t prvCommand_touch_57ed26(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length;
    int32_t param_length;
    char path[256];
    g2_lfs_file_t file;

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    const char *name = freertos_cli_get_parameter_5848fc(command, 1u, &param_length);
    if (!fs_lengths_below(name, 0x101u)) {
        (void)g2_log_transport_queue_failure(s_error_path);
        return 0;
    }
    char *full = fs_join_cwd(path, sizeof path, name);
    void *lfs = G2_LFS;
    if (audio_file_lfs_open(lfs, &file, full, LFS_O_WRONLY_CREAT) == 0)
        (void)audio_file_lfs_close_4cfad0(lfs, &file);
    else
        (void)g2_log_transport_queue_failure(s_mkdir_failed);
    return 0;
}

/* Stock 0x57ede2: "pwd". */
int32_t prvCommand_pwd_57ede2(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length; (void)command;
    if (audio_file_ready_200746a8 == 1u)
        (void)g2_log_transport_queue_failure(s_line, g2_cli_cwd);
    return 0;
}

/* Absolute operand copied (at most 254 bytes), relative operand appended to
 * the cwd; used twice by mv. */
static void fs_mv_operand(char *out, const char *operand)
{
    audio_uart_buffer_zero(out, 0xffu, 0u);
    if (operand[0] == '/') {
        (void)audio_settings_copy_text(out, operand, 0xfeu);
        return;
    }
    (void)g2_strcpy_48d540(out, g2_cli_cwd);
    if (g2_cli_cwd[g2_log_module_length(g2_cli_cwd) - 1u] != '/' && operand[0] != '/')
        g2_strcat((uint8_t *)out, (const uint8_t *)s_slash);
    g2_strcat((uint8_t *)out, (const uint8_t *)operand);
}

/* Stock 0x57ee0c: "mv <src> <dst>" - operands are split from the raw command
 * string; a directory destination receives the source basename. */
int32_t prvCommand_mv_57ee0c(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length;
    char param1[256], param2[256];
    char src[256], dst[256];
    char src_norm[256], dst_norm[256];
    char final_dst[256];
    g2_lfs_info_t src_info, dst_info;

    if (audio_file_ready_200746a8 != 1u)
        return 0;

    const char *p = command;
    while (*p != '\0' && *p != ' ')
        p++;
    while (*p != '\0' && *p == ' ')
        p++;
    const char *first = p;
    if (*first == '\0') {
        (void)g2_log_transport_queue_failure(s_mv_missing);
        return 0;
    }
    const char *first_end = first;
    while (*first_end != '\0' && *first_end != ' ')
        first_end++;
    const char *second = first_end;
    while (*second != '\0' && *second == ' ')
        second++;
    if (*second == '\0') {
        (void)g2_log_transport_queue_failure(s_mv_missing);
        return 0;
    }
    const char *second_end = second;
    while (*second_end != '\0' && *second_end != ' ')
        second_end++;

    int32_t len1 = (int32_t)(first_end - first);
    int32_t len2 = (int32_t)(second_end - second);
    if (len1 >= 0xff || len2 >= 0xff) {
        (void)g2_log_transport_queue_failure(s_mv_too_long);
        return 0;
    }
    (void)audio_settings_copy_text(param1, first, (uint32_t)len1);
    param1[len1] = '\0';
    (void)audio_settings_copy_text(param2, second, (uint32_t)len2);
    param2[len2] = '\0';
    FS_LOG_I(s_fn_mv, 0x26du, s_param1, s_param1_c, 0x10400000u, param1);
    FS_LOG_I(s_fn_mv, 0x26eu, s_param2, s_param2_c, 0x10400000u, param2);

    fs_mv_operand(src, param1);
    fs_mv_operand(dst, param2);
    FS_LOG_I(s_fn_mv, 0x28eu, s_src, s_src_c, 0x10400000u, src);
    FS_LOG_I(s_fn_mv, 0x28fu, s_dst, s_dst_c, 0x10400000u, dst);

    if (fs_normalize_path_57eaa8(src_norm, src) != 0) {
        (void)g2_log_transport_queue_failure(s_mv_bad_src);
        return 0;
    }
    if (fs_normalize_path_57eaa8(dst_norm, dst) != 0) {
        (void)g2_log_transport_queue_failure(s_mv_bad_dst);
        return 0;
    }
    void *lfs = G2_LFS;
    if (lfs_stat_4cfa8a(lfs, src_norm, &src_info) != 0) {
        (void)g2_log_transport_queue_failure(s_mv_no_src);
        return 0;
    }
    int32_t dst_rc = lfs_stat_4cfa8a(lfs, dst_norm, &dst_info);
    audio_uart_buffer_zero(final_dst, 0xffu, 0u);
    if (dst_rc == 0) {
        if (dst_info.type != LFS_TYPE_DIR) {
            (void)g2_log_transport_queue_failure(s_mv_file_exists);
            return 0;
        }
        (void)g2_strcpy_48d540(final_dst, dst_norm);
        if (final_dst[g2_log_module_length(final_dst) - 1u] != '/')
            g2_strcat((uint8_t *)final_dst, (const uint8_t *)s_slash);
        const char *slash = (const char *)g2_strrchr((const uint8_t *)src_norm, '/');
        g2_strcat((uint8_t *)final_dst, (const uint8_t *)(slash == NULL ? src_norm : slash + 1));
    } else {
        (void)g2_strcpy_48d540(final_dst, dst_norm);
    }
    FS_LOG_I(s_fn_mv, 0x2c9u, s_final, s_final_c, 0x10400000u, final_dst);
    if (lfs_stat_4cfa8a(lfs, final_dst, &dst_info) == 0)
        (void)g2_log_transport_queue_failure(s_mv_exists);
    else if (lfs_rename_4cfa80(lfs, src_norm, final_dst) != 0)
        (void)g2_log_transport_queue_failure(s_mv_failed);
    return 0;
}

/* Stock 0x57f274: "md5 <file>" - print the MD5 digest of a regular file. */
int32_t prvCommand_md5_57f274(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length;
    int32_t param_length;
    struct {
        uint8_t digest[16]; /* +0x00 */
        uint8_t chunk[64];  /* +0x10 */
    } io;
    g2_md5_ctx_t ctx;
    g2_lfs_file_t file;
    g2_lfs_info_t info;
    char normalized[256];
    char path[256];

    if (audio_file_ready_200746a8 != 1u)
        return 0;
    const char *name = freertos_cli_get_parameter_5848fc(command, 1u, &param_length);
    if (name == NULL) {
        (void)g2_log_transport_queue_failure(s_md5_missing);
        return 0;
    }
    audio_uart_buffer_zero(path, 0xffu, 0u);
    if (*name == '/')
        (void)audio_settings_copy_text(path, name, 0xfeu);
    else
        (void)g2_audio_dump_snprintf(path, 0xffu, s_join, g2_cli_cwd, name);
    if (fs_normalize_path_57eaa8(normalized, path) != 0) {
        (void)g2_log_transport_queue_failure(s_md5_bad_path);
        return 0;
    }
    void *lfs = G2_LFS;
    if (lfs_stat_4cfa8a(lfs, normalized, &info) != 0) {
        (void)g2_log_transport_queue_failure(s_md5_not_found);
        return 0;
    }
    if (info.type == LFS_TYPE_DIR) {
        (void)g2_log_transport_queue_failure(s_md5_dir);
        return 0;
    }
    if (audio_file_lfs_open(lfs, &file, normalized, LFS_O_RDONLY) != 0) {
        (void)g2_log_transport_queue_failure(s_md5_open);
        return 0;
    }
    md5_init_59544e(&ctx);
    for (;;) {
        audio_uart_buffer_zero(io.chunk, sizeof io.chunk, 0u);
        int32_t n = audio_file_lfs_read(lfs, &file, io.chunk, sizeof io.chunk);
        if (n < 0)
            break;
        if (n == 0) {
            md5_final_595608(io.digest, &ctx);
            (void)g2_log_transport_queue_failure(s_md5_head, normalized);
            for (int32_t i = 0; i < 16; i++)
                (void)g2_log_transport_queue_failure(s_hex2, io.digest[i]);
            (void)g2_log_transport_queue_failure(s_crlf);
            (void)audio_file_lfs_close_4cfad0(lfs, &file);
            return 0;
        }
        md5_update_595578(&ctx, io.chunk, (uint32_t)n);
    }
    (void)g2_log_transport_queue_failure(s_md5_read);
    (void)audio_file_lfs_close_4cfad0(lfs, &file);
    return 0;
}

/* Stock 0x57f3cc: "df" - littlefs usage from lfs_fs_size() and the config
 * geometry, rounded up to KiB. */
int32_t prvCommand_df_57f3cc(char *write_buffer, uint32_t write_length, const char *command)
{
    (void)write_buffer; (void)write_length; (void)command;
    void *lfs = G2_LFS;

    if (audio_file_ready_200746a8 != 1u) {
        (void)g2_log_transport_queue_failure(s_not_mounted);
        return 0;
    }
    int32_t used_blocks = lfs_fs_size_4cfd0c(lfs);
    if (used_blocks < 0) {
        const char *text;
        if (used_blocks == -84)
            text = s_err_corrupt;
        else if (used_blocks == -22)
            text = s_err_inval;
        else if (used_blocks == -12)
            text = s_err_nomem;
        else if (used_blocks == -5)
            text = s_err_io;
        else if (used_blocks == -2)
            text = s_err_noent;
        else
            text = s_unknown;
        (void)g2_log_transport_queue_failure(s_df_failed, used_blocks, text);
        return 0;
    }
    const g2_lfs_config_view_t *cfg =
        *(const g2_lfs_config_view_t *const *)(const void *)(audio_file_lfs_context + 0x68u);
    uint32_t block_size = cfg->block_size;
    uint32_t block_count = cfg->block_count;
    uint32_t total = block_size * block_count;
    uint32_t used = block_size * (uint32_t)used_blocks;
    uint32_t percent = total == 0u ? 0u : (used * 100u) / total;

    (void)g2_log_transport_queue_failure(s_df_head);
    uint32_t total_kb = (total + 0x3ffu) >> 10;
    uint32_t used_kb = (used + 0x3ffu) >> 10;
    uint32_t avail_kb = (total - used + 0x3ffu) >> 10;
    (void)g2_log_transport_queue_failure(s_df_row, total_kb, used_kb, avail_kb, percent);
    (void)g2_log_transport_queue_failure(s_crlf);
    (void)g2_log_transport_queue_failure(s_df_summary);
    (void)g2_log_transport_queue_failure(s_df_total, total_kb);
    (void)g2_log_transport_queue_failure(s_df_used, used_kb, percent);
    (void)g2_log_transport_queue_failure(s_df_avail, avail_kb);
    (void)g2_log_transport_queue_failure(s_df_rule);
    FS_LOG_I(s_fn_df, 899u, s_df_block, s_df_block_c, 0x10c00000u,
             block_size, block_count, used_blocks);
    return 0;
}

/* Stock 0x57f530: tlsf_walk_pool() walker for the memory command at
 * 0x57f550: free/used byte totals, block count and free-block count. */
void cli_heap_walker_57f530(void *block, uint32_t size, int32_t used, void *user)
{
    g2_heap_walk_totals_t *totals = (g2_heap_walk_totals_t *)user;
    (void)block;
    if (used != 0) {
        totals->used_bytes += size;
    } else {
        totals->free_bytes += size;
        totals->free_blocks++;
    }
    totals->blocks++;
}
