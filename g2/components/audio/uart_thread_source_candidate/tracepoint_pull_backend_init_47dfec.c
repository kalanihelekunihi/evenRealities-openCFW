/* Stock Main 0x47dfec: initialize tracepoint persistence and resume state. */
#include <stdint.h>

extern uint8_t audio_tracepoint_pull_enabled_20075038;
extern volatile uint32_t audio_tracepoint_session_generation_20074ad4;
extern volatile uint32_t audio_tracepoint_next_sequence_20004188;
extern uint32_t audio_tracepoint_pull_pending_20074ad8[2];
extern int32_t audio_tracepoint_storage_mkdir_474a76(const char *,uint32_t);
extern void audio_tracepoint_read_state_47df8a(void);
extern int32_t audio_tracepoint_list_files_47deb4(uint32_t *);
extern void audio_tracepoint_format_pull_path_47de0a(char *,uint32_t,uint32_t);
extern uint32_t audio_tracepoint_file_size_47de7a(const char *);
extern int32_t audio_tracepoint_write_state_47df28(void);

int32_t audio_tracepoint_pull_backend_init_47dfec(void) {
    if(audio_tracepoint_pull_enabled_20075038!=0u) return 0;
    (void)audio_tracepoint_storage_mkdir_474a76("/log/tp",0u);
    audio_tracepoint_read_state_47df8a();
    audio_tracepoint_session_generation_20074ad4++;

    struct {
        int32_t count;
        uint32_t lowest;
        uint32_t highest;
        char path[64];
    } state;
    int32_t status=audio_tracepoint_list_files_47deb4((uint32_t *)&state);
    if(status!=0) return status;
    if(state.count>0) {
        uint32_t after_highest=state.highest+1u;
        if(audio_tracepoint_next_sequence_20004188<after_highest)
            audio_tracepoint_next_sequence_20004188=after_highest;
        audio_tracepoint_format_pull_path_47de0a(state.path,64u,state.highest);
        uint32_t size=audio_tracepoint_file_size_47de7a(state.path);
        if(size-32u<0x7fe0u) {
            audio_tracepoint_pull_pending_20074ad8[0]=state.highest;
            audio_tracepoint_pull_pending_20074ad8[1]=size;
        }
    }
    status=audio_tracepoint_write_state_47df28();
    if(status==0) audio_tracepoint_pull_enabled_20075038=1u;
    return status;
}
