/* Native SVC_Settings_Init 0x46be10: live-state restore and service registration. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* RAM 0x20072da8, at least 0x50 bytes */
extern uint8_t *audio_settings_config_previous; /* manager +4, RAM 0x20003700 */
extern uint8_t *audio_settings_als_previous; /* manager +24, RAM 0x20003714 */
extern uint8_t *audio_settings_terminal_previous; /* manager +28, RAM 0x20003718 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern void audio_settings_apply_als(uint32_t); /* native 0x4ae8e8 */
extern void SVC_Settings_DumpSettingConfig(void); /* native 0x46b458 */
extern void SVC_Settings_BatteryCallback(uint32_t,void *); /* native 0x46b3e4 */
extern uint32_t audio_settings_register_battery_callback(void (*)(uint32_t,void *)); /* 0x4aea56 */
extern void audio_settings_apply_display_levels(void); /* 0x46b912 */
extern void audio_settings_send_config_to_peer(void); /* 0x46b930 */

/* Native SVC_Settings_Init 0x46be10. */
uint32_t SVC_Settings_Init(void) {
    audio_uart_buffer_zero(audio_settings_config_live,0x50u,0u);
    (void)audio_queue_copy_bytes(audio_settings_config_live,audio_settings_config_previous,0x1cu);
    (void)audio_queue_copy_bytes(audio_settings_config_live+0x1cu,audio_settings_als_previous,4u);
    (void)audio_queue_copy_bytes(audio_settings_config_live+0x20u,audio_settings_terminal_previous,0xcu);
    uint32_t als_scale=*(const uint32_t *)(const void *)(audio_settings_config_live+0x24u);
    audio_settings_apply_als(als_scale);
    SVC_Settings_DumpSettingConfig();
    (void)audio_settings_register_battery_callback(SVC_Settings_BatteryCallback);
    audio_settings_apply_display_levels();
    audio_settings_send_config_to_peer();
    return 0u;
}
