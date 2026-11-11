/* Stock R1 sleep-sync report callback at application 0x8f954. */
#include <stdint.h>
#include <stddef.h>

extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_sleep_sync_packet_builder(const void *,uint32_t,uint32_t,const void *);

struct r1_sleep_sync_report {
    uint8_t kind;
    uint8_t reserved_01[11];
    uint32_t first_day;
    uint32_t last_day;
    uint8_t reserved_14[10];
    uint16_t stage_count;
};
_Static_assert(offsetof(struct r1_sleep_sync_report,first_day)==12,"sleep sync first day");
_Static_assert(offsetof(struct r1_sleep_sync_report,last_day)==16,"sleep sync last day");
_Static_assert(offsetof(struct r1_sleep_sync_report,stage_count)==30,"sleep sync stages");

struct r1_sleep_sync_request {
    uint8_t kind;
    uint8_t reserved_01;
    uint16_t count;
};
_Static_assert(offsetof(struct r1_sleep_sync_request,count)==2,"sleep sync request count");

static const char ring_text[]="[RING]report sleep data: %d-%d, type:%d, numStages:%d";
static const char sdk_text[]="report sleep data: %d-%d, type:%d, numStages:%d";

uint32_t r1_health_sync_provider_0008f954(
    const uint8_t *source,const struct r1_sleep_sync_report *report,
    uint32_t ignored,const struct r1_sleep_sync_request *request)
{
    (void)ignored;
    if (!request) return 0;
    if (source[0]==1) return 1;
    if ((r1_structured_log_mode_get()&1u)||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0d000000,ring_text,ring_text,
                                       report->first_day,report->last_day,
                                       report->kind,report->stage_count);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_4(0x001c0003,sdk_text,report->first_day,
                               report->last_day,report->kind,report->stage_count);
    r1_sleep_sync_packet_builder(report,request->kind,request->count,source);
    return 1;
}
