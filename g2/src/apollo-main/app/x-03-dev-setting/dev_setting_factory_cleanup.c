/* Device-setting restore-factory cleanup helper, native 0x542d4c..0x542dc3
 * (literal 0x543908 shared with pb_service_dev_setting.c, which starts right
 * after it at PB_RxRestoreFactory 0x542dc4; stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_dev_config\pb_service_dev_setting.c
 * by placement).
 *
 * Closes a running background/foreground app alert (the master glasses send
 * the close; both sides wait 500 ms), invalidates the KVDB magic, sets
 * onboarding config item 0 to 1, deletes the notification whitelist file and
 * clears all BLE bonds. No filesystem format and no reset; the caller (the
 * pt protocol processor, app/a-55-pt-protocol) does the rest. Returns 0. */
#include <stdint.h>

#define DEVICE_ROLE_MASTER 1u
#define DEVSET_ALERT_DELAY_MS 500u

extern uint8_t audio_uart_device_role_get(void);               /* 0x45a568, 1 = master */
extern uint32_t audio_log_wake_allowed(void);                  /* 0x443484 */
extern uint32_t display_background_app_running_44349c(void);
extern uint32_t display_foreground_app_running_4434b4(void);
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t context);
extern int32_t osDelay(uint32_t ticks);                        /* 0x449376 */
extern int32_t SVC_KvdbInvalidateMagic(void);                  /* 0x4d9a84 */
extern void kvdbOnboardingConfigUpdateAndPersist(uint8_t index, const uint8_t *value); /* 0x4a7820 */
extern int32_t file_remove(const char *path);                  /* 0x47498c */
extern void app_clear_all_bonding_info_4b46ce(void);

int32_t dev_setting_factory_cleanup_542d4c(void);

static const char whitelist_path[] = "user/notify_whitelist.json"; /* ROM 0x76f518 */

static void close_alert_and_wait(uint8_t role)
{
    if (role == DEVICE_ROLE_MASTER)
        audio_system_alert_close_464c36(0u, 0u, 0u, 0u);
    (void)osDelay(DEVSET_ALERT_DELAY_MS);
}

int32_t dev_setting_factory_cleanup_542d4c(void)
{
    uint8_t const role = audio_uart_device_role_get();
    uint8_t onboarding = 1u;

    if (audio_log_wake_allowed() == 1u) {
        if (display_background_app_running_44349c() == 1u)
            close_alert_and_wait(role);
        if (display_foreground_app_running_4434b4() == 1u)
            close_alert_and_wait(role);
    }
    (void)SVC_KvdbInvalidateMagic();
    kvdbOnboardingConfigUpdateAndPersist(0u, &onboarding);
    (void)file_remove(whitelist_path);
    app_clear_all_bonding_info_4b46ce();
    return 0;
}
