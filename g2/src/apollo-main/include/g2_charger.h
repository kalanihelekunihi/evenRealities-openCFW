/* Charger common layer and ring-battery service (G2 Apollo main 2.2.6.10).
 *
 * Stock sources:
 *   platform\service\charger\charger_common.c        native 0x4ace10..0x4ad908
 *   platform\service\callback_mgr\cb_charge.c         native 0x4aea40..0x4aeafe
 *   platform\service\ring_battery\service_ring_battery.c native 0x4ff8d4..0x4ffa44
 *   platform\service\callback_mgr\cb_ring_battery.c   native 0x500380..0x5003f2
 *
 * The two temples exchange battery state as 12-byte records on sync service
 * 0x105 (SendDataToPeer 0x4651e0; the ring update uses SendDataToBoth
 * 0x464d1c). UX_BatterySyncHandler 0x5f958c rejects records shorter than 12
 * bytes and dispatches on msg_id. The aggregate SOC is the minimum of local and
 * peer SOC; it is valid only when 0..100, so the -1 start sentinel is invalid.
 *
 * Stock functions of these files already defined elsewhere in g2/src under
 * other names (do not redefine): CHG_InitBatterySync (charge-battery),
 * CHG_GetSoc / CHG_GetIsCharging (app/settings-charge),
 * CB_CHG_InitBatInfoCallbacks / CB_CHG_RegisterBatInfoCallback
 * (app/charge-callback), CB_RING_BAT_Init and the 0x4ff8d4 wrapper
 * (power/ring-battery), SVC_RingBattery_RequestFromPeer (app/service-prepare7). */
#ifndef G2_CHARGER_H
#define G2_CHARGER_H

#include <stdbool.h>
#include <stdint.h>

#define G2_BAT_SYNC_SERVICE 0x105u   /* sync-interface application ID */
#define G2_BAT_SYNC_MSG_LEN 12u
#define G2_BAT_INFO_PAYLOAD_LEN 8u

/* msg_id byte of a 0x105 record, as dispatched by UX_BatterySyncHandler. */
enum {
    G2_BAT_SYNC_REQUEST = 1u,        /* peer answers with RESPONSE */
    G2_BAT_SYNC_RESPONSE = 2u,       /* import peer state, recompute */
    G2_BAT_SYNC_NOTIFY = 3u,         /* import, answer RESPONSE, recompute */
    G2_BAT_SYNC_REQUEST_NOTIFY = 4u, /* peer answers with NOTIFY */
    G2_RING_BAT_UPDATE = 5u,         /* ring level/charging to the other side */
    G2_RING_BAT_REQUEST = 6u,        /* peer answers with RING_BAT_UPDATE */
};

/* Event keys passed to BAT_INFO / RING_BAT_INFO callbacks. */
enum {
    G2_BAT_INFO_EVENT_SOC = 0u,
    G2_BAT_INFO_EVENT_CHARGING = 1u,
};

typedef struct {
    int32_t soc;        /* +0 percent, -1 = unknown */
    int8_t is_charging; /* +4 */
    uint8_t pad[3];
} g2_battery_info_t;
_Static_assert(sizeof(g2_battery_info_t) == G2_BAT_INFO_PAYLOAD_LEN, "battery info is 8 bytes");

typedef struct {
    uint8_t msg_id;      /* +0 G2_BAT_SYNC_* / G2_RING_BAT_* */
    uint8_t payload_len; /* +1 8 when info is filled, 0 for requests */
    uint8_t src_role;    /* +2 sender device role (0x45a568) */
    uint8_t dst_role;    /* +3 2 when sender role is 1, else 1 */
    g2_battery_info_t info; /* +4 */
} g2_battery_sync_msg_t;
_Static_assert(sizeof(g2_battery_sync_msg_t) == G2_BAT_SYNC_MSG_LEN, "sync record is 12 bytes");

/* Callback-manager callbacks receive (event, &value); value is in/out. */
typedef void (*g2_bat_info_cb_t)(uint32_t event, uint32_t *value);

/* charger_common.c */
bool charger_soc_is_valid(uint32_t soc);
bool charger_aggregate_soc_is_valid(void);
uint32_t _CHG_HandleInitSync(void);
void CHG_DeinitBatterySync(void);
void CHG_CompareAndUpdateSoc(void);
void CHG_CompareAndUpdateIsCharging(void);
void CHG_OnBatteryLevelChanged(void);
void CHG_SendBatteryInfoToPeer(uint8_t msg_id);
void CHG_ReceiveBatteryInfoFromPeer(const g2_battery_sync_msg_t *msg);
void CHG_RequestNotifyBatteryInfoFromPeer(void);
int32_t charger_get_local_battery_info(g2_battery_info_t *info);

/* cb_charge.c */
void CB_CHG_DeinitBatInfoCallbacks(void);
void CB_CHG_UnregisterBatInfoCallback(g2_bat_info_cb_t callback);
uint32_t CB_CHG_NotifyBatInfo(uint32_t event, uint32_t value);

/* service_ring_battery.c */
void svc_ring_battery_deinit_4ff8dc(void);
void SVC_RingBattery_Update(uint8_t level, uint8_t is_charging);
void ring_battery_state_set(uint8_t level, uint8_t is_charging);
uint8_t ring_battery_level_get(void);
uint8_t ring_battery_charging_get(void);

/* cb_ring_battery.c */
void cb_ring_battery_forwarder(void *context);
void CB_RING_BAT_Deinit(void);
uint32_t CB_RING_BAT_RegisterCallback(g2_bat_info_cb_t callback);
uint32_t CB_RING_BAT_Notify(uint32_t event, uint32_t value);

#endif
