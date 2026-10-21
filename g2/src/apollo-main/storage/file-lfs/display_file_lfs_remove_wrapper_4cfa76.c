/* Stock Main 0x4cfa76: public remove entry passes a zero option to 0x4ce4dc. */
#include <stdint.h>

extern int32_t audio_file_lfs_remove_core_4ce4dc(void *, const char *, uint32_t);

int32_t audio_file_lfs_remove_4cfa76(void *filesystem, const char *path) {
    return audio_file_lfs_remove_core_4ce4dc(filesystem, path, 0u);
}
