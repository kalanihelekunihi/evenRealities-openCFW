/* Stock source: D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_system\ux_system.c
 * Native UX_LocalSystemStatusSyncHandler 0x47cf60..0x47d818,
 * UX_GetSelfRingStatus 0x47d8e4..0x47d8f0 and the two ring-status UI
 * helpers 0x47d9c4..0x47d9fa.
 *
 * The shared status byte (RAM 0x20075043) packs the left/right peer state:
 *   bit0 self OTA, bit1 peer OTA, bit2 self BLE, bit3 peer BLE,
 *   bit4 self ring, bit5 peer ring, bit6 ring MAC set.
 * Peer messages arrive through UI registry entry 0x103 (ROM 0x6a4740). */
#include <stdint.h>
#include <stddef.h>

/* Eight-byte inter-arm status message (templates at ROM 0x78ede4/0x78edec). */
typedef struct {
    uint16_t id;        /* +0 SYSTEM_*_ID, see below */
    uint8_t  hdr[2];    /* +2 template bytes 01 00 */
    uint8_t  self_role; /* +4 msgSelfRole: sender role */
    uint8_t  peer_role; /* +5 msgPeerRole: addressed role */
    uint8_t  state;     /* +6 */
    uint8_t  pad;       /* +7 */
} ux_system_status_msg_t;
_Static_assert(sizeof(ux_system_status_msg_t) == 8u, "ux_system message");

enum {
    SYSTEM_OTA_STATUS_ID = 1u,
    SYSTEM_BLE_STATUS_ID = 2u,
    SYSTEM_BLE_STATUS_REPLY_ID = 3u,
    SYSTEM_BLE_STATUS_RING_MAC_SET_ID = 4u,
    SYSTEM_BLE_STATUS_RING_QUERY_ID = 5u,
    SYSTEM_BLE_STATUS_RING_REPLY_ID = 6u,
};

extern volatile uint8_t audio_ota_packed_status; /* RAM 0x20075043 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint8_t audio_uart_device_role_get(void);          /* 0x45a568, R = 1, L = 2 */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void)); /* 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void), uint32_t, uint32_t); /* 0x47697e */
extern void audio_ble_master_connect_event(void);        /* 0x4a1b60 APP_MasterConnectEvent */
extern uint32_t audio_wear_child_47432c(void);            /* 0x47432c */
extern uint32_t audio_wear_child_474100(void);            /* 0x474100 */
extern int32_t SVC_Settings_InputEventCheck(void);        /* 0x46b0ec */
extern uint8_t audio_ux_get_system_ble_status(void);      /* 0x47d8ce UX_GetSystemBLEStatus */
extern void UX_SendBLEStatusToPeer(void);                 /* 0x47ce90 */
extern void audio_uart_ring_sync_active(void);            /* 0x47ced6 UX_SendRingStatusToPeer */
extern uint32_t audio_uart_ring_active(void);             /* 0x4a2914 central_is_ring_owner_side */
extern uint32_t audio_uart_ring_mac_ready(void);          /* 0x4a2fdc APP_MasterRingMacIsSet */
extern void APP_MasterCancelRingConnectRetry(uint32_t);   /* 0x4a2ea4 */
extern void CB_BLE_STATUS_Notify(uint32_t, uint32_t);     /* 0x4abd60 */
extern uint32_t system_alert_ring_event_4d306c(uint8_t);  /* 0x4d306c, alert 0x21, 10 s throttle */
extern void dashboard_ring_status_post_49e448(uint8_t, uint8_t); /* 0x49e448, dashboard event 0x13 */
extern uint32_t audio_ble_peer_ring_status_47d8f0(void);  /* 0x47d8f0 UX_GetPeerRingStatus */

static const char module[] = "ux.setting"; /* ROM 0x78c908 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_system\\ux_system.c"; /* ROM 0x70874c */
static const char function[] = "UX_LocalSystemStatusSyncHandler"; /* ROM 0x768170 */

