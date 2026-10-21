/* Stock Main 0x47e220: close an active tracepoint file after pull draining. */
#include <stdint.h>

extern void *audio_tracepoint_active_file_handle;
extern int32_t audio_tracepoint_file_close_474910(void *);

void audio_tracepoint_pull_complete_47e220(void) {
    void *handle=audio_tracepoint_active_file_handle;
    if(handle!=0)
        (void)audio_tracepoint_file_close_474910(handle);
}
