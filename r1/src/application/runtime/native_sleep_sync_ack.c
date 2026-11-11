/* Stock R1 sleep sync ACK completion at application 0x8f780. */
#include <stdint.h>

extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern void vPortFree(void *);

struct r1_sleep_sync_ack_context {
    uint32_t head;
    uint32_t start;
    uint32_t end;
};
_Static_assert(sizeof(struct r1_sleep_sync_ack_context)==12,"sleep ACK context");

static const char null_ring[]="[RING]sleep sync ack ctx is null";
static const char null_sdk[]="sleep sync ack ctx is null";
static const char failed_ring[]="[RING]sleep sync ack msg send fail";
static const char failed_sdk[]="sleep sync ack msg send fail";
static const char ok_ring[]="[RING]sleep sync ack ok: head=0x%08X, start=%u, end=%u";
static const char ok_sdk[]="sleep sync ack ok: head=0x%08X, start=%u, end=%u";

static void log_plain(const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04000000,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0001,sdk);
}

void r1_sleep_sync_ack_plan(struct r1_sleep_sync_ack_context *context)
{
    if (!context) {
        log_plain(null_ring,null_sdk);
        return;
    }
    if (!r1_event_publish(0x2001,context,12)) {
        log_plain(failed_ring,failed_sdk);
    } else {
        if ((r1_structured_log_mode_get()&1u)||
            (r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x0cc00000,ok_ring,ok_ring,
                                           context->head,context->start,
                                           context->end);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_3(0x001c0003,ok_sdk,
                                   context->head,context->start,context->end);
    }
    vPortFree(context);
}
