/* Native APP_SlaveHanderInit 0x46ed94, full ordered profile setup. */
#include <stdint.h>
extern const uint8_t audio_ble_slave_registration_table[]; /* live source table 0x200003e0 */
extern const uint8_t audio_ble_slave_profile_table[]; /* ROM 0x78f6d2 */
extern const uint8_t *audio_ble_slave_registration_slot; /* RAM 0x2007434c */
extern const uint8_t *audio_ble_slave_profile_slot; /* RAM 0x20074350 */
extern uint8_t *audio_ble_profile_connection_context; /* RAM pointer cell 0x2007432c */
extern uint8_t *audio_ble_slave_mode_context; /* RAM pointer cell 0x20074330 */
extern uint8_t *audio_ble_slave_subcontext; /* RAM pointer cell 0x20074334 */
extern void audio_ble_adv_name_set(void); /* _bleAdvNameSet 0x46dd44 */
extern void audio_ble_msgtx_set_config(uint8_t,uint8_t *,uint8_t *); /* 0x4780dc */
extern void audio_ble_ota_handler_init(uint8_t); /* 0x4bdd00 */
extern void audio_ble_eus_handler_init(uint8_t); /* 0x4bdf98 */
extern void audio_ble_ess_handler_init(uint8_t); /* 0x4be2d6 */
extern void audio_ble_efs_handler_init(uint8_t); /* 0x4be524 */
extern void audio_ble_nus_handler_init(uint8_t); /* 0x4be7fa */
extern void audio_ble_profile_ancc_init(uint8_t,uint8_t *,uint8_t *); /* 0x4bf742 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
/* Stock 0x0046ED94 (APP_SlaveHanderInit) */
void audio_ble_app_slave_handler_init(uint8_t handler,uint8_t *state,uint8_t *mode) {
    if(audio_log_level()&2u)
      audio_log_extended(4u,"ble.Slave",
        "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c",
        "APP_SlaveHanderInit",0x264u,"APP_SlaveHanderInit");
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x10000000u,"[ble.Slave]APP_SlaveHanderInit","[ble.Slave]APP_SlaveHanderInit");
    audio_ble_slave_registration_slot=audio_ble_slave_registration_table;
    audio_ble_slave_profile_slot=audio_ble_slave_profile_table;
    audio_ble_profile_connection_context=state;
    audio_ble_slave_mode_context=mode;
    audio_ble_slave_subcontext=state+0x2au;
    mode[0x1fu]=0u;
    audio_ble_adv_name_set();
    audio_ble_msgtx_set_config(handler,state,mode);
    audio_ble_ota_handler_init(handler);
    audio_ble_eus_handler_init(handler);
    audio_ble_ess_handler_init(handler);
    audio_ble_efs_handler_init(handler);
    audio_ble_nus_handler_init(handler);
    audio_ble_profile_ancc_init(handler,state,mode);
}
