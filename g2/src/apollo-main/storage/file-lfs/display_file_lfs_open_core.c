/* Native lfs_file_open 0x4cdcc8 passes the exact 16-byte all-zero
 * default lfs_file_config at ROM0x78ab8c to lfs_file_opencfg. */
#include <stdint.h>
extern int32_t audio_file_lfs_opencfg(void *,void *,const char *,uint32_t,const void *); /* 0x4cda36 */
static const uint32_t default_config[4]={0u,0u,0u,0u};
int32_t audio_file_lfs_open_core(void *filesystem,void *file,const char *path,uint32_t flags) {
    return audio_file_lfs_opencfg(filesystem,file,path,flags,default_config);
}
