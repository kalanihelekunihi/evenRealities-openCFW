/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of platform/service/ring_battery/service_ring_battery.c. */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t message_id;
    uint8_t payload_length;
    uint8_t source_role;
    uint8_t destination_role;
    int32_t battery_level;
    uint8_t is_charging;
    uint8_t reserved[3];
} open_cfw_ring_battery_message;

typedef struct {
    uint8_t level;
    uint8_t is_charging;
} open_cfw_ring_battery_state;

_Static_assert(sizeof(open_cfw_ring_battery_message) == 12,
    "G2 ring-battery message must remain twelve bytes");
_Static_assert(offsetof(open_cfw_ring_battery_message, battery_level) == 4,
    "G2 ring-battery level offset changed");
_Static_assert(offsetof(open_cfw_ring_battery_message, is_charging) == 8,
    "G2 ring-battery charging offset changed");

#ifndef OPEN_CFW_RING_BATTERY_STATE_ADDRESS
#define OPEN_CFW_RING_BATTERY_STATE_ADDRESS 0x20074f3au
#endif
#define OPEN_CFW_RING_BATTERY_STATE \
    (*(volatile open_cfw_ring_battery_state *)(uintptr_t) \
        OPEN_CFW_RING_BATTERY_STATE_ADDRESS)

#ifndef OPEN_CFW_RING_BATTERY_POST_LOCAL
int32_t open_cfw_ring_battery_post_local(
    uint16_t service, const void *message, uint16_t length, uint8_t flags
);
#define OPEN_CFW_RING_BATTERY_POST_LOCAL(service, message, length, flags) \
    open_cfw_ring_battery_post_local((service), (message), (length), (flags))
#endif
#ifndef OPEN_CFW_RING_BATTERY_POST_PEER
int32_t open_cfw_ring_battery_post_peer(
    uint16_t service, const void *message, uint16_t length, uint8_t flags
);
#define OPEN_CFW_RING_BATTERY_POST_PEER(service, message, length, flags) \
    open_cfw_ring_battery_post_peer((service), (message), (length), (flags))
#endif

#if defined(OPEN_CFW_RING_BATTERY_UPDATE_ONLY)
void open_cfw_ring_battery_update(uint8_t level, uint8_t is_charging)
{
    open_cfw_ring_battery_message message = {0};
    message.message_id = 5u;
    message.payload_length = 8u;
    message.battery_level = level;
    message.is_charging = is_charging != 0u ? 1u : 0u;
    (void)OPEN_CFW_RING_BATTERY_POST_LOCAL(0x0105u, &message, sizeof(message), 0u);
}
#elif defined(OPEN_CFW_RING_BATTERY_STATE_SET_ONLY)
void open_cfw_ring_battery_state_set(uint8_t level, uint8_t is_charging)
{
    OPEN_CFW_RING_BATTERY_STATE.level = level > 100u ? 100u : level;
    OPEN_CFW_RING_BATTERY_STATE.is_charging =
        is_charging != 0u ? 1u : 0u;
}
#elif defined(OPEN_CFW_RING_BATTERY_LEVEL_GET_ONLY)
uint8_t open_cfw_ring_battery_level_get(void)
{
    return OPEN_CFW_RING_BATTERY_STATE.level;
}
#elif defined(OPEN_CFW_RING_BATTERY_CHARGING_GET_ONLY)
uint8_t open_cfw_ring_battery_charging_get(void)
{
    return OPEN_CFW_RING_BATTERY_STATE.is_charging;
}
#elif defined(OPEN_CFW_RING_BATTERY_REQUEST_ONLY)
void open_cfw_ring_battery_request_from_peer(void)
{
    open_cfw_ring_battery_message message = {0};
    message.message_id = 6u;
    (void)OPEN_CFW_RING_BATTERY_POST_PEER(0x0105u, &message, sizeof(message), 0u);
}
#endif
