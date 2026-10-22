/* Logger settings /log file helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\logger\logger_setting.c
 * (log tag "logger.setting").
 * Native rows: logger_file_size 0x458e9c..0x458ed2, delete_all_files_in_dir
 * 0x458ed2..0x45904a, scan_log_files 0x459050..0x459264. Inline literals
 * "r" 0x45904c, "." 0x4591fc, ".." 0x459200; pool 0x459278..0x4592dc and
 * 0x459d58 (file-list address).
 *
 * The rest of this source (loggerSetting_set_ble_transmit 0x458df0,
 * loggerSetting_ble_transmit_enabled 0x458e32, loggerSetting_cancel_ble_transmit
 * 0x458e48, loggerSetting_common_data_handler 0x4592dc) is not written here. */
#include <stdint.h>
#include <stddef.h>
#include "g2_logger_setting.h"

_Static_assert(sizeof(g2_logger_file_entry_t) == 0x28u, "stock /log row is 0x28 bytes");
_Static_assert(sizeof(g2_logger_file_list_t) == 0x328u, "stock /log inventory is 0x328 bytes");

/* Directory entry returned by the file-directory facade 0x474bb8. */
typedef struct {
    char name[0x100];      /* +0x000 */
    uint8_t type;          /* +0x100 8 regular file, 4 directory */
} g2_file_dirent_t;

#define LOGGER_DT_REG 8u
#define LOGGER_PATH_MAX 0x140u

extern g2_logger_file_list_t g2_logger_file_list;   /* RAM 0x2037b098 */

extern void *file_open(const char *path, const char *mode);      /* 0x474550 */
extern int32_t file_close(void *file);                           /* 0x4745f4 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin); /* 0x474814 */
extern int32_t file_tell(void *file);                            /* 0x474870 */
extern int32_t file_remove(const char *path);                    /* 0x47498c */
extern void *audio_tracepoint_dir_open_474b02(const char *path); /* file_opendir */
extern g2_file_dirent_t *audio_tracepoint_dir_read_474bb8(void *dir); /* file_readdir */
extern int32_t audio_tracepoint_dir_close_474c66(void *dir);     /* file_closedir */
extern int32_t audio_uart_font_path_compare(const char *a, const char *b); /* 0x46cacc strcmp */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 memset */
extern uint32_t audio_log_flags(void);                           /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "logger.setting"; /* ROM 0x786220 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\logger\\logger_setting.c"; /* ROM 0x7034f4 */
static const char fn_delete[] = "delete_all_files_in_dir"; /* ROM 0x777dbc */
static const char fn_scan[] = "scan_log_files";            /* ROM 0x786230 */
static const char mode_read[] = "r";                       /* ROM 0x45904c */
static const char name_dot[] = ".";                        /* ROM 0x4591fc */
static const char name_dotdot[] = "..";                    /* ROM 0x459200 */
static const char dir_log[] = "/log";                      /* ROM 0x78d81c */
static const char name_compress_manager[] = "compress_manager.bin"; /* ROM 0x777dd4 */
static const char fmt_dir_file[] = "%s/%s";                /* ROM 0x78d814 */
static const char fmt_log_file[] = "/log/%s";              /* ROM 0x78d824 */

static const char s_opendir_failed[] = "Failed to open directory: %s"; /* 0x760590 */
static const char c_opendir_failed[] = "[logger.setting]Failed to open directory: %s"; /* 0x734c04 */
static const char s_deleted[] = "Deleted file: %s"; /* 0x77f928 */
static const char c_deleted[] = "[logger.setting]Deleted file: %s"; /* 0x755004 */
static const char s_delete_failed[] = "Failed to delete file: %s"; /* 0x76c4c0 */
static const char c_delete_failed[] = "[logger.setting]Failed to delete file: %s"; /* 0x73f2c0 */
static const char s_deleted_count[] = "Deleted %d files from %s"; /* 0x76c4dc */
static const char c_deleted_count[] = "[logger.setting]Deleted %d files from %s"; /* 0x73f2ec */
static const char s_log_dir_failed[] = "Failed to open /log directory"; /* 0x7605b0 */
static const char c_log_dir_failed[] = "[logger.setting]Failed to open /log directory"; /* 0x734c34 */
static const char s_skip_manager[] = "compress manager log not to send"; /* 0x755028 */
static const char c_skip_manager[] = "[logger.setting]compress manager log not to send"; /* 0x72a258 */
static const char s_found[] = "Found: %s, size: %d bytes, type: %d"; /* 0x75504c */
static const char c_found[] = "[logger.setting]Found: %s, size: %d bytes, type: %d"; /* 0x72a28c */
static const char s_total[] = "Total %d files found in /log, total size: %d bytes"; /* 0x72a2c0 */
static const char c_total[] = "[logger.setting]Total %d files found in /log, total size: %d bytes"; /* 0x703538 */

