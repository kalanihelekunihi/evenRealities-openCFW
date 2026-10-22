/* Logger settings /log helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\logger\logger_setting.c. */
#ifndef G2_LOGGER_SETTING_H
#define G2_LOGGER_SETTING_H

#include <stdint.h>

#define G2_LOGGER_FILE_LIST_MAX 20u

/* One /log inventory row. */
typedef struct {
    char name[0x20];       /* +0x00 truncated to 31 chars, name[0x1f] = 0 */
    uint32_t size;         /* +0x20 bytes, 0 for non-regular entries */
    uint8_t type;          /* +0x24 directory-entry type (8 regular, 4 directory) */
    uint8_t pad_25[3];
} g2_logger_file_entry_t;

/* /log inventory filled by scan_log_files (RAM 0x2037b098, cleared as 0x328 bytes). */
typedef struct {
    g2_logger_file_entry_t files[G2_LOGGER_FILE_LIST_MAX]; /* +0x000 */
    uint32_t count;        /* +0x320 */
    uint32_t total_size;   /* +0x324 sum of regular-file sizes */
} g2_logger_file_list_t;

/* File size by seek-to-end, 0 when the file cannot be opened or tell fails. */
int32_t logger_file_size(const char *path);
/* Removes regular files directly in dir; returns the count or -1 if dir cannot be opened. */
int32_t delete_all_files_in_dir(const char *dir);
/* Rebuilds the /log inventory (skips compress_manager.bin); 0 ok, -1 no /log. */
int32_t scan_log_files(void);

#endif
