/* AT^RM / AT^LS / AT^MKDIR file-system commands, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_fs.c.
 * Native 0x5a5530..0x5a56cf; literal pool 0x5a56d0..0x5a571f.
 *
 * All commands need the file system mounted (audio_file_ready_200746a8 == 1)
 * and return 0 otherwise. AT^LS prints every entry below a path
 * recursively: "D <path>" for directories, "F <path>\t size:<n>(<n/1024>KB)"
 * for files, pausing 30 ms per entry so the UART can drain. */
#include <stdint.h>
#include "g2_at_core.h"

#define FILE_DIRENT_TYPE_DIR 4u
#define FILE_SEEK_END 2
#define AT_LS_PATH_SIZE 0x84u     /* stack buffer; 0x81 bytes cleared */
#define AT_LS_ENTRY_DELAY 30u

/* file_readdir result (shared 257-byte dirent). */
typedef struct {
    char name[0x100];            /* +0x000 */
    uint8_t type;                /* +0x100 FILE_DIRENT_TYPE_* */
} g2_file_dirent_t;

extern uint32_t audio_file_ready_200746a8;        /* RAM 0x200746a8, 1 once mounted */
extern uint8_t audio_file_lfs_context[];          /* RAM 0x20071ac8, lfs_t */
extern int32_t file_remove(const char *path);     /* 0x47498c */
extern void *file_opendir(const char *path);      /* 0x474b02 */
extern const g2_file_dirent_t *file_readdir(void *dir); /* 0x474bb8 */
extern int32_t file_closedir(void *dir);          /* 0x474c66 */
extern void *file_open(const char *path, const char *mode); /* 0x474550 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin); /* 0x474814 */
extern int32_t file_tell(void *file);             /* 0x474870 */
extern int32_t file_close(void *file);            /* 0x4745f4 */
extern int32_t audio_file_lfs_mkdir_4cfc5c(void *lfs, const char *path);
extern int32_t string_compare_46cacc(const char *a, const char *b); /* strcmp */
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern uint8_t *g2_strcat(uint8_t *dst, const uint8_t *src); /* 0x567c80 strcat */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t osDelay(uint32_t ticks);           /* 0x449376 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "at.fs"; /* ROM 0x78cbd4 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\eAT\\at_fs.c"; /* ROM 0x700854 */
static const char fn_rm[] = "_atRM"; /* ROM 0x78cbcc */
static const char s_rm[] = "RM %s"; /* ROM 0x78cbdc */
static const char c_rm[] = "[at.fs]RM %s"; /* ROM 0x785160 */
static const char o_rm_ok[] = "RM+OK\r\n"; /* ROM 0x78cbe4 */
static const char o_rm_err[] = "^RM: remove file[%s] error(%d)\r\n"; /* ROM 0x752394 */
static const char k_dot[] = "."; /* ROM 0x5a56d0 */
static const char k_dotdot[] = ".."; /* ROM 0x5a56d4 */
static const char f_dir_prefix[] = "%s/"; /* ROM 0x5a56d8 */
static const char k_read[] = "r"; /* ROM 0x5a56dc */
static const char o_opendir_fail[] = "opendir fail, path: %s\r\n"; /* ROM 0x769b30 */
static const char o_dir[] = "D %s\r\n"; /* ROM 0x78cbec */
static const char o_file[] = "F %s\t size:%ld(%ldKB)\r\n"; /* ROM 0x7755fc */
static const char o_ls_ok[] = "LS+OK\r\n"; /* ROM 0x78cbf4 */
static const char o_ls_err[] = "LS+ERR\r\n"; /* ROM 0x78a37c */
static const char o_mkdir_ok[] = "MKDIR+OK\r\n"; /* ROM 0x78a388 */
static const char o_mkdir_err[] = "Directory creation failed %s\r\n"; /* ROM 0x75e230 */

int32_t _atRM(const char *arg1, const char *arg2)
{
    (void)arg2;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_rm, 0x13u, s_rm, arg1);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, c_rm, c_rm, arg1);
    if (audio_file_ready_200746a8 != 1u)
        return 0;
    int32_t err = file_remove(arg1);
    if (err != 0) {
        at_core_output(o_rm_err, arg1, err);
        return 0;
    }
    at_core_output(o_rm_ok);
    return 1;
}

uint8_t atFsListRecursive(const char *path)
{
    if (audio_file_ready_200746a8 != 1u)
        return 0u;
    void *dir = file_opendir(path);
    if (dir == 0) {
        at_core_output(o_opendir_fail, path);
        return 0u;
    }

    char full[AT_LS_PATH_SIZE];
    (void)aeabi_memset_43c0e4(full, 0x81u, 0);
    const g2_file_dirent_t *entry;
    while ((entry = file_readdir(dir)) != 0) {
        if (string_compare_46cacc(entry->name, k_dot) == 0 || string_compare_46cacc(entry->name, k_dotdot) == 0)
            continue;
        (void)audio_ble_format_to_buffer(full, f_dir_prefix, path);
        (void)g2_strcat((uint8_t *)full, (const uint8_t *)entry->name);
        if (entry->type == FILE_DIRENT_TYPE_DIR) {
            (void)osDelay(AT_LS_ENTRY_DELAY);
            at_core_output(o_dir, full);
            (void)atFsListRecursive(full);
        } else {
            (void)osDelay(AT_LS_ENTRY_DELAY);
            void *file = file_open(full, k_read);
            int32_t size = 0;
            if (file != 0) {
                (void)file_seek(file, 0, FILE_SEEK_END);
                size = file_tell(file);
                (void)file_close(file);
            }
            at_core_output(o_file, full, size, size / 1024);
        }
    }
    (void)file_closedir(dir);
    return 1u;
}

int32_t atLsHandler(const char *arg1, const char *arg2)
{
    (void)arg2;
    uint8_t ok = atFsListRecursive(arg1);
    (void)osDelay(AT_LS_ENTRY_DELAY);
    at_core_output(ok ? o_ls_ok : o_ls_err);
    return 1;
}

int32_t atMkdirHandler(const char *arg1, const char *arg2)
{
    (void)arg2;
    if (audio_file_ready_200746a8 != 1u)
        return 0;
    if (audio_file_lfs_mkdir_4cfc5c(audio_file_lfs_context, arg1) != 0)
        at_core_output(o_mkdir_err, arg1);
    else
        at_core_output(o_mkdir_ok);
    return 1;
}
