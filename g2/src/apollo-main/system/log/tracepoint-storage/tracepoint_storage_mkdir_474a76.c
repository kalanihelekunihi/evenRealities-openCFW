/* Stock Main 0x474a76: guarded LittleFS directory creation facade. */
#include <stdint.h>

extern uint32_t audio_file_ready_200746a8;
extern int32_t *audio_file_errno_location_439cc4(void);
extern int32_t audio_file_mutex_acquire(void *,uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_file_lfs_mkdir_4cfc5c(void *,const char *);
extern void *audio_file_api_mutex;
extern uint8_t audio_file_lfs_context[];

int32_t audio_tracepoint_storage_mkdir_474a76(const char *path,uint32_t ignored) {
    (void)ignored;
    if(audio_file_ready_200746a8!=1u) return 0;
    if(path==0) {*audio_file_errno_location_439cc4()=22;return -1;}
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) {
        *audio_file_errno_location_439cc4()=16;return -1;
    }
    int32_t status=audio_file_lfs_mkdir_4cfc5c(audio_file_lfs_context,path);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if(status<0) {
        *audio_file_errno_location_439cc4()=status==-17 ? 17 : status==-2 ? 2 : 5;
        return -1;
    }
    return 0;
}
