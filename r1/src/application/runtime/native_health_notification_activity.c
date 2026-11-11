/* Stock 0x8baec: activity notification and flash/offline day merge. */
#include <stdint.h>
#include <stddef.h>
#include "native_health_offline_consume.h"
#include "native_health_offline_merge.h"
#include "native_health_packet_flush.h"

struct fdb_tsdb;
struct fdb_tsl;
extern uint32_t r1_health_record_read(void *), r1_health_record_write(const void *);
extern uint32_t r1_time_backend_timestamp(void), r1_time_local_day_start(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_0(uint32_t, const char *);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);
extern void nrf_log_frontend_std_2(uint32_t, const char *, uint32_t, uint32_t);
extern void nrf_log_frontend_std_3(uint32_t, const char *, uint32_t, uint32_t, uint32_t);
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern struct fdb_tsdb *r1_health_sync_provider_00070028(void);
extern uint32_t r1_health_sync_provider_00063694(volatile uint8_t *, uint32_t, volatile uint8_t *);
extern uint32_t r1_health_sync_provider_00063cb4(const volatile uint8_t *, int32_t, int32_t, uint32_t);
extern void r1_health_sync_provider_00063ad8(struct fdb_tsdb *, int32_t, int32_t,
    uint32_t (*)(struct fdb_tsl *, void *), void *);
extern uint32_t r1_health_sync_provider_0003c958(struct fdb_tsl *, void *);
extern void r1_health_sync_provider_0003c0d8(volatile uint8_t *);
extern void r1_health_sync_provider_0003c304(volatile uint8_t *, uint32_t, uint32_t);
extern volatile uint8_t r1_health_sync_pending_activity;

/* The iterator callback reads these five fields at offsets 0,4,8,12,16. */
struct activity_flash_context {
    struct fdb_tsdb *database;
    void *cache;
    volatile uint8_t *builder;
    uint16_t sample_offset;
    uint16_t reserved;
    uint32_t today;
};
_Static_assert(sizeof(struct activity_flash_context) == 20, "activity FlashDB context ABI");

static uint32_t ring_enabled(void)
{
    if (r1_structured_log_mode_get() & 1u) return 1u;
    return (r1_structured_log_mode_get() & 4u) != 0u;
}
static void log0(uint32_t level, uint32_t metadata, const char *ring, const char *sdk)
{
    if (ring_enabled()) (void)r1_structured_log_format(level, ring, ring);
    if (r1_structured_log_mode_get() & 2u) nrf_log_frontend_std_0(metadata, sdk);
}
static void log1(uint32_t level, uint32_t metadata, const char *ring,
                 const char *sdk, uint32_t a)
{
    if (ring_enabled()) (void)r1_structured_log_format(level, ring, ring, a);
    if (r1_structured_log_mode_get() & 2u) nrf_log_frontend_std_1(metadata, sdk, a);
}
static void log2(uint32_t level, uint32_t metadata, const char *ring,
                 const char *sdk, uint32_t a, uint32_t b)
{
    if (ring_enabled()) (void)r1_structured_log_format(level, ring, ring, a, b);
    if (r1_structured_log_mode_get() & 2u) nrf_log_frontend_std_2(metadata, sdk, a, b);
}

