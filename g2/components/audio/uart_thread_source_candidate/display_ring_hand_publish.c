/* Native service universal setting sync 0x4661a6. */
#include <stdint.h>
extern uint8_t audio_uart_hand_record[0x30u]; /* literal 0x4667ec -> RAM 0x200736d4 */
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern int32_t audio_settings_send_peer_packet(uint16_t,const void *,uint32_t,uint32_t,uint32_t); /* 0x465480 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv_universal_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\service_universal_setting\\service_universal_setting.c";
static const char function[]="svc_universal_setting_sync_config_send";
#define LOG(line,mask,plain,compact,...) do { \
 if(audio_log_level()&2u)audio_log_extended(4u,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_level()&1u)||(audio_log_level()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
void audio_uart_ring_unpair_publish_hand_4661a6(void) {
    uint8_t packet[0x30u];
    audio_uart_buffer_zero(packet,sizeof(packet),0u);
    packet[0]=audio_uart_device_role_get()!=1u;
    (void)audio_queue_copy_bytes(packet+2u,audio_uart_hand_record,0x14u);
    (void)audio_queue_copy_bytes(packet+0x18u,audio_uart_hand_record+0x14u,0x0cu);
    (void)audio_queue_copy_bytes(packet+0x24u,audio_uart_hand_record+0x20u,0x0cu);
    (void)audio_settings_send_peer_packet(0x10du,packet,0x30u,0u,5u);
    const uint8_t *r=audio_uart_hand_record;
    LOG(0x8bu,0x11c00000u,
        "Send universal setting sync, type=%d, metric_unit=%d, date_format=%d, distance_unit=%d, temperature_unit=%d, time_format=%d, dominant_hand=%d",
        "[srv_universal_setting]Send universal setting sync, type=%d, metric_unit=%d, date_format=%d, distance_unit=%d, temperature_unit=%d, time_format=%d, dominant_hand=%d",
        packet[0],r[1],r[2],r[3],r[4],*(const uint32_t *)(const void *)(r+0x18u),r[0x0bu]);
    LOG(0x92u,0x11800000u,
        "screen_off_apptypes=[%d,%d,%d], screen_on_apptypes=[%d,%d,%d]",
        "[srv_universal_setting]screen_off_apptypes=[%d,%d,%d], screen_on_apptypes=[%d,%d,%d]",
        r[5],r[6],r[7],r[8],r[9],r[10]);
    LOG(0x99u,0x11800000u,
        "ring_mac=%02X:%02X:%02X:%02X:%02X:%02X",
        "[srv_universal_setting]ring_mac=%02X:%02X:%02X:%02X:%02X:%02X",
        r[0x11u],r[0x10u],r[0x0fu],r[0x0eu],r[0x0du],r[0x0cu]);
}
