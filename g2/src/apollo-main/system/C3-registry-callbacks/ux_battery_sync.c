/* UX_BatterySyncHandler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_battery_sync\ux_battery_sync.c.
 * Native 0x5f958c..0x5f98cf; literal pool 0x5f98d0..0x5f9923. UI registry row 36
 * (sync service 0x105, G2_BAT_SYNC_SERVICE) primary handler. Reconstructed 2026-10-21
 * (C3) from the 2.2.6.10 disassembly; compiles, byte identity not established.
 *
 * Registry primary handler ABI: (event type, data, length); the event type is unused.
 * Rejects records shorter than 12 bytes, then dispatches on msg_id: battery requests
 * are answered through CHG_SendBatteryInfoToPeer, responses and notifications are
 * imported through CHG_ReceiveBatteryInfoFromPeer, and the ring battery records update
 * the ring battery service and notify the RING_BAT_INFO callbacks of what changed.
 * Returns 0, or 0xffffffff (-1) for a short record or an unknown msg_id. */
#include <stdint.h>
#include <stddef.h>
#include "g2_charger.h"

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...);                                            /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char tag[] = "ux.battery_sync"; /* ROM 0x789f00 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_battery_sync\\ux_battery_sync.c"; /* ROM 0x6f1168 */
static const char fn[] = "UX_BatterySyncHandler"; /* ROM 0x77d7bc */
static const char invalid[] = "Invalid battery sync data: raw_data=%p, len=%d"; /* ROM 0x73b4d4 */
static const char invalid_s[] = "[ux.battery_sync]Invalid battery sync data: raw_data=%p, len=%d"; /* ROM 0x711be4 */
static const char header[] =
    "UX_BatterySyncHandler: msg_id=%d, msg_len=%d, self_role=%d, peer_role=%d"; /* ROM 0x6f7c58 */
static const char header_s[] =
    "[ux.battery_sync]UX_BatterySyncHandler: msg_id=%d, msg_len=%d, self_role=%d, peer_role=%d"; /* ROM 0x6e2068 */
static const char request[] = "Received battery sync request"; /* ROM 0x768070 */
static const char request_s[] = "[ux.battery_sync]Received battery sync request"; /* ROM 0x73b504 */
static const char response[] = "Received battery sync response"; /* ROM 0x768090 */
static const char response_s[] = "[ux.battery_sync]Received battery sync response"; /* ROM 0x73b534 */
static const char notification[] = "Received battery sync notification"; /* ROM 0x75d23c */
static const char notification_s[] = "[ux.battery_sync]Received battery sync notification"; /* ROM 0x730c2c */
static const char request_notify[] = "Received battery sync request notify"; /* ROM 0x75133c */
static const char request_notify_s[] = "[ux.battery_sync]Received battery sync request notify"; /* ROM 0x726090 */
static const char ring_request[] = "Received ring battery sync request"; /* ROM 0x75d260 */
static const char ring_request_s[] = "[ux.battery_sync]Received ring battery sync request"; /* ROM 0x730c60 */
static const char ring_update[] =
    "Received ring battery sync update: soc=%d, charge=%d, soc_changed=%d, charge_changed=%d"; /* ROM 0x6e5c40 */
static const char ring_update_s[] = "[ux.battery_sync]Received ring battery sync update: soc=%d, charge=%d, "
                                    "soc_changed=%d, charge_changed=%d"; /* ROM 0x6d81dc */
static const char unknown[] = "Unknown battery sync message ID: %d"; /* ROM 0x75d284 */
static const char unknown_s[] = "[ux.battery_sync]Unknown battery sync message ID: %d"; /* ROM 0x7260c8 */

#define BAT_LOG(level, line, cflags, text, short_text, ...)                                 \
    do {                                                                                    \
        if ((audio_log_flags() & 2u) != 0u)                                                 \
            audio_log_extended((level), tag, file, fn, (line), (text), ##__VA_ARGS__);      \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)               \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__); \
    } while (0)

uint32_t audio_uart_registry_callback_5f958c(uint32_t event, const uint8_t *raw_data, uint32_t len);

/* Stock 0x005F958C (UX_BatterySyncHandler) */
uint32_t audio_uart_registry_callback_5f958c(uint32_t event, const uint8_t *raw_data, uint32_t len)
{
    const g2_battery_sync_msg_t *msg;

    (void)event;
    if (raw_data == NULL || len < G2_BAT_SYNC_MSG_LEN) {
        BAT_LOG(1u, 0x1au, 0x04800000u, invalid, invalid_s, raw_data, len);
        return UINT32_MAX;
    }
    msg = (const g2_battery_sync_msg_t *)raw_data;
    BAT_LOG(4u, 0x21u, 0x11000000u, header, header_s, msg->msg_id, msg->payload_len, msg->src_role,
            msg->dst_role);
    switch (msg->msg_id) {
    case G2_BAT_SYNC_REQUEST:
        BAT_LOG(4u, 0x2cu, 0x10000000u, request, request_s);
        CHG_SendBatteryInfoToPeer(G2_BAT_SYNC_RESPONSE);
        break;
    case G2_BAT_SYNC_RESPONSE:
        BAT_LOG(4u, 0x32u, 0x10000000u, response, response_s);
        CHG_ReceiveBatteryInfoFromPeer(msg);
        break;
    case G2_BAT_SYNC_NOTIFY:
        BAT_LOG(4u, 0x38u, 0x10000000u, notification, notification_s);
        CHG_ReceiveBatteryInfoFromPeer(msg);
        break;
    case G2_BAT_SYNC_REQUEST_NOTIFY:
        BAT_LOG(4u, 0x3eu, 0x10000000u, request_notify, request_notify_s);
        CHG_SendBatteryInfoToPeer(G2_BAT_SYNC_NOTIFY);
        break;
    case G2_RING_BAT_REQUEST: {
        uint8_t charging;
        uint8_t level;
        BAT_LOG(4u, 0x44u, 0x10000000u, ring_request, ring_request_s);
        charging = ring_battery_charging_get();
        level = ring_battery_level_get();
        SVC_RingBattery_Update(level, charging);
        break;
    }
    case G2_RING_BAT_UPDATE: {
        int32_t soc = msg->info.soc;
        uint8_t charge;
        uint8_t soc_changed;
        uint8_t charge_changed;
        if (soc < 0)
            soc = 0;
        else if (soc > 100)
            soc = 100;
        charge = msg->info.is_charging != 0 ? 1u : 0u;
        soc_changed = ring_battery_level_get() != (uint8_t)soc ? 1u : 0u;
        charge_changed = ring_battery_charging_get() != charge ? 1u : 0u;
        BAT_LOG(3u, 0x52u, 0x0d000000u, ring_update, ring_update_s, (uint8_t)soc, charge, soc_changed,
                charge_changed);
        ring_battery_state_set((uint8_t)soc, charge);
        if (soc_changed != 0u)
            (void)CB_RING_BAT_Notify(G2_BAT_INFO_EVENT_SOC, (uint8_t)soc);
        if (charge_changed != 0u)
            (void)CB_RING_BAT_Notify(G2_BAT_INFO_EVENT_CHARGING, charge);
        break;
    }
    default:
        BAT_LOG(2u, 0x60u, 0x08400000u, unknown, unknown_s, msg->msg_id);
        return UINT32_MAX;
    }
    return 0u;
}
