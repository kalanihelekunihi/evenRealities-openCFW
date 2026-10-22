/* Ring battery service, stock D:\01_workspace\s200_ap510b_iar_git\platform\service\ring_battery\service_ring_battery.c.
 * Native 0x4ff8dc..0x4ff8e3 and 0x4ff8e4..0x4ffa43; literal pool 0x4ffa44..0x4ffa6f.
 *
 * Caches the ring's battery level (clamped to 100) and charging flag in two
 * bytes at RAM 0x20074f3a and forwards them on sync service 0x105 as
 * G2_RING_BAT_UPDATE records (msg_id 5) through SendDataToBoth 0x464d1c.
 *
 * Already defined elsewhere: the init wrapper 0x4ff8d4
 * (audio_ring_battery_callback_wrapper_4ff8d4, drivers/power/ring-battery) and
 * SVC_RingBattery_RequestFromPeer 0x4ff99a (audio_uart_service_prepare7,
 * app/service-prepare7). */
#include <stdint.h>
#include "g2_charger.h"

typedef struct {
    uint8_t level;       /* +0 percent, <= 100 */
    uint8_t is_charging; /* +1 0 or 1 */
} g2_ring_battery_state_t;
_Static_assert(sizeof(g2_ring_battery_state_t) == 2u, "ring battery cache is 2 bytes");

extern g2_ring_battery_state_t g2_ring_battery_state; /* RAM 0x20074f3a */

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern int32_t audio_ble_send_status_message(uint32_t app, const uint8_t *data, uint32_t len,
                                             uint32_t flags); /* SendDataToBoth 0x464d1c */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "svc.ring_bat"; /* ROM 0x788ef0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\ring_battery\\service_ring_battery.c"; /* ROM 0x6e1938 */
static const char update_fn[] = "SVC_RingBattery_Update"; /* ROM 0x77bc44 */
static const char update_failed[] = "SVC_RingBattery_Update send failed: ret=%d"; /* ROM 0x7434c0 */
static const char update_failed_short[] = "[svc.ring_bat]SVC_RingBattery_Update send failed: ret=%d"; /* ROM 0x7186d0 */

/* Deinit counterpart of the 0x4ff8d4 init wrapper. */
void svc_ring_battery_deinit_4ff8dc(void) {
    CB_RING_BAT_Deinit();
}

void SVC_RingBattery_Update(uint8_t level, uint8_t is_charging) {
    g2_battery_sync_msg_t msg;
    audio_uart_buffer_zero(&msg, sizeof msg, 0u);
    msg.msg_id = G2_RING_BAT_UPDATE;
    msg.payload_len = G2_BAT_INFO_PAYLOAD_LEN;
    msg.info.soc = (int32_t)level;
    msg.info.is_charging = is_charging != 0u;
    int32_t ret = audio_ble_send_status_message(G2_BAT_SYNC_SERVICE, (const uint8_t *)&msg, sizeof msg, 0u);
    if (ret != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, update_fn, 0x24u, update_failed, ret);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04400000u, update_failed_short, update_failed_short, ret);
    }
}

void ring_battery_state_set(uint8_t level, uint8_t is_charging) {
    if (level > 100u)
        level = 100u;
    g2_ring_battery_state.level = level;
    g2_ring_battery_state.is_charging = is_charging != 0u;
}

uint8_t ring_battery_level_get(void) {
    return g2_ring_battery_state.level;
}

uint8_t ring_battery_charging_get(void) {
    return g2_ring_battery_state.is_charging;
}
