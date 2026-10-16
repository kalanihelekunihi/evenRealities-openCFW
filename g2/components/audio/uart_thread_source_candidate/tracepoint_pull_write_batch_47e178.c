/* Stock Main 0x47e178: append one bounded tracepoint batch to the active file. */
#include <stdint.h>

extern uint8_t audio_tracepoint_pull_enabled_20075038;
extern uint32_t audio_tracepoint_pull_pending_20074ad8[2];
extern void *audio_tracepoint_active_file_handle;
extern void audio_tracepoint_close_active_file_47e06a(void);
extern int32_t audio_tracepoint_open_new_file_47e0c8(void);
extern int32_t audio_tracepoint_reopen_pending_file_47e144(void);
extern int32_t audio_tracepoint_file_write_474682(const void *,uint32_t,uint32_t,void *);

int32_t audio_tracepoint_pull_write_batch_47e178(const void *batch,uint32_t bytes) {
    if(audio_tracepoint_pull_enabled_20075038==0u) return -2;

    if(audio_tracepoint_pull_pending_20074ad8[0]!=0u &&
       bytes+audio_tracepoint_pull_pending_20074ad8[1]>=0x8001u) {
        audio_tracepoint_close_active_file_47e06a();
        audio_tracepoint_pull_pending_20074ad8[0]=0u;
    }

    if(audio_tracepoint_active_file_handle==0) {
        int32_t status=(audio_tracepoint_pull_pending_20074ad8[0]==0u)
            ? audio_tracepoint_open_new_file_47e0c8()
            : audio_tracepoint_reopen_pending_file_47e144();
        if(status!=0) return status;
    }

    int32_t written=audio_tracepoint_file_write_474682(batch,1u,bytes,
                                                         audio_tracepoint_active_file_handle);
    if((uint32_t)written!=bytes) {
        audio_tracepoint_close_active_file_47e06a();
        return -5;
    }
    audio_tracepoint_pull_pending_20074ad8[1]+=bytes;
    return 0;
}
