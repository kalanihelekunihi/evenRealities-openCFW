/* Native setting type-9 unit route 0x467206..0x4672da; record getter 0x466010. */
#include <stdint.h>
extern uint8_t audio_uart_hand_record[0x30u]; /* stock RAM 0x200736d4 */
extern void audio_uart_ring_unpair_publish_hand_4661a6(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[]="setting_handle_unit_setting";
static const char null_message[]="unit_data is NULL";
static const char null_short[]="[setting]unit_data is NULL";
static const char message[]="Received universal unit setting: unit_format=%d, distance_unit=%d, time_format=%d, date_format=%d, temperature_unit=%d";
static const char compact[]="[setting]Received universal unit setting: unit_format=%d, distance_unit=%d, time_format=%d, date_format=%d, temperature_unit=%d";
__attribute__((noinline)) uint8_t *audio_setting_unit_record_get_466010(void) {
    return audio_uart_hand_record;
}
void audio_setting_dispatch_type9_467206(const uint32_t *data) {
    if(data==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x1e9u,null_message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,null_short,null_short);
        return;
    }
    uint8_t *record=audio_setting_unit_record_get_466010();
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x1f4u,message,
                           data[0],data[1],data[2],data[3],data[4]);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0d400000u,compact,compact,
                                    data[0],data[1],data[2],data[3],data[4]);
    record[1]=(uint8_t)data[0];
    record[2]=(uint8_t)data[3];
    record[3]=(uint8_t)data[1];
    *(uint32_t *)(void *)(record+0x18u)=data[2];
    record[4]=(uint8_t)data[4];
    audio_uart_ring_unpair_publish_hand_4661a6();
}
