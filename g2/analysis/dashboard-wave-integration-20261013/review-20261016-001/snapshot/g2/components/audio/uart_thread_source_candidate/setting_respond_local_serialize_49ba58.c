/* Native setting_respond_with_local_data_serialize 0x49ba58..0x49bbb0. */
#include <stdint.h>
extern uint8_t audio_uart_device_role_get(void);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_setting_local_response_encode_49b7c4(uint8_t *,uint32_t *);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t,uint32_t,const void *,uint32_t);
extern uint8_t audio_settings_notify_encode_buffer[256];
extern uint32_t audio_settings_response_command_id_20074860;

static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="setting_respond_with_local_data_serialize";
static const char not_master[]="not master role, not send";
static const char not_master_short[]="[pb_service_setting]not master role, not send";
static const char bad_id[]="invalid command_id (0)";
static const char bad_id_short[]="[pb_service_setting]invalid command_id (0)";
static const char failed[]="respond local_data failed";
static const char failed_short[]="[pb_service_setting]respond local_data failed";
static const char sent[]="[Send Local Data] BLE sent successfully";
static const char sent_short[]="[pb_service_setting][Send Local Data] BLE sent successfully";

uint32_t audio_setting_serialize_local_response_49ba58(void) {
    if(audio_uart_device_role_get()!=1u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,0x142u,not_master);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,not_master_short,not_master_short);
        return 0u;
    }
    uint32_t length=256u;
    if(audio_settings_response_command_id_20074860==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x14au,bad_id);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,bad_id_short,bad_id_short);
        return 1u;
    }
    audio_uart_buffer_zero(audio_settings_notify_encode_buffer,256u,0u);
    if(audio_setting_local_response_encode_49b7c4(audio_settings_notify_encode_buffer,&length)==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x153u,failed);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,failed_short,failed_short);
        return 43u;
    }
    if(audio_uart_device_role_get()==1u)
        (void)audio_ring_pb_tx_ble_475b14(1u,9u,audio_settings_notify_encode_buffer,(uint16_t)length);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x15au,sent);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,sent_short,sent_short);
    return 0u;
}
