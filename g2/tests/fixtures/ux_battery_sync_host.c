#include <stddef.h>
#include <stdint.h>

uint8_t host_level;
uint8_t host_charging;
uint8_t host_sent_id;
const void *host_received;
uint32_t host_notifications[4];
uint32_t host_notification_count;
uint8_t host_update_level;
uint8_t host_update_charging;
uint32_t host_update_count;

void host_reset(void)
{
    host_level = 0;
    host_charging = 0;
    host_sent_id = 0;
    host_received = NULL;
    host_notification_count = 0;
    host_update_level = 0;
    host_update_charging = 0;
    host_update_count = 0;
}

void host_charger_send(uint8_t message_id) { host_sent_id = message_id; }
void host_charger_receive(const void *message) { host_received = message; }
uint8_t host_ring_level_get(void) { return host_level; }
uint8_t host_ring_charging_get(void) { return host_charging; }
void host_ring_state_set(uint8_t level, uint8_t charging)
{
    host_level = level;
    host_charging = charging;
}
void host_ring_notify(uint32_t key, uint32_t value)
{
    if (host_notification_count < 2u) {
        host_notifications[host_notification_count * 2u] = key;
        host_notifications[host_notification_count * 2u + 1u] = value;
    }
    ++host_notification_count;
}
void host_ring_update(uint8_t level, uint8_t charging)
{
    host_update_level = level;
    host_update_charging = charging;
    ++host_update_count;
}
