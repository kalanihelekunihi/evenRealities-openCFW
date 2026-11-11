#include <stdint.h>

/* Native 0x3227e0..0x322832: drain the PAwR response queue at 0x805008.
 * Each event is decoded; a decoded response gets its 6-byte address (event
 * +8) and a status of 1, or -1 when the decoder flagged it, and is
 * dispatched. Every event is released and the queue resumed. */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_pawr_decode_31e84c(uintptr_t,uintptr_t,uintptr_t);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_pawr_response_dispatch_322834(uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_pawr_queue_resume_31694c(void);

struct pawr_response {
    uint8_t decoded[18];
    int8_t status;
    uint8_t address[6];
    uint8_t reserved[5];
    uint8_t flagged;
    uint8_t handler;
} __attribute__((aligned(4)));

void opencfw_em9305_callback_3227e0(void)
{
    struct pawr_response response;
    for (;;) {
        uintptr_t event = opencfw_em9305_wsf_event_remove(0x805008u, (uintptr_t)&response.handler);
        if (event == 0u) return;
        if (opencfw_em9305_pawr_decode_31e84c(event, (uintptr_t)&response,
                                              (uintptr_t)&response.flagged) != 0u) {
            response.status = 1;
            (void)opencfw_em9305_memcpy(response.address, (const void *)(event + 8u), 6u);
            if (response.flagged != 0u) response.status = -1;
            (void)opencfw_em9305_pawr_response_dispatch_322834((uintptr_t)&response);
        }
        (void)opencfw_em9305_wsf_event_release(event);
        (void)opencfw_em9305_pawr_queue_resume_31694c();
    }
}
