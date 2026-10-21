/* Stock Main 0x47e0c8: allocate and initialize a new tracepoint file. */
#include <stdint.h>

volatile uint32_t audio_tracepoint_next_sequence_20004188
    __attribute__((section(".bss.opencfw.tracepoint.next_sequence"),aligned(4),used));
volatile uint32_t audio_tracepoint_session_generation_20074ad4
    __attribute__((section(".bss.opencfw.tracepoint.session_generation"),aligned(4),used));

extern uint32_t audio_tracepoint_pull_pending_20074ad8[2];
extern void *audio_tracepoint_active_file_handle;
extern int32_t audio_tracepoint_trim_old_files_47e090(void);
extern int32_t audio_tracepoint_write_state_47df28(void);
extern void audio_tracepoint_format_pull_path_47de0a(char *,uint32_t,uint32_t);
extern void *audio_tracepoint_file_open_474550(const char *,const char *);
extern void audio_tracepoint_build_header_48ed00(uint8_t *,uint32_t,uint32_t);
extern int32_t audio_tracepoint_file_write_474682(const void *,uint32_t,uint32_t,void *);
extern void audio_tracepoint_close_active_file_47e06a(void);

int32_t audio_tracepoint_open_new_file_47e0c8(void) {
    int32_t status=audio_tracepoint_trim_old_files_47e090();
    if(status!=0) return status;

    uint32_t sequence=audio_tracepoint_next_sequence_20004188;
    audio_tracepoint_next_sequence_20004188=sequence+1u;
    status=audio_tracepoint_write_state_47df28();
    if(status!=0) return status;

    uint8_t header[32];
    char path[64];
    audio_tracepoint_format_pull_path_47de0a(path,64u,sequence);
    audio_tracepoint_active_file_handle=audio_tracepoint_file_open_474550(path,"wb");
    if(audio_tracepoint_active_file_handle==0) return -5;

    audio_tracepoint_build_header_48ed00(header,sequence,
                                         audio_tracepoint_session_generation_20074ad4);
    if(audio_tracepoint_file_write_474682(header,1u,32u,
                                          audio_tracepoint_active_file_handle)!=32) {
        audio_tracepoint_close_active_file_47e06a();
        return -5;
    }
    audio_tracepoint_pull_pending_20074ad8[0]=sequence;
    audio_tracepoint_pull_pending_20074ad8[1]=32u;
    return 0;
}