static const char s_raw[] = "raw_data = 0x%x,len = %d"; /* ROM 0x774758 */
static const char c_raw[] = "[ux.setting]raw_data = 0x%x,len = %d"; /* ROM 0x751454 */
static const char s_self_role[] = "pHeadMsg->msgSelfRole = %d %d(R = 1|L=2)"; /* ROM 0x746b3c */
static const char c_self_role[] = "[ux.setting]pHeadMsg->msgSelfRole = %d %d(R = 1|L=2)"; /* ROM 0x7261a8 */
static const char s_peer_role[] = "pHeadMsg->msgPeerRole = %d %d"; /* ROM 0x768190 */
static const char c_peer_role[] = "[ux.setting]pHeadMsg->msgPeerRole = %d %d"; /* ROM 0x746b68 */
static const char s_ota[] = "SYSTEM_OTA_STATUS_ID\r\n"; /* ROM 0x77d7ec */
static const char c_ota[] = "[ux.setting]SYSTEM_OTA_STATUS_ID\r\n"; /* ROM 0x75d314 */
static const char s_ota_self[] = "SYSTEM_OTA_STATUS_ID state come from self = %d"; /* ROM 0x73b6b4 */
static const char c_ota_self[] = "[ux.setting]SYSTEM_OTA_STATUS_ID state come from self = %d"; /* ROM 0x71b40c */
static const char s_ota_peer[] = "SYSTEM_OTA_STATUS_ID state come from peer = %d"; /* ROM 0x73b6e4 */
static const char c_ota_peer[] = "[ux.setting]SYSTEM_OTA_STATUS_ID state come from peer = %d"; /* ROM 0x71b448 */
static const char s_right[] = "RIGHT"; /* ROM 0x78edcc */
static const char s_left[] = "LEFT";   /* ROM 0x78edd4 */
static const char s_ble_role[] = "SYSTEM_BLE_STATUS_ID ROLE = %s"; /* ROM 0x7681b0 */
static const char c_ble_role[] = "[ux.setting]SYSTEM_BLE_STATUS_ID ROLE = %s"; /* ROM 0x746b94 */
static const char s_ble_status[] =
    "SYSTEM_BLE_STATUS_ID selfBleStatus = %d, peerBleStatus = %d"; /* ROM 0x71b484 */
static const char c_ble_status[] =
    "[ux.setting]SYSTEM_BLE_STATUS_ID selfBleStatus = %d, peerBleStatus = %d"; /* ROM 0x6ff6bc */
static const char s_ble_ring[] =
    "SYSTEM_BLE_STATUS_ID selfBleRingStatus = %d, peerBleRingStatus = %d"; /* ROM 0x708790 */
static const char c_ble_ring[] =
    "[ux.setting]SYSTEM_BLE_STATUS_ID selfBleRingStatus = %d, peerBleRingStatus = %d"; /* ROM 0x6f11b8 */
static const char s_ble_self[] = "SYSTEM_BLE_STATUS_ID state come from self = %d"; /* ROM 0x73b714 */
static const char c_ble_self[] = "[ux.setting]SYSTEM_BLE_STATUS_ID state come from self = %d"; /* ROM 0x71b4c0 */
static const char s_ble_peer[] = "SYSTEM_BLE_STATUS_ID state come from peer = %d"; /* ROM 0x73b744 */
static const char c_ble_peer[] = "[ux.setting]SYSTEM_BLE_STATUS_ID state come from peer = %d"; /* ROM 0x71b4fc */
static const char s_reply_peer[] = "SYSTEM_BLE_STATUS_REPLY_ID state come from peer = %d"; /* ROM 0x7261e0 */
static const char c_reply_peer[] =
    "[ux.setting]SYSTEM_BLE_STATUS_REPLY_ID state come from peer = %d"; /* ROM 0x7087d4 */
static const char s_mac_set[] = "SYSTEM_BLE_STATUS_RING_MAC_SET_ID status=%d"; /* ROM 0x746bc0 */
static const char c_mac_set[] = "[ux.setting]SYSTEM_BLE_STATUS_RING_MAC_SET_ID status=%d"; /* ROM 0x726218 */
static const char s_ring_reply[] = "SYSTEM_BLE_STATUS_RING_REPLY_ID status=%d"; /* ROM 0x746bec */
static const char c_ring_reply[] = "[ux.setting]SYSTEM_BLE_STATUS_RING_REPLY_ID status=%d"; /* ROM 0x726250 */
static const char s_ring_reply_peer[] =
    "SYSTEM_BLE_STATUS_RING_REPLY_ID state come from peer = %d"; /* ROM 0x71b538 */
static const char c_ring_reply_peer[] =
    "[ux.setting]SYSTEM_BLE_STATUS_RING_REPLY_ID state come from peer = %d"; /* ROM 0x6ff704 */
static const char s_ring_query[] = "SYSTEM_BLE_STATUS_RING_QUERY_ID"; /* ROM 0x7681d0 */
static const char c_ring_query[] = "[ux.setting]SYSTEM_BLE_STATUS_RING_QUERY_ID"; /* ROM 0x746c18 */
static const char s_ring_query_peer[] =
    "SYSTEM_BLE_STATUS_RING_QUERY_ID from peer, self owner=%d"; /* ROM 0x71b574 */
