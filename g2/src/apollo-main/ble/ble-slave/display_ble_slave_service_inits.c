/* Native 0x4780dc, 0x4bdd00, 0x4bdf98, 0x4be2d6, 0x4be524, 0x4be7fa. */
#include <stdint.h>
extern volatile uint8_t audio_ble_msgtx_handler_id; /* RAM 0x20074f8e */
extern uint8_t *audio_ble_msgtx_state; /* pointer cell 0x20074338 */
extern uint8_t *audio_ble_msgtx_mode; /* pointer cell 0x2007433c */
extern const uint8_t *audio_ble_msgtx_table_slot; /* pointer cell 0x2007435c */
extern const uint8_t audio_ble_msgtx_table[16]; /* ROM 0x784eb0 */
extern uint8_t audio_ble_ota_handler_state[4]; /* RAM 0x200748b4 */
extern uint8_t audio_ble_eus_handler_state[4]; /* RAM 0x200748ac */
extern uint8_t audio_ble_ess_handler_state[4]; /* RAM 0x200748a8 */
extern uint8_t audio_ble_efs_handler_state[4]; /* RAM 0x200748a4 */
extern uint8_t audio_ble_nus_handler_state[4]; /* RAM 0x200748b0 */
extern void audio_ble_ota_reset_export_state(void); /* semantic_OtaResetExportState */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
void audio_ble_msgtx_set_config(uint8_t handler,uint8_t *state,uint8_t *mode) {
    audio_ble_msgtx_handler_id=handler;
    audio_ble_msgtx_state=state;
    audio_ble_msgtx_mode=mode;
    audio_ble_msgtx_table_slot=audio_ble_msgtx_table;
}
void audio_ble_ota_handler_init(uint8_t handler) {
    audio_ble_ota_handler_state[1]=handler;
    audio_ble_ota_handler_state[0]=0u;
    audio_ble_ota_handler_state[2]=0u;
    audio_ble_ota_handler_state[3]=0u;
    audio_ble_ota_reset_export_state();
}
#define PROFILE_INIT(symbol,state,mod,path,name,func,line,compact) \
void symbol(uint8_t handler) { \
    if(audio_log_level()&2u) audio_log_extended(4u,mod,path,name,line,func); \
    if((audio_log_level()&1u)||(audio_log_level()&4u)) \
      (void)compressed_log_output(0x10000000u,compact,compact); \
    state[1]=handler;state[0]=0u;state[2]=0u;state[3]=0u; \
}
PROFILE_INIT(audio_ble_eus_handler_init,audio_ble_eus_handler_state,"profile.eus",
 "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\eus\\profile_eus.c",
 "APP_BleEusHandlerInit","EusHandlerInit",0xa7u,"[profile.eus]EusHandlerInit")
void audio_ble_ess_handler_init(uint8_t handler) {
    audio_ble_ess_handler_state[1]=handler;
    audio_ble_ess_handler_state[0]=0u;
    audio_ble_ess_handler_state[2]=0u;
    audio_ble_ess_handler_state[3]=0u;
}
PROFILE_INIT(audio_ble_efs_handler_init,audio_ble_efs_handler_state,"profile.efs",
 "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\efs\\profile_efs.c",
 "APP_BleEfsHandlerInit","EfsHandlerInit",0xadu,"[profile.efs]EfsHandlerInit")
PROFILE_INIT(audio_ble_nus_handler_init,audio_ble_nus_handler_state,"profile.nus",
 "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\nus\\profile_nus.c",
 "APP_BleNusHandlerInit","NusHandlerInit",0xa6u,"[profile.nus]NusHandlerInit")
