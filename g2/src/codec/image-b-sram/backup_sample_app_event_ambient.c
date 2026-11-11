/* Native image-B sample LVP_APP event callback 0x1000c1c8..0x1000c1f3.
 * On event 91 it fetches the frame slot for the event's index (address and
 * size land in frame[0]/frame[1]) and pushes &frame[2] to audio-out, as the
 * native 16-byte stack frame does. Native leaves frame[2]/frame[3] unwritten;
 * they are zero here. Full downstream callback/hardware effects are not
 * qualified here. */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_frame_slot_10009e8c(
    uint32_t, uint32_t *, uint32_t *);
extern uint32_t gx8002_image_b_audio_out_push_frame_10006b60(
    uint32_t, uint32_t);

__attribute__((used))
int gx8002_image_b_sample_app_event_1000c1c8(void *event)
{
    const uint32_t *const message = event;
    if (message[0] != 91u)
        return 0;
    uint32_t frame[4];
    frame[2] = 0u;
    frame[3] = 0u;
    (void)gx8002_image_b_audio_frame_slot_10009e8c(message[1], &frame[0],
                                                   &frame[1]);
    (void)gx8002_image_b_audio_out_push_frame_10006b60(
        *(volatile const uint32_t *)(uintptr_t)UINT32_C(0x2002d798),
        (uint32_t)(uintptr_t)&frame[2]);
    return 0;
}