static const char c_ring_query_peer[] =
    "[ux.setting]SYSTEM_BLE_STATUS_RING_QUERY_ID from peer, self owner=%d"; /* ROM 0x6ff74c */
static const char s_change[] =
    "CB_EVENT_BLE_STATUS_CHANGE UX_GetSystemBLEStatus() = %d"; /* ROM 0x726288 */
static const char c_change[] =
    "[ux.setting]CB_EVENT_BLE_STATUS_CHANGE UX_GetSystemBLEStatus() = %d"; /* ROM 0x708818 */

/* Each argument expression is evaluated separately for the two sinks, as in stock. */
#define UX_LOG(level, line, code, plain, compact, ...) do {                         \
    if (audio_log_flags() & 2u)                                                     \
        audio_log_extended((level), module, path, function, (line), (plain), ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                      \
        (void)compress_log_output((code), (compact), (compact), ##__VA_ARGS__);     \
} while (0)

#define STATUS (audio_ota_packed_status)

/* OTA start on either arm re-queues the master connect event (0x102 ticks). */
static void restart_master_connect(void)
{
    void (*event)(void) = audio_ble_master_connect_event;
    (void)audio_event_loop_remove_delayed(event);
    audio_event_loop_push_delayed(event, 0x102u, 0u);
}

static uint32_t ble_changed(uint8_t before)
{
    return before != audio_ux_get_system_ble_status() ? 1u : 0u;
}

uint32_t UX_LocalSystemStatusSyncHandler(uint32_t event, const ux_system_status_msg_t *msg,
                                         uint32_t len)
{
    uint8_t notify = 0u;
    uint8_t before;
    (void)event;

    UX_LOG(4u, 0x50u, 0x10800000u, s_raw, c_raw, msg, len);
    UX_LOG(4u, 0x51u, 0x10800000u, s_self_role, c_self_role, msg->self_role,
           audio_uart_device_role_get());
    UX_LOG(4u, 0x52u, 0x10800000u, s_peer_role, c_peer_role, msg->peer_role,
           audio_uart_device_role_get());

    switch (msg->id) {
    case SYSTEM_OTA_STATUS_ID:
        UX_LOG(4u, 0x57u, 0x10000000u, s_ota, c_ota);
        if (msg->self_role == audio_uart_device_role_get()) {
            UX_LOG(4u, 0x59u, 0x10400000u, s_ota_self, c_ota_self, msg->state);
            if (msg->state == 1u) {
                STATUS |= 0x01u;
                restart_master_connect();
            } else {
                STATUS &= 0xfeu;
            }
        } else if (msg->peer_role == audio_uart_device_role_get()) {
            UX_LOG(4u, 0x62u, 0x10400000u, s_ota_peer, c_ota_peer, msg->state);
            if (msg->state == 1u) {
                STATUS |= 0x02u;
                restart_master_connect();
            } else {
                STATUS &= 0xfdu;
            }
        }
        if ((STATUS & 0x0cu) == 0x0cu)
            (void)audio_wear_child_47432c();
        else if ((STATUS & 0x0cu) == 0u && SVC_Settings_InputEventCheck() == 1)
            (void)audio_wear_child_474100();
        break;

    case SYSTEM_BLE_STATUS_ID:
        before = audio_ux_get_system_ble_status();
        UX_LOG(4u, 0x7au, 0x10400000u, s_ble_role, c_ble_role,
               audio_uart_device_role_get() == 1u ? s_right : s_left);
        UX_LOG(4u, 0x7bu, 0x10800000u, s_ble_status, c_ble_status,
               (uint8_t)((STATUS >> 2) & 1u), (uint8_t)((STATUS >> 3) & 1u));
        UX_LOG(4u, 0x7cu, 0x10800000u, s_ble_ring, c_ble_ring,
               (uint8_t)((STATUS >> 4) & 1u), (uint8_t)((STATUS >> 5) & 1u));
        if (msg->self_role == audio_uart_device_role_get()) {
            UX_LOG(4u, 0x7eu, 0x10400000u, s_ble_self, c_ble_self, msg->state);
            if (msg->state == 1u) {
                STATUS |= 0x04u;
                notify = (uint8_t)ble_changed(before);
            } else if (msg->state == 0u) {
                STATUS &= 0xfbu;
                notify = (uint8_t)ble_changed(before);
            } else if (msg->state == 3u) {
                STATUS |= 0x10u;
                (void)system_alert_ring_event_4d306c(2u);
                dashboard_ring_status_post_49e448(3u, 0u);
            } else if (msg->state == 2u) {
                STATUS &= 0xefu;
                (void)system_alert_ring_event_4d306c(1u);
                dashboard_ring_status_post_49e448(2u, 0u);
            }
        } else if (msg->peer_role == audio_uart_device_role_get()) {
            UX_LOG(4u, 0x93u, 0x10400000u, s_ble_peer, c_ble_peer, msg->state);
            if (msg->state == 1u) {
                STATUS |= 0x08u;
                notify = (uint8_t)ble_changed(before);
                UX_SendBLEStatusToPeer();
            } else if (msg->state == 0u) {
                STATUS &= 0xf7u;
                notify = (uint8_t)ble_changed(before);
                UX_SendBLEStatusToPeer();
            } else if (msg->state == 3u) {
                STATUS |= 0x20u;
                if (audio_uart_ring_active() == 0u)
                    APP_MasterCancelRingConnectRetry(1u);
            } else if (msg->state == 2u) {
                STATUS &= 0xdfu;
            }
        }
        break;

    case SYSTEM_BLE_STATUS_REPLY_ID:
        before = audio_ux_get_system_ble_status();
        if (msg->peer_role == audio_uart_device_role_get()) {
            UX_LOG(4u, 0xb3u, 0x10400000u, s_reply_peer, c_reply_peer, msg->state);
            if (msg->state == 1u) {
                STATUS |= 0x08u;
                notify = (uint8_t)ble_changed(before);
            } else if (msg->state == 0u) {
                STATUS &= 0xf7u;
                notify = (uint8_t)ble_changed(before);
            }
        }
        break;

    case SYSTEM_BLE_STATUS_RING_MAC_SET_ID:
        UX_LOG(3u, 0xc1u, 0x0c400000u, s_mac_set, c_mac_set, msg->state);
        STATUS = (uint8_t)((STATUS & 0xbfu) | ((msg->state & 1u) << 6));
        if (((STATUS >> 6) & 1u) == 0u) {
            STATUS &= 0xefu;
            STATUS &= 0xdfu;
        }
        if (audio_uart_device_role_get() == 1u)
            CB_BLE_STATUS_Notify(1u, (uint8_t)((STATUS >> 6) & 1u));
        break;

    case SYSTEM_BLE_STATUS_RING_QUERY_ID:
        UX_LOG(3u, 0xe5u, 0x0c000000u, s_ring_query, c_ring_query);
        if (msg->peer_role == audio_uart_device_role_get()) {
            UX_LOG(4u, 0xe7u, 0x10400000u, s_ring_query_peer, c_ring_query_peer,
                   (uint8_t)audio_uart_ring_active());
            if (audio_uart_ring_active() != 0u)
                audio_uart_ring_sync_active();
        }
        break;

    case SYSTEM_BLE_STATUS_RING_REPLY_ID:
        UX_LOG(3u, 0xd0u, 0x0c400000u, s_ring_reply, c_ring_reply, msg->state);
        if (msg->peer_role == audio_uart_device_role_get()) {
            UX_LOG(4u, 0xd2u, 0x10400000u, s_ring_reply_peer, c_ring_reply_peer, msg->state);
            if (msg->state == 3u) {
                STATUS |= 0x20u;
                (void)system_alert_ring_event_4d306c(2u);
                dashboard_ring_status_post_49e448(3u, 0u);
                if (audio_uart_ring_active() == 0u)
                    APP_MasterCancelRingConnectRetry(1u);
            } else if (msg->state == 2u) {
                STATUS &= 0xdfu;
                (void)system_alert_ring_event_4d306c(1u);
                dashboard_ring_status_post_49e448(2u, 0u);
            }
        }
        break;

    default:
        break;
    }

    if (notify != 0u) {
        UX_LOG(4u, 0xf4u, 0x10400000u, s_change, c_change, audio_ux_get_system_ble_status());
        CB_BLE_STATUS_Notify(0u, audio_ux_get_system_ble_status());
    }
    return 0u;
}

uint32_t UX_GetSelfRingStatus(void)
{
    return (uint32_t)(audio_ota_packed_status & 0x1fu) >> 4;
}

/* 0x47d9c4: thin forwarder used by the ring settings pages (0x5b7b60..0x5bb36c). */
uint32_t ux_ring_mac_is_set_47d9c4(void)
{
    return audio_uart_ring_mac_ready();
}

/* 0x47d9cc: ring connected as seen from the arm that owns the ring link. */
uint8_t ux_ring_connected_47d9cc(void)
{
    if (audio_uart_ring_active() != 0u)
        return UX_GetSelfRingStatus() != 0u ? 1u : 0u;
    return audio_ble_peer_ring_status_47d8f0() != 0u ? 1u : 0u;
}