void r1_health_notification_stage_0008baec(uint32_t first, uint32_t second)
{
    (void)second;
    uint32_t record[6] = {0};
    (void)r1_health_record_read(record);
    uint32_t now = r1_time_backend_timestamp();
    uint32_t today = r1_time_local_day_start();
    if (today <= UINT32_C(0x38640900)) today = 0;
    const uint32_t metadata2 = 0x001c0002u;
    const uint32_t metadata3 = 0x001c0003u;
    if (now > UINT32_C(0x38640900) && record[4] > now) {
        log2(0x08800000u, metadata2,
             "[RING]activity_sync: last_sync(%u) > now(%u), self-heal clamp",
             "activity_sync: last_sync(%u) > now(%u), self-heal clamp", record[4], now);
        uint32_t updated[6] = {0};
        record[4] = now;
        (void)r1_health_record_read(updated);
        updated[4] = now;
        (void)r1_health_record_write(updated);
    }
    log2(0x0c800000u, metadata3,
         "[RING]activity_sync start: last_sync=%u today_zero=%u",
         "activity_sync start: last_sync=%u today_zero=%u", record[4], today);

    struct fdb_tsdb *database = r1_health_sync_provider_00070028();
    void *cache = pvPortMalloc(128u);
    if (!cache) {
        log0(0x04000000u, 0x001c0001u,
             "[RING]activity_sync: alloc cache failed", "activity_sync: alloc cache failed");
        return;
    }
    uint32_t last_flash = 0;
    (void)r1_health_sync_provider_00063694((volatile uint8_t *)database, 6u,
                                            (volatile uint8_t *)&last_flash);
    uint32_t start = record[4] < today ? record[4] : today;
    if (now > 259200u && now - 259200u > start) {
        start = now - 259200u;
        log1(0x08400000u, metadata2,
             "[RING]activity_sync: limit flash window to %u days",
             "activity_sync: limit flash window to %u days", 3u);
    }
    uint32_t count = 0;
    if (start < today) {
        count = r1_health_sync_provider_00063cb4((const volatile uint8_t *)database,
                                                   (int32_t)(start + 1u), (int32_t)today, 2u);
    }
    uint32_t offline_empty = r1_activity_offline_queue_empty();
    if (!count && offline_empty && start < today) {
        uint32_t rewind = last_flash;
        if (!rewind || rewind >= today) rewind = today ? today - 1u : 0u;
        if (record[4] < rewind) {
            uint32_t updated[6] = {0};
            (void)r1_health_record_read(updated);
            updated[4] = rewind;
            (void)r1_health_record_write(updated);
            log1(0x0c400000u, metadata3,
                 "[RING]activity_sync: fast forward to %u (no flash data)",
                 "activity_sync: fast forward to %u (no flash data)", rewind);
        }
    }

    /* The stock scan adds the lengths of kinds zero through three before
     * finding activity at kind four, for a 20-byte packet prefix. */
    volatile uint8_t *builder = pvPortMalloc(1180u);
    if (!builder) {
        log0(0x04000000u, 0x001c0001u,
             "[RING]activity_sync: alloc day builder failed", "activity_sync: alloc day builder failed");
        vPortFree(cache);
        return;
    }
    for (uint32_t i = 0; i < 1180u; ++i) builder[i] = 0;
    *(volatile uint16_t *)(builder + 1168u) = (uint16_t)first;
    *(volatile uint32_t *)(builder + 1172u) = (uint32_t)(uintptr_t)r1_health_sync_provider_0003c0d8;
    builder[1176] = 0;
    struct activity_flash_context context = {database, cache, builder, 20u, 0u, today};
    if (count && start < today) {
        if (ring_enabled())
            (void)r1_structured_log_format(0x0cc00000u,
                "[RING]activity_sync flash: [%u, %u) cnt=%u",
                "[RING]activity_sync flash: [%u, %u) cnt=%u", start + 1u, today, count);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_3(metadata3,
                "activity_sync flash: [%u, %u) cnt=%u", start + 1u, today, count);
        r1_health_sync_provider_00063ad8(database, (int32_t)(start + 1u),
                                           (int32_t)today,
                                           r1_health_sync_provider_0003c958, &context);
    }
    r1_activity_day_packet_flush(builder);
    if (!r1_activity_offline_queue_empty()) {
        if (ring_enabled())
            (void)r1_structured_log_format(0x0c400000u,
                "[RING]activity_sync offline: buf_cnt=%u",
                "[RING]activity_sync offline: buf_cnt=%u", r1_health_sync_pending_activity);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_1(metadata3,
                "activity_sync offline: buf_cnt=%u", r1_health_sync_pending_activity);
        builder[1176] = 1;
        r1_activity_day_builder_reset(builder);
        r1_activity_offline_queue_merge(builder);
        r1_activity_day_packet_flush(builder);
        builder[1176] = 0;
    }
    r1_health_sync_provider_0003c304(builder, today, record[4]);
    vPortFree((void *)builder);
    vPortFree(cache);
}
