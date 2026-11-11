#include <stdint.h>

/* Native 0x32c148..0x32c174: drain the LL event queue at 0x805694. Each
 * removed event is handed to the LL event callback through a frame whose
 * first word is the event pointer (handler byte from the queue at frame+7),
 * then released (re-read from the frame); finally run 32c254. */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_32c254(void);

struct init_event_frame_32c148 {
    uintptr_t event;
    uint8_t ambient[3];
    uint8_t handler;
};

uint32_t opencfw_em9305_callback_32c148(void)
{
    struct init_event_frame_32c148 frame;
    for(;;) {
        uintptr_t event=opencfw_em9305_wsf_event_remove((uintptr_t)0x805694u,
                                                        (uintptr_t)&frame.handler);
        frame.event=event;
        if(event==0u) break;
        (void)opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&frame);
        (void)opencfw_em9305_wsf_event_release(frame.event);
    }
    return opencfw_em9305_init_callback_32c254();
}
