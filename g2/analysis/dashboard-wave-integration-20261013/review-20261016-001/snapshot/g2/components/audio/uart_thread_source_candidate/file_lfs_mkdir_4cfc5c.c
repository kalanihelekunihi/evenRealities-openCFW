/* Stock Main 0x4cfc5c: public LittleFS mkdir wrapper. */
#include <stdint.h>

extern int32_t audio_file_lfs_mkdir_core_4cd3aa(void *,const char *,uint32_t);

int32_t audio_file_lfs_mkdir_4cfc5c(void *filesystem,const char *path) {
    return audio_file_lfs_mkdir_core_4cd3aa(filesystem,path,0u);
}
