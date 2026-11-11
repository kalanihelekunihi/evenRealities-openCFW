/* Health sample event gates and five/six-byte storage records. */
#include <stdint.h>

extern void r1_activity_event_storage(const volatile uint8_t *sample);
extern void r1_hr_event_storage(const volatile uint8_t *sample);
extern void r1_hrv_event_storage(const volatile uint8_t *sample);
extern void r1_spo2_event_storage(const volatile uint8_t *sample);
extern void r1_stress_event_storage(const volatile uint8_t *sample);
extern void r1_temperature_event_storage(const volatile uint8_t *sample);
extern uint32_t r1_time_backend_timestamp(void);
extern void r1_health_event_notification_throttle(uint32_t kind);

static uint32_t load_timestamp(const volatile uint8_t *sample)
{
    return *(const volatile uint32_t *)(const void *)(sample + 4);
}

static void store_timestamp(volatile uint8_t *sample, uint32_t timestamp)
{
    *(volatile uint32_t *)(void *)(sample + 4) = timestamp;
}

static void record_timestamp(uint8_t *record, uint32_t timestamp, uint32_t offset)
{
    record[offset] = (uint8_t)timestamp;
    record[offset + 1u] = (uint8_t)(timestamp >> 8);
    record[offset + 2u] = (uint8_t)(timestamp >> 16);
    record[offset + 3u] = (uint8_t)(timestamp >> 24);
}

void r1_event_service_0008a7f4(uint32_t payload, uint32_t length)
{
    (void)length;
    if (payload == 0u) return;
    r1_activity_event_storage((const volatile uint8_t *)(uintptr_t)payload);
    r1_health_event_notification_throttle(4u);
}

void r1_event_service_0008a80a(uint32_t payload, uint32_t length)
{
    (void)length;
    if (payload == 0u) return;
    volatile uint8_t *sample = (volatile uint8_t *)(uintptr_t)payload;
    uint32_t value = sample[0];
    if (value < 40u || value > 220u) return;
    uint32_t timestamp = load_timestamp(sample);
    if (timestamp == 0u) {
        timestamp = r1_time_backend_timestamp();
        store_timestamp(sample, timestamp);
    }
    uint8_t record[5];
    record[0] = sample[0];
    record_timestamp(record, load_timestamp(sample), 1u);
    r1_hr_event_storage(record);
    r1_health_event_notification_throttle(0u);
}

void r1_event_service_0008a83e(uint32_t payload, uint32_t length)
{
    (void)length;
    volatile uint8_t *sample = (volatile uint8_t *)(uintptr_t)payload;
    uint32_t timestamp = load_timestamp(sample);
    if (timestamp == 0u) {
        timestamp = r1_time_backend_timestamp();
        store_timestamp(sample, timestamp);
    }
    uint16_t value = *(const volatile uint16_t *)(const void *)sample;
    uint8_t record[6];
    record[0] = (uint8_t)value;
    record[1] = (uint8_t)(value >> 8);
    record_timestamp(record, load_timestamp(sample), 2u);
    r1_hrv_event_storage(record);
    r1_health_event_notification_throttle(5u);
}

void r1_event_service_0008a8ae(uint32_t payload, uint32_t length)
{
    (void)length;
    if (payload == 0u) return;
    volatile uint8_t *sample = (volatile uint8_t *)(uintptr_t)payload;
    if (sample[0] < 70u) return;
    uint32_t timestamp = r1_time_backend_timestamp();
    store_timestamp(sample, timestamp);
    uint8_t record[5];
    record[0] = sample[0];
    record_timestamp(record, timestamp, 1u);
    r1_spo2_event_storage(record);
    r1_health_event_notification_throttle(1u);
}

void r1_event_service_0008a8d8(uint32_t payload, uint32_t length)
{
    (void)length;
    if (payload == 0u) return;
    volatile uint8_t *sample = (volatile uint8_t *)(uintptr_t)payload;
    if (sample[0] > 100u) return;
    uint32_t timestamp = r1_time_backend_timestamp();
    store_timestamp(sample, timestamp);
    uint8_t record[5];
    record[0] = sample[0];
    record_timestamp(record, timestamp, 1u);
    r1_stress_event_storage(record);
}

void r1_event_service_0008a8fc(uint32_t payload, uint32_t length)
{
    (void)length;
    if (payload == 0u) return;
    volatile uint8_t *sample = (volatile uint8_t *)(uintptr_t)payload;
    uint32_t value = *(const volatile uint16_t *)(const void *)sample;
    if (value < 250u || value > 500u) return;
    uint32_t timestamp = r1_time_backend_timestamp();
    store_timestamp(sample, timestamp);
    uint8_t record[5];
    record[0] = (uint8_t)(sample[0] + 6u);
    record_timestamp(record, timestamp, 1u);
    r1_temperature_event_storage(record);
}
