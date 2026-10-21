/* Stock Main file unlink facade at 0x47498c. */
#include <stdint.h>
extern int32_t *audio_file_errno_location_439cc4(void);
extern int32_t audio_file_mutex_acquire(void *,uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_file_lfs_remove_4cfa76(void *,const char *);
extern void *audio_file_api_mutex;
extern uint8_t audio_file_lfs_context[];
uint32_t audio_file_ready_200746a8
    __attribute__((section(".bss.opencfw.file.ready"),aligned(4),used));
_Static_assert(sizeof(audio_file_ready_200746a8)==4u,"stock file-ready cell");
int32_t audio_tracepoint_storage_unlink_47498c(const char *path)
{
    if (audio_file_ready_200746a8!=1u)
        return 0;
    if (path==0) {
        *audio_file_errno_location_439cc4()=22;
        return -1;
    }
    if (audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) {
        *audio_file_errno_location_439cc4()=16;
        return -1;
    }
    int32_t result=audio_file_lfs_remove_4cfa76(audio_file_lfs_context,path);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if (result>=0 || result==-2)
        return 0;
    *audio_file_errno_location_439cc4()=5;
    return -1;
}
