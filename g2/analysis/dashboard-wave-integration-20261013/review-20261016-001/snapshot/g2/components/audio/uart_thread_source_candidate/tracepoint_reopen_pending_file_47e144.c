/* Stock Main 0x47e144: reopen the pending tracepoint file in append mode. */
#include <stdint.h>

extern uint32_t audio_tracepoint_pull_pending_20074ad8[2];
extern void *audio_tracepoint_active_file_handle;
extern void audio_tracepoint_format_pull_path_47de0a(char *,uint32_t,uint32_t);
extern void *audio_tracepoint_file_open_474550(const char *,const char *);

int32_t audio_tracepoint_reopen_pending_file_47e144(void) {
    char path[64];
    audio_tracepoint_format_pull_path_47de0a(path,64u,
                                             audio_tracepoint_pull_pending_20074ad8[0]);
    audio_tracepoint_active_file_handle=audio_tracepoint_file_open_474550(path,"ab");
    return audio_tracepoint_active_file_handle!=0 ? 0 : -5;
}
