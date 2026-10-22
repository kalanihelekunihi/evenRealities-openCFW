/* LittleFS stdio-style facade (file runtime), native 0x4748b4..0x47490f and 0x474a02..0x474a75
 * (shared literal pool 0x474e40..0x474e9f). Siblings: file_close 0x4745f4
 * (storage/file/file-close.c), file_read/seek/tell 0x474634/0x474814/0x474870
 * (storage/file-api/display_file_api.c), mkdir 0x474a76 (tracepoint_storage_mkdir_474a76.c).
 *
 * Every call serialises on the file-API mutex (RAM 0x200748f4, 1000-tick timeout) and maps
 * failures to newlib errno values: EIO 5, EBADF 9, EBUSY 16, EINVAL 22. */
#include <stdint.h>
#include <stddef.h>

#define FILE_MUTEX_TIMEOUT 1000u
enum { FILE_EIO = 5, FILE_EBADF = 9, FILE_EBUSY = 16, FILE_EINVAL = 22 };

/* 96-byte FILE record: owning lfs_t at +0, lfs_file_t from +4. */
typedef struct {
    void *lfs;         /* +0x0 */
    uint8_t file[92];  /* +0x4 lfs_file_t */
} g2_file_t;
_Static_assert(sizeof(g2_file_t) == 96u, "stock FILE record is 96 bytes");

extern uint32_t audio_file_ready_200746a8;  /* RAM 0x200746a8, 1 once LittleFS is mounted */
extern void *audio_file_api_mutex;          /* RAM 0x200748f4 */
extern uint8_t audio_file_lfs_context[];    /* RAM 0x20071ac8 lfs_t */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                   /* 0x44981c */
extern int32_t *audio_file_errno_location_439cc4(void);
extern int32_t lfs_file_size_4cfc2e(void *lfs, void *file);
extern int32_t lfs_rename_4cfa80(void *lfs, const char *old_path, const char *new_path);

int32_t file_size(g2_file_t *stream)
{
    if (stream == NULL) {
        *audio_file_errno_location_439cc4() = FILE_EBADF;
        return -1;
    }
    if (osMutexAcquire(audio_file_api_mutex, FILE_MUTEX_TIMEOUT) != 0) {
        *audio_file_errno_location_439cc4() = FILE_EBUSY;
        return -1;
    }
    int32_t size = lfs_file_size_4cfc2e(stream->lfs, stream->file);
    (void)osMutexRelease(audio_file_api_mutex);
    if (size < 0) {
        *audio_file_errno_location_439cc4() = FILE_EIO;
        return -1;
    }
    return size;
}

/* Silently succeeds (returns 0) while the file system is not mounted. */
int32_t file_rename(const char *old_path, const char *new_path)
{
    if (audio_file_ready_200746a8 != 1u)
        return 0;
    if (old_path == NULL || new_path == NULL) {
        *audio_file_errno_location_439cc4() = FILE_EINVAL;
        return -1;
    }
    if (osMutexAcquire(audio_file_api_mutex, FILE_MUTEX_TIMEOUT) != 0) {
        *audio_file_errno_location_439cc4() = FILE_EBUSY;
        return -1;
    }
    int32_t status = lfs_rename_4cfa80(audio_file_lfs_context, old_path, new_path);
    (void)osMutexRelease(audio_file_api_mutex);
    if (status < 0) {
        *audio_file_errno_location_439cc4() = FILE_EIO;
        return -1;
    }
    return 0;
}
