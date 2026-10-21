/* Native CB_CHG_RegisterBatInfoCallback 0x4aea56. */
#include <stdint.h>
extern uint8_t audio_charge_callback_manager[]; /* RAM 0x20073f78 */
extern uint32_t audio_callback_mgr_register(void *,void *); /* native 0x510240 */
extern uint32_t audio_callback_mgr_init(void *,const char *); /* native 0x510108 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="cb.charge";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\cb_charge.c";
static const char function[]="CB_CHG_RegisterBatInfoCallback";
static const char message[]="Invalid callback function";
static const char short_message[]="[cb.charge]Invalid callback function";
static const char battery_type[]="BAT_INFO"; /* ROM 0x78a574 */
void audio_settings_init_battery_callbacks(void) {
    (void)audio_callback_mgr_init(audio_charge_callback_manager,battery_type);
}
uint32_t audio_settings_register_battery_callback(void (*callback)(uint32_t,void *)) {
    if(callback==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,42u,message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,short_message,short_message);
        return 0u;
    }
    return audio_callback_mgr_register(audio_charge_callback_manager,(void *)callback);
}
