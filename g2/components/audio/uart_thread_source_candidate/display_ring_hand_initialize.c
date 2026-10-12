/* Native svc_universal_setting_init 0x466660: producer of RAM 0x200736d4. */
#include <stdint.h>
extern uint8_t audio_uart_hand_record[0x30u]; /* RAM 0x200736d4 */
extern uint8_t audio_uart_hand_snapshot_context[]; /* RAM struct base 0x200036fc */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void audio_uart_ring_unpair_publish_hand_4661a6(void);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv_universal_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\service_universal_setting\\service_universal_setting.c";
static const char function[]="svc_universal_setting_init";
#define LOG(line,mask,plain,compact,...) do { \
 if(audio_log_level()&2u)audio_log_extended(3u,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_level()&1u)||(audio_log_level()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
uint32_t audio_uart_hand_initialize_466660(void) {
    uint8_t *record=audio_uart_hand_record;
    const uint8_t *snapshot=audio_uart_hand_snapshot_context;
    audio_uart_buffer_zero(record,0x2cu,0u);
    (void)audio_queue_copy_bytes(record,
         *(const uint8_t *const *)(const void *)(snapshot+0x14u),0x14u);
    (void)audio_queue_copy_bytes(record+0x14u,
         *(const uint8_t *const *)(const void *)(snapshot+0x0cu),0x0cu);
    (void)audio_queue_copy_bytes(record+0x20u,
         *(const uint8_t *const *)(const void *)(snapshot+0x10u),0x0cu);
    LOG(0x143u,0x0c000000u,"***default universal_setting***",
        "[srv_universal_setting]***default universal_setting***");
    LOG(0x14au,0x0d800000u,
        "metric_unit=%d, date_format=%d, distance_unit=%d, time_format=%d, temp_unit=%d, dominant_hand=%d",
        "[srv_universal_setting]metric_unit=%d, date_format=%d, distance_unit=%d, time_format=%d, temp_unit=%d, dominant_hand=%d",
        record[1],record[2],record[3],
        *(const uint32_t *)(const void *)(record+0x18u),
        *(const uint32_t *)(const void *)(record+0x24u),record[0x0bu]);
    LOG(0x151u,0x0d800000u,
        "ring_mac=%02X:%02X:%02X:%02X:%02X:%02X",
        "[srv_universal_setting]ring_mac=%02X:%02X:%02X:%02X:%02X:%02X",
        record[0x11u],record[0x10u],record[0x0fu],record[0x0eu],record[0x0du],record[0x0cu]);
    LOG(0x159u,0x0c000000u,"****************",
        "[srv_universal_setting]****************");
    audio_uart_ring_unpair_publish_hand_4661a6();
    return 0u;
}