/* compress_log_output record code: level << 26 | argument count << 22. */
#define LOGGER_LOG_CODE(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

#define LOGGER_LOG(fn, level, line, nargs, plain, compact, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), (plain), ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output(LOGGER_LOG_CODE((level), (nargs)), (compact), (compact), ##__VA_ARGS__); \
} while (0)

int32_t logger_file_size(const char *path)
{
    void *file;
    int32_t size;

    file = file_open(path, mode_read);
    if (file == NULL)
        return 0;
    (void)file_seek(file, 0, 2);
    size = file_tell(file);
    (void)file_close(file);
    if (size < 0)
        size = 0;
    return size;
}

int32_t delete_all_files_in_dir(const char *dir)
{
    char path[LOGGER_PATH_MAX];
    g2_file_dirent_t *entry;
    void *handle;
    int32_t deleted;

    handle = audio_tracepoint_dir_open_474b02(dir);
    if (handle == NULL) {
        LOGGER_LOG(fn_delete, 1u, 0x7au, 1u, s_opendir_failed, c_opendir_failed, dir);
        return -1;
    }
    deleted = 0;
    while ((entry = audio_tracepoint_dir_read_474bb8(handle)) != NULL) {
        if (audio_uart_font_path_compare(entry->name, name_dot) == 0 ||
            audio_uart_font_path_compare(entry->name, name_dotdot) == 0 ||
            entry->type != LOGGER_DT_REG)
            continue;
        (void)g2_audio_dump_snprintf(path, sizeof(path), fmt_dir_file, dir, entry->name);
        if (file_remove(path) == 0) {
            LOGGER_LOG(fn_delete, 4u, 0x8fu, 1u, s_deleted, c_deleted, path);
            deleted++;
        } else {
            LOGGER_LOG(fn_delete, 1u, 0x92u, 1u, s_delete_failed, c_delete_failed, path);
        }
    }
    (void)audio_tracepoint_dir_close_474c66(handle);
    LOGGER_LOG(fn_delete, 4u, 0x98u, 2u, s_deleted_count, c_deleted_count, deleted, dir);
    return deleted;
}

int32_t scan_log_files(void)
{
    g2_logger_file_list_t *list = &g2_logger_file_list;
    g2_logger_file_entry_t *row;
    char path[LOGGER_PATH_MAX];
    g2_file_dirent_t *entry;
    void *handle;
    uint32_t count;

    audio_uart_buffer_zero(list, sizeof(*list), 0u);
    handle = audio_tracepoint_dir_open_474b02(dir_log);
    if (handle == NULL) {
        LOGGER_LOG(fn_scan, 1u, 0xa8u, 0u, s_log_dir_failed, c_log_dir_failed);
        return -1;
    }
    count = 0u;
    /* readdir runs before the 20-row bound is tested. */
    while ((entry = audio_tracepoint_dir_read_474bb8(handle)) != NULL &&
           count < G2_LOGGER_FILE_LIST_MAX) {
        if (audio_uart_font_path_compare(entry->name, name_dot) == 0 ||
            audio_uart_font_path_compare(entry->name, name_dotdot) == 0)
            continue;
        if (audio_uart_font_path_compare(entry->name, name_compress_manager) == 0) {
            LOGGER_LOG(fn_scan, 4u, 0xb7u, 0u, s_skip_manager, c_skip_manager);
            continue;
        }
        row = &list->files[count];
        (void)audio_settings_copy_text(row->name, entry->name, 0x1fu);
        row->name[0x1f] = '\0';
        row->type = entry->type;
        if (entry->type == LOGGER_DT_REG) {
            (void)g2_audio_dump_snprintf(path, sizeof(path), fmt_log_file, entry->name);
            row->size = (uint32_t)logger_file_size(path);
            list->total_size += row->size;
        } else {
            row->size = 0u;
        }
        count++;
        LOGGER_LOG(fn_scan, 4u, 0xd1u, 3u, s_found, c_found,
                   entry->name, list->files[count - 1u].size, entry->type);
    }
    list->count = count;
    (void)audio_tracepoint_dir_close_474c66(handle);
    LOGGER_LOG(fn_scan, 4u, 0xd8u, 2u, s_total, c_total, list->count, list->total_size);
    return 0;
}
