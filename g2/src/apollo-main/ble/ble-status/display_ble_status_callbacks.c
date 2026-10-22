/* Native BLE status callback wrappers 0x4abcc6 and 0x4abd14. */
#include <stdint.h>
uint8_t audio_ble_status_callback_manager[12]; /* native RAM 0x20073f6c */
extern uint32_t audio_callback_mgr_register(void *,void *); /* 0x510240 */
extern void audio_callback_mgr_unregister(void *,void *); /* 0x5103c4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="cb.ble_status";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\cb_ble_status.c";
static const char register_name[]="CB_BLE_STATUS_RegisterCallback";
static const char unregister_name[]="CB_BLE_STATUS_UnregisterCallback";
static const char message[]="Invalid callback function";
static const char short_message[]="[cb.ble_status]Invalid callback function";
static void log_null(const char *function,uint32_t line) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,short_message,short_message);
}
/* Stock 0x4ABCC6 (CB_BLE_STATUS_RegisterCallback) */
void audio_ble_status_register_callback(void (*callback)(uint32_t,const void *)) {
    if(callback==0) {log_null(register_name,41u);return;}
    (void)audio_callback_mgr_register(audio_ble_status_callback_manager,(void *)callback);
}
/* Stock 0x4ABD14 (CB_BLE_STATUS_UnregisterCallback) */
void audio_ble_status_unregister_callback(void (*callback)(uint32_t,const void *)) {
    if(callback==0) {log_null(unregister_name,52u);return;}
    audio_callback_mgr_unregister(audio_ble_status_callback_manager,(void *)callback);
}
