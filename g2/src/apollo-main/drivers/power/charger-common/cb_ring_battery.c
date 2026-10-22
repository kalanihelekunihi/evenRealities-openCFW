/* RING_BAT_INFO callback list, stock D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_ring_battery.c.
 * Native 0x500378..0x5003f1; literal pool 0x5003f4..0x50040f.
 *
 * Same 12-byte callback manager shape as cb_charge.c, at RAM 0x20073f90 with
 * name "RING_BAT_INFO" (ROM 0x7856f0). UX_BatterySyncHandler 0x5f958c notifies
 * event 0 with the ring level and event 1 with the ring charging flag.
 *
 * CB_RING_BAT_Init 0x500380 is already defined as
 * audio_ring_battery_callback_init_500380 in drivers/power/ring-battery. */
#include <stddef.h>
#include <stdint.h>
#include "g2_charger.h"

extern uint8_t audio_ring_battery_callback_manager[12]; /* RAM 0x20073f90 */

extern void dashboard_main_screen_4e93e4(void *context);                     /* 0x4e93e4, g2-dashboard-main-screen */
extern uint32_t CALLBACK_MGR_Deinit(void *manager);                          /* 0x5101ae */
extern uint32_t audio_callback_mgr_register(void *manager, void *callback);  /* CALLBACK_MGR_Register 0x510240 */
extern void audio_even_ai_ancc_display_send_5105bc(void *manager, uint32_t event,
                                                   const uint32_t *value);   /* CALLBACK_MGR_Notify 0x5105bc */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "cb.ring_bat"; /* ROM 0x78a598 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\cb_ring_battery.c"; /* ROM 0x6e6718 */
static const char register_fn[] = "CB_RING_BAT_RegisterCallback"; /* ROM 0x75e570 */
static const char invalid_cb[] = "Invalid ring callback function"; /* ROM 0x75e590 */
static const char invalid_cb_short[] = "[cb.ring_bat]Invalid ring callback function"; /* ROM 0x73c820 */

/* Sits directly before CB_RING_BAT_Init with no log strings of its own, so
 * its stock file is inferred; called once from UI init at 0x49e706. */
void cb_ring_battery_forwarder(void *context) {
    dashboard_main_screen_4e93e4(context);
}

void CB_RING_BAT_Deinit(void) {
    (void)CALLBACK_MGR_Deinit(audio_ring_battery_callback_manager);
}

uint32_t CB_RING_BAT_RegisterCallback(g2_bat_info_cb_t callback) {
    if (callback == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, register_fn, 0x17u, invalid_cb);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, invalid_cb_short, invalid_cb_short);
        return 0u;
    }
    return audio_callback_mgr_register(audio_ring_battery_callback_manager, (void *)callback);
}

uint32_t CB_RING_BAT_Notify(uint32_t event, uint32_t value) {
    audio_even_ai_ancc_display_send_5105bc(audio_ring_battery_callback_manager, event, &value);
    return value;
}
