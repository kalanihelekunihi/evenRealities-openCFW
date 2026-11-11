#include <stdint.h>
/* Symbolic native code and typed .word/.asciz data; no instruction-byte arrays. */
const uint8_t r1_health_sync_kind0[2] __attribute__((section(".r1.health.sync.kind0")))={0,3};
const uint8_t r1_health_sync_kind1[2] __attribute__((section(".r1.health.sync.kind1")))={1,3};
const uint8_t r1_health_sync_kind2[2] __attribute__((section(".r1.health.sync.kind2")))={2,3};
const uint8_t r1_health_sync_kind3[2] __attribute__((section(".r1.health.sync.kind3")))={3,3};
const uint8_t r1_health_sync_kind4[2] __attribute__((section(".r1.health.sync.kind4")))={4,24};
const uint8_t r1_health_sync_kind5[2] __attribute__((section(".r1.health.sync.kind5")))={5,6};
volatile uint8_t r1_health_sync_pending_hr __attribute__((section(".r1.health.sync.pending.hr")))=0;
volatile uint8_t r1_health_sync_pending_spo2 __attribute__((section(".r1.health.sync.pending.spo2")))=0;
volatile uint8_t r1_health_sync_pending_hrv __attribute__((section(".r1.health.sync.pending.hrv")))=0;
volatile uint8_t r1_health_sync_pending_activity __attribute__((section(".r1.health.sync.pending.activity")))=0;
/* Stock 0x8b818: issue a sleep-data report request.  The byte at offset 1
 * is padding and is never read by the stock iterator. */
struct r1_sleep_sync_request {
    uint8_t kind;
    uint8_t reserved;
    uint16_t count;
};
struct r1_sleep_sync_report;
typedef uint32_t (*r1_sleep_report_callback)(const uint8_t *,
        const struct r1_sleep_sync_report *, uint32_t,
        const struct r1_sleep_sync_request *);
extern uint32_t r1_health_sync_provider_0008f954(const uint8_t *,
        const struct r1_sleep_sync_report *, uint32_t,
        const struct r1_sleep_sync_request *);
extern uint32_t r1_health_sync_provider_0005b39c(uint32_t,
        r1_sleep_report_callback, const struct r1_sleep_sync_request *);
_Static_assert(sizeof(struct r1_sleep_sync_request)==4,
               "sleep request ABI");
void r1_health_notification_stage_0008b818(uint32_t first, uint32_t second)
{
    struct r1_sleep_sync_request request;
    request.kind=(uint8_t)first;
    request.count=(uint16_t)second;
    r1_health_sync_provider_0005b39c(1u,
        r1_health_sync_provider_0008f954,&request);
}
