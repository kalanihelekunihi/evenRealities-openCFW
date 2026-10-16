/* Stock Main 0x47e090: keep fewer than four tracepoint files before creation. */
#include <stdint.h>

extern int32_t audio_tracepoint_list_files_47deb4(void *);
extern void audio_tracepoint_format_pull_path_47de0a(char *,uint32_t,uint32_t);
extern int32_t audio_tracepoint_storage_unlink_47498c(const char *);

int32_t audio_tracepoint_trim_old_files_47e090(void) {
    struct {
        int32_t count;
        uint32_t oldest_sequence;
        uint32_t reserved;
        char path[64];
    } state;
    for(;;) {
        int32_t status=audio_tracepoint_list_files_47deb4(&state);
        if(status!=0) return status;
        if(state.count<4) return 0;
        audio_tracepoint_format_pull_path_47de0a(state.path,64u,
                                                 state.oldest_sequence);
        if(audio_tracepoint_storage_unlink_47498c(state.path)!=0) return -5;
    }
}
