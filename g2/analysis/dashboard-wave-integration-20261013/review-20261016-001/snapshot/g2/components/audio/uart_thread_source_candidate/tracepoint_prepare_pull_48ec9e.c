/* Stock Main 0x48ec9e: prepare file pull through readiness/init children. */
#include <stdint.h>
extern int32_t audio_tracepoint_pull_ready_48eb90(void);
extern int32_t audio_tracepoint_pull_initialize_47e1ec(void);
int32_t audio_tracepoint_prepare_pull_48ec9e(void) {
    int32_t result=audio_tracepoint_pull_ready_48eb90();
    return result!=0 ? result : audio_tracepoint_pull_initialize_47e1ec();
}
