/* Native APP_MasterHanderInit 0x4a19f4, central profile bring-up. */
#include <stdint.h>
extern const uint8_t audio_ble_master_registration_table[]; /* ROM 0x78c9e4 */
extern const uint8_t *audio_ble_master_registration_slot; /* RAM 0x20074354 */
extern uint8_t *audio_ble_master_state_slot; /* RAM 0x200742fc */
extern uint8_t *audio_ble_master_mode_slot; /* RAM 0x20074300 */
extern uint8_t *audio_ble_master_state_shadow; /* RAM 0x20074304 */
extern uint8_t *audio_ble_master_payload_slot; /* RAM 0x20074308 */
extern void audio_ble_set_ring_link_state(uint8_t,const char *); /* 0x49f870 */
extern void audio_ble_ring_handler_init(uint8_t,uint8_t *); /* 0x4c4810 */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_uart_ring_mac_ready(void); /* 0x4a2fdc */
extern void audio_ble_status_reply(uint8_t); /* 0x47d870 */
extern uint32_t audio_uart_ring_active(void); /* 0x4a2914 */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* 0x47697e */
extern void audio_ble_master_start_try_connect_ring(void); /* 0x4a23ac */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[]="APP_MasterHanderInit";
static const char connected[]="APP_MasterHanderInit: ring owner side, ringMac is set, start try connect ring after 15 seconds";
static const char connected_short[]="[ble.master]APP_MasterHanderInit: ring owner side, ringMac is set, start try connect ring after 15 seconds";
static const char missing[]="APP_MasterHanderInit: ring owner side, ringMac is not set, skip try connect ring";
static const char missing_short[]="[ble.master]APP_MasterHanderInit: ring owner side, ringMac is not set, skip try connect ring";
/* Stock 0x004A19F4 (APP_MasterHanderInit) */
void audio_ble_app_master_handler_init(uint8_t handler,uint8_t *state,uint8_t *mode) {
    audio_ble_master_registration_slot=audio_ble_master_registration_table;
    audio_ble_master_state_slot=state;
    audio_ble_master_mode_slot=mode;
    audio_ble_set_ring_link_state(0u,function);
    audio_ble_master_state_shadow=audio_ble_master_state_slot;
    audio_ble_master_payload_slot=audio_ble_master_state_slot+4u;
    audio_ble_ring_handler_init(handler,audio_ble_master_payload_slot);
    if(audio_uart_device_role_get()==1u)
        audio_ble_status_reply((uint8_t)audio_uart_ring_mac_ready());
    if(audio_uart_ring_active()!=0u) {
        if(audio_uart_ring_mac_ready()!=0u) {
            if(audio_log_level()&2u)
                audio_log_extended(3u,module,source,function,0x3f1u,connected);
            if((audio_log_level()&1u)||(audio_log_level()&4u))
                (void)compressed_log_output(0x0c000000u,connected_short,connected_short);
            audio_event_loop_push_delayed(audio_ble_master_start_try_connect_ring,0u,15000u);
        } else {
            if(audio_log_level()&2u)
                audio_log_extended(3u,module,source,function,0x3f4u,missing);
            if((audio_log_level()&1u)||(audio_log_level()&4u))
                (void)compressed_log_output(0x0c000000u,missing_short,missing_short);
        }
    }
}
