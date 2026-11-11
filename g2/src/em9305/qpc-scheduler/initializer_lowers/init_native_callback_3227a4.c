#include <stdint.h>

/* Native 0x3227a4..0x3227e0: drain the PAwR queue at 0x805000. Each event
 * is decoded; a decoded response gets status -1 and is dispatched. Every
 * event is released and the queue resumed. */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t out_u8);
extern uint32_t opencfw_em9305_pawr_decode_31e84c(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_pawr_response_dispatch_322834(uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);
extern uint32_t opencfw_em9305_pawr_queue_resume_31694c(void);

struct pawr_response {
    uint8_t decoded[18];
    int8_t status;
    uint8_t address[6];
    uint8_t reserved[5];
    uint8_t flagged;
    uint8_t handler;
} __attribute__((aligned(4)));

void opencfw_em9305_callback_3227a4(void)
{
    struct pawr_response response;
    for(;;){
        uintptr_t event=opencfw_em9305_wsf_event_remove(0x805000u,
                                                        (uintptr_t)&response.handler);
        if(event==0u)return;
        if(opencfw_em9305_pawr_decode_31e84c(event,(uintptr_t)&response,
                                             (uintptr_t)&response.flagged)!=0u){
            response.status=-1;
            (void)opencfw_em9305_pawr_response_dispatch_322834((uintptr_t)&response);
        }
        (void)opencfw_em9305_wsf_event_release(event);
        (void)opencfw_em9305_pawr_queue_resume_31694c();
    }
}
