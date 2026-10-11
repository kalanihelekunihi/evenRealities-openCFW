/* Native 0x46b912 and 0x46b930: display level apply and peer configuration. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* RAM 0x20072da8 */
extern const uint8_t audio_settings_version_text[9]; /* ROM 0x78c074: "2.2.6.10" */
extern uint32_t audio_settings_brightness_level(uint8_t); /* 0x46c622 */
extern uint32_t audio_settings_profile_for_role(uint8_t); /* 0x46c600 */
extern uint32_t audio_settings_display_apply(uint32_t,uint32_t); /* 0x46c9d0 */
extern uint32_t audio_settings_device_role(void); /* selected 0x45a568 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439c04 */
extern void *audio_settings_copy_text(void *,const void *,uint32_t); /* 0x44b5a0 */
extern int32_t audio_settings_send_peer_packet(uint16_t,const void *,uint32_t,uint32_t,uint32_t); /* 0x465480 */
void audio_settings_apply_display_levels(void) {
    uint32_t brightness=audio_settings_brightness_level(audio_settings_config_live[8]);
    uint32_t profile=audio_settings_profile_for_role(audio_settings_config_live[9]);
    (void)audio_settings_display_apply(brightness,profile);
}
void audio_settings_send_config_to_peer(void) {
    uint8_t packet[48];
    audio_uart_buffer_zero(packet,48u,0u);
    if(audio_settings_device_role()==1u) packet[0]=0u;
    else {
        packet[0]=1u;
        (void)audio_settings_copy_text(packet+36u,audio_settings_version_text,9u);
    }
    audio_uart_checksum_copy(packet+4u,audio_settings_config_live,28u);
    *(uint32_t *)(void *)(packet+32u)=*(const uint32_t *)(const void *)(audio_settings_config_live+28u);
    (void)audio_settings_send_peer_packet(9u,packet,48u,0u,5u);
}
