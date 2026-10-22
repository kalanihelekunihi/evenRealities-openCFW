/* UX local settings sync handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_settings\ux_settings.c (tag "ux.setting").
 * Native UX_LocalSettingsSyncHandler 0x5f9ce0..0x5f9ec7, literal pool
 * 0x5f9ec8..0x5f9f13 (0x5f9ec8/0x5f9ecc belong to UX_SettingsCommonDataHandler
 * 0x5f9c8c, see system/registry-callback/registry_callback_5f9c8c.c).
 *
 * Registered in the UI registry table (entry 40, event 0x100) under the name
 * audio_uart_registry_callback_5f9ce0. Only eDevCfgCommandId_TIME_SYNC (0x80)
 * is acted on: the peer's UTC second and time zone are applied when the
 * message roles match, and the periodic RPC_SystemTimeSync is re-armed for
 * 30 s. In production test mode the message is ignored. */
#include <stdint.h>
#include <stddef.h>

enum {
    DEV_CFG_COMMAND_TIME_SYNC = 0x80u, /* eDevCfgCommandId_TIME_SYNC */
    MASTER_ROLE = 1u,
    PRODUCT_MODE_TEST = 1u,
    TIME_SYNC_REARM_MS = 30000u,
};

/* Local settings sync message (pMsg). */
typedef struct {
    uint16_t command_id;     /* +0x00 eDevCfgCommandId_* */
    uint16_t reserved_02;    /* +0x02 */
    uint8_t msg_self_role;   /* +0x04 head.msgSelfRole */
    uint8_t msg_peer_role;   /* +0x05 head.msgPeerRole */
    uint16_t reserved_06;    /* +0x06 */
    uint32_t sys_utc_second; /* +0x08 */
    uint32_t time_zone;      /* +0x0c low byte used, signed */
} g2_ux_local_settings_msg_t;
_Static_assert(offsetof(g2_ux_local_settings_msg_t, sys_utc_second) == 0x08u, "pMsg layout");
_Static_assert(offsetof(g2_ux_local_settings_msg_t, time_zone) == 0x0cu, "pMsg layout");

extern uint8_t productModeGet(void);                                        /* 0x4abe60 */
extern uint32_t display_driver_uled_mode_45a568(void);                      /* 0x45a568 device role */
extern uint32_t audio_log_flags(void);                                      /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);                /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void SVC_SystemTimeSync(uint32_t epoch, int8_t zone);                /* 0x44a1fe */
extern void RPC_SystemTimeSync(void);                                       /* 0x44a2b2 */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void));      /* 0x476ace */
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument,
                                       uint32_t delay_ms);                  /* 0x47697e */

static const char tag[] = "ux.setting"; /* ROM 0x78c8fc */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_settings\\ux_settings.c"; /* ROM 0x6ff674 */
static const char function[] = "UX_LocalSettingsSyncHandler"; /* ROM 0x774720 */
static const char msg_production[] = "In production test mode, skip time sync"; /* ROM 0x751404 */
static const char cmp_production[] =
    "[ux.setting]In production test mode, skip time sync"; /* ROM 0x730cc8 */
static const char msg_raw[] = "raw_data = 0x%x,len = %d"; /* ROM 0x77473c */
static const char cmp_raw[] = "[ux.setting]raw_data = 0x%x,len = %d"; /* ROM 0x75142c */
static const char msg_self_role[] = "pMsg->head.msgSelfRole = %d(MASTER_ROLE = %d)"; /* ROM 0x73b654 */
static const char cmp_self_role[] =
    "[ux.setting]pMsg->head.msgSelfRole = %d(MASTER_ROLE = %d)"; /* ROM 0x71b3d0 */
static const char msg_peer_role[] = "pMsg->head.msgPeerRole = %d %d"; /* ROM 0x768130 */
static const char cmp_peer_role[] = "[ux.setting]pMsg->head.msgPeerRole = %d %d"; /* ROM 0x746ae4 */
static const char msg_time_sync[] = "eDevCfgCommandId_TIME_SYNC\r\n"; /* ROM 0x768150 */
static const char cmp_time_sync[] = "[ux.setting]eDevCfgCommandId_TIME_SYNC\r\n"; /* ROM 0x746b10 */
static const char msg_utc[] = "sysUtcSecond = %lu time_zone = %d"; /* ROM 0x75d2f0 */
static const char cmp_utc[] = "[ux.setting]sysUtcSecond = %lu time_zone = %d"; /* ROM 0x73b684 */

static int compact_log_enabled(void)
{
    return (audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u;
}

/* UX_LocalSettingsSyncHandler. r0 and r3 are unused. */
uint32_t audio_uart_registry_callback_5f9ce0(uint32_t unused, const g2_ux_local_settings_msg_t *msg,
                                             uint32_t length, uint32_t extra)
{
    (void)unused;
    (void)extra;

    if (productModeGet() == PRODUCT_MODE_TEST) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, tag, path, function, 29u, msg_production);
        if (compact_log_enabled())
            (void)compress_log_output(0x10000000u, cmp_production, cmp_production);
        return 0u;
    }

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, tag, path, function, 34u, msg_raw, msg, length);
    if (compact_log_enabled())
        (void)compress_log_output(0x10800000u, cmp_raw, cmp_raw, msg, length);

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, tag, path, function, 35u, msg_self_role, msg->msg_self_role,
                           MASTER_ROLE);
    if (compact_log_enabled())
        (void)compress_log_output(0x10800000u, cmp_self_role, cmp_self_role, msg->msg_self_role,
                                  MASTER_ROLE);

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, tag, path, function, 36u, msg_peer_role, msg->msg_peer_role,
                           (uint8_t)display_driver_uled_mode_45a568());
    if (compact_log_enabled())
        (void)compress_log_output(0x10800000u, cmp_peer_role, cmp_peer_role, msg->msg_peer_role,
                                  (uint8_t)display_driver_uled_mode_45a568());

    if (msg->command_id == DEV_CFG_COMMAND_TIME_SYNC) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, tag, path, function, 40u, msg_time_sync);
        if (compact_log_enabled())
            (void)compress_log_output(0x10000000u, cmp_time_sync, cmp_time_sync);

        /* Apply when this side is master and the peer role equals ours, or
         * when both roles are 0 (single device). */
        if ((msg->msg_self_role == MASTER_ROLE &&
             msg->msg_peer_role == (uint8_t)display_driver_uled_mode_45a568()) ||
            (msg->msg_self_role == 0u && msg->msg_peer_role == 0u)) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(4u, tag, path, function, 43u, msg_utc, msg->sys_utc_second,
                                   msg->time_zone);
            if (compact_log_enabled())
                (void)compress_log_output(0x10800000u, cmp_utc, cmp_utc, msg->sys_utc_second,
                                          msg->time_zone);
            SVC_SystemTimeSync(msg->sys_utc_second, (int8_t)msg->time_zone);
        }
        (void)fw_event_loop_remove_delayed(RPC_SystemTimeSync);
        fw_event_loop_push_delayed(RPC_SystemTimeSync, 0u, TIME_SYNC_REARM_MS);
    }
    return 0u;
}
