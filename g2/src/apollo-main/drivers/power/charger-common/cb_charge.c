/* BAT_INFO callback list, stock D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_charge.c.
 * Native 0x4aea40..0x4aeafd; literal pool 0x4aeb00..0x4aeb1f.
 *
 * The list is a 12-byte callback manager at RAM 0x20073f78 (head node, u8
 * count, name "BAT_INFO"); nodes are 8-byte {callback, next} heap cells, so
 * there is no fixed table size. Event 0 carries the aggregate SOC, event 1 the
 * aggregate charging flag (see g2_charger.h).
 *
 * CB_CHG_InitBatInfoCallbacks 0x4aea40 (audio_settings_init_battery_callbacks)
 * and CB_CHG_RegisterBatInfoCallback 0x4aea56
 * (audio_settings_register_battery_callback) are already defined in
 * app/charge-callback/display_charge_callback_register.c. */
#include <stddef.h>
#include <stdint.h>
#include "g2_charger.h"

extern uint8_t audio_charge_callback_manager[12]; /* RAM 0x20073f78 */

extern uint32_t CALLBACK_MGR_Deinit(void *manager);                          /* 0x5101ae */
extern void audio_callback_mgr_unregister(void *manager, void *callback);    /* CALLBACK_MGR_Unregister 0x5103c4 */
extern void audio_even_ai_ancc_display_send_5105bc(void *manager, uint32_t event,
                                                   const uint32_t *value);   /* CALLBACK_MGR_Notify 0x5105bc */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "cb.charge"; /* ROM 0x78a580 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\cb_charge.c"; /* ROM 0x6eb998 */
static const char unregister_fn[] = "CB_CHG_UnregisterBatInfoCallback"; /* ROM 0x75273c */
static const char invalid_cb[] = "Invalid callback function"; /* ROM 0x769fe4 */
static const char invalid_cb_short[] = "[cb.charge]Invalid callback function"; /* ROM 0x74800c */

void CB_CHG_DeinitBatInfoCallbacks(void) {
    (void)CALLBACK_MGR_Deinit(audio_charge_callback_manager);
}

void CB_CHG_UnregisterBatInfoCallback(g2_bat_info_cb_t callback) {
    if (callback == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, unregister_fn, 0x35u, invalid_cb);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, invalid_cb_short, invalid_cb_short);
        return;
    }
    audio_callback_mgr_unregister(audio_charge_callback_manager, (void *)callback);
}

/* Callbacks get (event, &value) and may rewrite value, which is returned. */
uint32_t CB_CHG_NotifyBatInfo(uint32_t event, uint32_t value) {
    audio_even_ai_ancc_display_send_5105bc(audio_charge_callback_manager, event, &value);
    return value;
}
