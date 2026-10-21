/* Stock Main 0x47e1ec: finalize a pending pull before the next one. */
#include <stdint.h>
extern void audio_tracepoint_close_active_file_47e06a(void);

uint32_t audio_tracepoint_pull_pending_20074ad8[2]
    __attribute__((section(".bss.opencfw.tracepoint.pull_pending"),aligned(4),used));
uint8_t audio_tracepoint_pull_enabled_20075038
    __attribute__((section(".bss.opencfw.tracepoint.pull_enabled"),used));

int32_t audio_tracepoint_pull_initialize_47e1ec(void) {
    if(audio_tracepoint_pull_enabled_20075038==0u) return -2;
    if(audio_tracepoint_pull_pending_20074ad8[0]!=0u &&
       audio_tracepoint_pull_pending_20074ad8[1]>=0x21u) {
        audio_tracepoint_close_active_file_47e06a();
        audio_tracepoint_pull_pending_20074ad8[0]=0u;
        audio_tracepoint_pull_pending_20074ad8[1]=0u;
    }
    return 0;
}
