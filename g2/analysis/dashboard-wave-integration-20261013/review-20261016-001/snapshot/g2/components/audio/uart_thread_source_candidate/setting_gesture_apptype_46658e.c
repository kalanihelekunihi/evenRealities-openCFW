/* Native gesture application type setter 0x46658e..0x466660. */
#include <stdint.h>
extern uint8_t audio_uart_hand_record[0x30u]; /* stock RAM 0x200736d4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv_universal_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\service_universal_setting\\service_universal_setting.c";
static const char function[]="svc_universal_setting_set_gesture_apptype";
static const char invalid[]="Invalid operation_type: %d";
static const char invalid_compact[]="[srv_universal_setting]Invalid operation_type: %d";
static const char success[]="Set gesture apptype: screen_on=%d, operation_type=%d, apptype=%d";
static const char success_compact[]="[srv_universal_setting]Set gesture apptype: screen_on=%d, operation_type=%d, apptype=%d";
void audio_setting_gesture_apptype_46658e(uint32_t screen_on,uint32_t operation_type,
                                           uint32_t apptype) {
    uint32_t op=(uint8_t)operation_type;
    if(op>=3u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x12bu,invalid,op);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,invalid_compact,invalid_compact,op);
        return;
    }
    audio_uart_hand_record[(uint8_t)screen_on!=0u?8u+op:5u+op]=(uint8_t)apptype;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x135u,success,
                           (uint8_t)screen_on,op,(uint8_t)apptype);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0cc00000u,success_compact,success_compact,
                                    (uint8_t)screen_on,op,(uint8_t)apptype);
}
