/* Native setting type-10 gesture-list route 0x467308..0x4674a6. */
#include <stdint.h>
extern void audio_setting_gesture_apptype_46658e(uint32_t,uint32_t,uint32_t);
extern uint8_t *audio_setting_unit_record_get_466010(void);
extern void audio_uart_ring_unpair_publish_hand_4661a6(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[]="setting_handle_gesture_control_list";
static const char null_message[]="gesture_list_data is NULL";
static const char null_compact[]="[setting]gesture_list_data is NULL";
static const char empty_message[]="No gesture control items received";
static const char empty_compact[]="[setting]No gesture control items received";
static const char count_message[]="Received gesture control list, count=%d";
static const char count_compact[]="[setting]Received gesture control list, count=%d";
static const char updated_message[]="Updated gesture config: screen_off=[%d,%d,%d], screen_on=[%d,%d,%d]";
static const char updated_compact[]="[setting]Updated gesture config: screen_off=[%d,%d,%d], screen_on=[%d,%d,%d]";
static void log_empty(uint32_t line,const char *message,const char *compact) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08000000u,compact,compact);
}
void audio_setting_dispatch_type10_467308(const uint8_t *data) {
    if(data==0) {
        log_empty(0x208u,null_message,null_compact);
        return;
    }
    uint8_t count=data[0];
    if(count==0u) {
        log_empty(0x20fu,empty_message,empty_compact);
        return;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x213u,count_message,count);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,count_compact,count_compact,count);
    for(uint32_t index=0;index<count;index++) {
        const uint8_t *entry=data+4u+12u*index;
        uint32_t screen_on=*(const uint32_t *)(const void *)entry;
        uint32_t operation_type=*(const uint32_t *)(const void *)(entry+4u);
        uint32_t apptype=entry[8];
        audio_setting_gesture_apptype_46658e((uint8_t)screen_on,(uint8_t)operation_type,
                                               apptype);
    }
    uint8_t *record=audio_setting_unit_record_get_466010();
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x227u,updated_message,
                           record[5],record[6],record[7],record[8],record[9],record[10]);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0d800000u,updated_compact,updated_compact,
                                    record[5],record[6],record[7],record[8],record[9],record[10]);
    audio_uart_ring_unpair_publish_hand_4661a6();
}
