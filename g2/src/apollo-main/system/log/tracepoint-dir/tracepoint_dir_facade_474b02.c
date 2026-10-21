/* Stock Main file-directory API 0x474b02/0x474bb8/0x474c66. */
#include <stdint.h>

extern uint32_t audio_file_ready_200746a8;
extern uint8_t audio_file_lfs_context[];
extern void *audio_file_api_mutex;
extern int32_t *audio_file_errno_location_439cc4(void);
extern void *codec_allocate(uint32_t);
extern void audio_file_heap_free(void *);
extern void *audio_settings_copy_text(void *,const void *,uint32_t);
extern int32_t audio_file_mutex_acquire(void *,uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_file_lfs_dir_open_4cfc66(void *,void *,const char *);
extern int32_t audio_file_lfs_dir_read_4cfd02(void *,void *,void *);
extern int32_t audio_file_lfs_dir_close_4cfcf8(void *,void *);

uint8_t audio_tracepoint_dir_result_200701e8[0x101]
    __attribute__((section(".bss.opencfw.tracepoint.dir_result"),used));

void *audio_tracepoint_dir_open_474b02(const char *path) {
    if(audio_file_ready_200746a8!=1u) {*audio_file_errno_location_439cc4()=2;return 0;}
    if(path==0) {*audio_file_errno_location_439cc4()=22;return 0;}
    uint8_t *dir=(uint8_t *)codec_allocate(0x240u);
    if(dir==0) {*audio_file_errno_location_439cc4()=12;return 0;}
    *(uint32_t *)(void *)dir=(uint32_t)(uintptr_t)audio_file_lfs_context;
    (void)audio_settings_copy_text(dir+0x140u,path,0xffu);
    dir[0x23fu]=0;
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) {
        audio_file_heap_free(dir);*audio_file_errno_location_439cc4()=16;return 0;
    }
    int32_t result=audio_file_lfs_dir_open_4cfc66(audio_file_lfs_context,dir+4u,path);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if(result<0) {
        audio_file_heap_free(dir);
        *audio_file_errno_location_439cc4()=result==-2 ? 2 : 5;
        return 0;
    }
    return dir;
}

void *audio_tracepoint_dir_read_474bb8(void *handle) {
    if(audio_file_ready_200746a8!=1u || handle==0) {
        *audio_file_errno_location_439cc4()=9;return 0;
    }
    uint8_t *dir=(uint8_t *)handle;
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) {
        *audio_file_errno_location_439cc4()=16;return 0;
    }
    int32_t result=audio_file_lfs_dir_read_4cfd02(
        (void *)(uintptr_t)*(uint32_t *)(void *)dir,dir+4u,dir+0x38u);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if(result<0) {*audio_file_errno_location_439cc4()=5;return 0;}
    if(result==0) return 0;
    (void)audio_settings_copy_text(audio_tracepoint_dir_result_200701e8,dir+0x40u,0xffu);
    audio_tracepoint_dir_result_200701e8[0xffu]=0;
    uint8_t type=dir[0x38u];
    audio_tracepoint_dir_result_200701e8[0x100u]=type==2u ? 4u : (type==1u ? 8u : 0u);
    return audio_tracepoint_dir_result_200701e8;
}

int32_t audio_tracepoint_dir_close_474c66(void *handle) {
    if(audio_file_ready_200746a8!=1u) return 0;
    if(handle==0) {*audio_file_errno_location_439cc4()=9;return -1;}
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) {
        *audio_file_errno_location_439cc4()=16;return -1;
    }
    uint8_t *dir=(uint8_t *)handle;
    int32_t result=audio_file_lfs_dir_close_4cfcf8(
        (void *)(uintptr_t)*(uint32_t *)(void *)dir,dir+4u);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    audio_file_heap_free(handle);
    if(result<0) {*audio_file_errno_location_439cc4()=5;return -1;}
    return 0;
}
