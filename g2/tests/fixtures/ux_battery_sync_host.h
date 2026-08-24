#ifndef OPEN_CFW_UX_BATTERY_SYNC_HOST_H
#define OPEN_CFW_UX_BATTERY_SYNC_HOST_H

#include <stdint.h>

void host_charger_send(uint8_t message_id);
void host_charger_receive(const void *message);
void host_ring_update(uint8_t level, uint8_t charging);
void host_ring_state_set(uint8_t level, uint8_t charging);
uint8_t host_ring_level_get(void);
uint8_t host_ring_charging_get(void);
void host_ring_notify(uint32_t key, uint32_t value);

#define OPEN_CFW_UX_CHARGER_SEND(message_id) host_charger_send(message_id)
#define OPEN_CFW_UX_CHARGER_RECEIVE(message) host_charger_receive(message)
#define OPEN_CFW_UX_RING_UPDATE(level, charging) host_ring_update(level, charging)
#define OPEN_CFW_UX_RING_STATE_SET(level, charging) host_ring_state_set(level, charging)
#define OPEN_CFW_UX_RING_LEVEL_GET() host_ring_level_get()
#define OPEN_CFW_UX_RING_CHARGING_GET() host_ring_charging_get()
#define OPEN_CFW_UX_RING_NOTIFY(key, value) host_ring_notify(key, value)

#endif
