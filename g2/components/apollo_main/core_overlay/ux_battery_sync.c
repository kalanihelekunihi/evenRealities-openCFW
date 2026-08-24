/* Clean-room reconstruction of app/ux/ux_battery_sync/ux_battery_sync.c. */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t message_id;
    uint8_t payload_length;
    uint8_t source_role;
    uint8_t destination_role;
    int32_t battery_level;
    int8_t is_charging;
    uint8_t reserved[3];
} open_cfw_ux_battery_sync_message;

_Static_assert(sizeof(open_cfw_ux_battery_sync_message) == 12,
    "G2 battery-sync messages must remain twelve bytes");
_Static_assert(offsetof(open_cfw_ux_battery_sync_message, battery_level) == 4,
    "G2 battery level offset changed");
_Static_assert(offsetof(open_cfw_ux_battery_sync_message, is_charging) == 8,
    "G2 charging-state offset changed");

#ifndef OPEN_CFW_UX_CHARGER_SEND
void open_cfw_ux_charger_send(uint8_t message_id);
#define OPEN_CFW_UX_CHARGER_SEND(message_id) \
    open_cfw_ux_charger_send((message_id))
#endif
#ifndef OPEN_CFW_UX_CHARGER_RECEIVE
void open_cfw_ux_charger_receive(
    const open_cfw_ux_battery_sync_message *message
);
#define OPEN_CFW_UX_CHARGER_RECEIVE(message) \
    open_cfw_ux_charger_receive((message))
#endif
#ifndef OPEN_CFW_UX_RING_UPDATE
void open_cfw_ux_ring_update(uint8_t level, uint8_t is_charging);
#define OPEN_CFW_UX_RING_UPDATE(level, is_charging) \
    open_cfw_ux_ring_update((level), (is_charging))
#endif
#ifndef OPEN_CFW_UX_RING_STATE_SET
void open_cfw_ux_ring_state_set(uint8_t level, uint8_t is_charging);
#define OPEN_CFW_UX_RING_STATE_SET(level, is_charging) \
    open_cfw_ux_ring_state_set((level), (is_charging))
#endif
#ifndef OPEN_CFW_UX_RING_LEVEL_GET
uint8_t open_cfw_ux_ring_level_get(void);
#define OPEN_CFW_UX_RING_LEVEL_GET() open_cfw_ux_ring_level_get()
#endif
#ifndef OPEN_CFW_UX_RING_CHARGING_GET
uint8_t open_cfw_ux_ring_charging_get(void);
#define OPEN_CFW_UX_RING_CHARGING_GET() open_cfw_ux_ring_charging_get()
#endif
#ifndef OPEN_CFW_UX_RING_NOTIFY
void open_cfw_ux_ring_notify(uint32_t key, uint32_t value);
#define OPEN_CFW_UX_RING_NOTIFY(key, value) \
    open_cfw_ux_ring_notify((key), (value))
#endif

int32_t open_cfw_ux_battery_sync_handler(
    void *service_context, const void *raw_data, uint16_t length
)
{
    const open_cfw_ux_battery_sync_message *message = raw_data;
    int32_t level;
    uint8_t normalized_level;
    uint8_t normalized_charging;
    uint8_t level_changed;
    uint8_t charging_changed;

    (void)service_context;
    if (message == NULL || length < sizeof(*message)) {
        return -1;
    }

    switch (message->message_id) {
    case 1u:
        OPEN_CFW_UX_CHARGER_SEND(2u);
        return 0;
    case 2u:
    case 3u:
        OPEN_CFW_UX_CHARGER_RECEIVE(message);
        return 0;
    case 4u:
        OPEN_CFW_UX_CHARGER_SEND(3u);
        return 0;
    case 5u:
        level = message->battery_level;
        if (level < 0) {
            level = 0;
        } else if (level > 100) {
            level = 100;
        }
        normalized_level = (uint8_t)level;
        normalized_charging = message->is_charging != 0 ? 1u : 0u;
        level_changed = OPEN_CFW_UX_RING_LEVEL_GET() != normalized_level;
        charging_changed =
            OPEN_CFW_UX_RING_CHARGING_GET() != normalized_charging;
        OPEN_CFW_UX_RING_STATE_SET(normalized_level, normalized_charging);
        if (level_changed != 0u) {
            OPEN_CFW_UX_RING_NOTIFY(0u, normalized_level);
        }
        if (charging_changed != 0u) {
            OPEN_CFW_UX_RING_NOTIFY(1u, normalized_charging);
        }
        return 0;
    case 6u:
        OPEN_CFW_UX_RING_UPDATE(
            OPEN_CFW_UX_RING_LEVEL_GET(), OPEN_CFW_UX_RING_CHARGING_GET()
        );
        return 0;
    default:
        return -1;
    }
}
