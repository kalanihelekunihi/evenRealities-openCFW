/* Stock Main 0x47e088 wrapper and 0x47e06a active-file close/clear. */
#include <stdint.h>
extern int32_t audio_file_close(void *); /* stock 0x4745f4 */
void *audio_tracepoint_active_file_handle
    __attribute__((section(".bss.opencfw.tracepoint.active_file"), aligned(4), used));
_Static_assert(sizeof(audio_tracepoint_active_file_handle)==4u,
               "Apollo active-file handle slot");
void audio_tracepoint_close_active_file_47e06a(void)
{
    void *handle=audio_tracepoint_active_file_handle;
    if (handle!=0) {
        (void)audio_file_close(handle);
        audio_tracepoint_active_file_handle=0;
    }
}
void audio_tracepoint_storage_lock_47e088(void)
{
    audio_tracepoint_close_active_file_47e06a();
}
