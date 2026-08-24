#ifndef OPEN_CFW_SERVICE_RING_BATTERY_HOST_H
#define OPEN_CFW_SERVICE_RING_BATTERY_HOST_H

#include <stdint.h>

typedef struct { uint8_t level; uint8_t is_charging; } host_ring_state;
extern host_ring_state host_state;
int32_t host_post_local(uint16_t, const void *, uint16_t, uint8_t);
int32_t host_post_peer(uint16_t, const void *, uint16_t, uint8_t);

#define OPEN_CFW_RING_BATTERY_STATE_ADDRESS ((uintptr_t)&host_state)
#define OPEN_CFW_RING_BATTERY_POST_LOCAL(service, message, length, flags) \
    host_post_local((service), (message), (length), (flags))
#define OPEN_CFW_RING_BATTERY_POST_PEER(service, message, length, flags) \
    host_post_peer((service), (message), (length), (flags))

#endif
