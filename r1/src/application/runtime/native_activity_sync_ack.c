/* Source-owned acknowledgement callbacks at 0x3c0d8, 0x3fcec, 0x40bd4, and 0x43eb0. */
#include <stdint.h>

extern uint32_t r1_time_backend_timestamp(void);
extern uint32_t r1_health_record_read(void *record);
extern uint32_t r1_health_record_write(const void *record);
extern void r1_activity_offline_queue_consume(uint32_t cutoff);
extern void r1_heart_rate_offline_queue_consume(uint32_t cutoff);
extern void r1_hrv_offline_queue_consume(uint32_t cutoff);
extern void r1_spo2_offline_queue_consume(uint32_t cutoff);
extern void vPortFree(void *memory);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t metadata, const char *format,
                                         const char *record, ...);
extern void nrf_log_frontend_std_0(uint32_t metadata, const char *format);
extern void nrf_log_frontend_std_2(uint32_t metadata, const char *format,
                                   uint32_t first, uint32_t second);

struct acknowledgement_config {
    uint32_t cursor_index;
    uint32_t clock_after_mode;
    void (*consume)(uint32_t);
    const char *null_ring;
    const char *null_sdk;
    const char *future_ring;
    const char *future_sdk;
    const char *update_ring;
    const char *update_sdk;
};

static const struct acknowledgement_config activity = {
    4u, 0u, r1_activity_offline_queue_consume,
    "[RING]activity_sync ack ctx is NULL", "activity_sync ack ctx is NULL",
    "[RING]activity_sync ack ignore future ts:%u > now:%u",
    "activity_sync ack ignore future ts:%u > now:%u",
    "[RING]activity_sync ack: update last_sync=%u type=%d",
    "activity_sync ack: update last_sync=%u type=%d"
};
static const struct acknowledgement_config heart_rate = {
    0u, 0u, r1_heart_rate_offline_queue_consume,
    "[RING]hr_sync ack ctx is NULL", "hr_sync ack ctx is NULL",
    "[RING]hr_sync ack ignore future ts:%u > now:%u",
    "hr_sync ack ignore future ts:%u > now:%u",
    "[RING]hr_sync ack: update last_sync=%u type=%d",
    "hr_sync ack: update last_sync=%u type=%d"
};
static const struct acknowledgement_config hrv = {
    3u, 1u, r1_hrv_offline_queue_consume,
    "[RING]hrv_sync ack ctx is NULL", "hrv_sync ack ctx is NULL",
    "[RING]hrv_sync ack ignore future ts:%u > now:%u",
    "hrv_sync ack ignore future ts:%u > now:%u",
    "[RING]hrv_sync ack: update last_sync=%u type=%d",
    "hrv_sync ack: update last_sync=%u type=%d"
};
static const struct acknowledgement_config spo2 = {
    1u, 0u, r1_spo2_offline_queue_consume,
    "[RING]spo2_sync ack ctx is NULL", "spo2_sync ack ctx is NULL",
    "[RING]spo2_sync ack ignore future ts:%u > now:%u",
    "spo2_sync ack ignore future ts:%u > now:%u",
    "[RING]spo2_sync ack: update last_sync=%u type=%d",
    "spo2_sync ack: update last_sync=%u type=%d"
};

static uint32_t ring_enabled(void)
{
    if (r1_structured_log_mode_get() & 1u) return 1u;
    return (r1_structured_log_mode_get() & 4u) != 0u;
}

__attribute__((noinline))
static void acknowledge(const struct acknowledgement_config *config,
                        volatile uint8_t *context)
{
    if (context == 0) {
        if (ring_enabled())
            (void)r1_structured_log_format(0x04000000u,
                config->null_ring, config->null_ring);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_0(0x001c0001u, config->null_sdk);
        return;
    }

    uint32_t now = 0u;
    if (!config->clock_after_mode) now = r1_time_backend_timestamp();
    uint32_t mode = context[0];
    if (mode == 0u || mode == 2u) {
        if (config->clock_after_mode) now = r1_time_backend_timestamp();
        uint32_t record[6] = {0};
        (void)r1_health_record_read(record);
        uint32_t acknowledged = *(volatile uint32_t *)(void *)(context + 4);
        if (acknowledged > now) {
            if (ring_enabled())
                (void)r1_structured_log_format(0x0c800000u,
                    config->future_ring, config->future_ring,
                    acknowledged, now);
            if (r1_structured_log_mode_get() & 2u)
                nrf_log_frontend_std_2(0x001c0003u,
                    config->future_sdk, acknowledged, now);
        } else if (acknowledged > record[config->cursor_index]) {
            record[config->cursor_index] = acknowledged;
            (void)r1_health_record_write(record);
            if (ring_enabled())
                (void)r1_structured_log_format(0x0c800000u,
                    config->update_ring, config->update_ring,
                    acknowledged, context[0]);
            if (r1_structured_log_mode_get() & 2u)
                nrf_log_frontend_std_2(0x001c0003u,
                    config->update_sdk, acknowledged, context[0]);
        }
    } else if (mode == 1u) {
        config->consume(*(volatile uint32_t *)(void *)(context + 4));
    }
    vPortFree((void *)context);
}

void r1_health_sync_provider_0003c0d8(volatile uint8_t *context)
{ acknowledge(&activity, context); }
void r1_health_sync_provider_0003fcec(volatile uint8_t *context)
{ acknowledge(&heart_rate, context); }
void r1_health_sync_provider_00040bd4(volatile uint8_t *context)
{ acknowledge(&hrv, context); }
void r1_health_sync_provider_00043eb0(volatile uint8_t *context)
{ acknowledge(&spo2, context); }
