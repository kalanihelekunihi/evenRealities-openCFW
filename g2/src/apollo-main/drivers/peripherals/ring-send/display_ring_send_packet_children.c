/* Native ring command children 0x47263c, 0x47269e, 0x4727aa, 0x4728b2,
 * target address copy 0x4a2190, and disable-touch callback 0x4c4fe4. */
#include <stdint.h>
extern volatile uint32_t audio_uart_ring_touch_tick; /* RAM 0x20074900 */
extern volatile uint32_t audio_uart_ring_wear_tick; /* RAM 0x20074904 */
extern volatile uint8_t audio_uart_ring_worn; /* RAM 0x2007500c */
extern uint8_t audio_ble_master_target_address[6]; /* RAM 0x200003c0 */
extern char audio_ble_master_target_name[15]; /* RAM 0x200003c8 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern void audio_uart_ring_touch_event_4c5916(uint16_t,uint32_t,uint8_t,uint8_t);
extern void audio_ble_device_manager_send(const uint8_t *); /* selected 0x4c659a */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t,uint32_t,const void *);
extern uint32_t g2_flashdb_candidate_tick(void); /* selected 0x4490cc */
extern int32_t audio_ble_ring_touch_message(uint8_t); /* selected 0x472426 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ring.proto";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_service.c";
static const char touch_fn[]="RING_CmdTouchUpdata";
static const char touch_fmt[]="RING_CmdTouchUpdata tick = %d, type = %d";
static const char touch_short[]="[ring.proto]RING_CmdTouchUpdata tick = %d, type = %d";
static const char hid_fn[]="RING_CmdHID";
static const char hid_msg[]="ring touch enable ok";
static const char hid_short[]="[ring.proto]ring touch enable ok";
static const char battery_fn[]="RING_CmdBatteryReport";
static const char battery_invalid[]="RING_CmdBatteryReport invalid len: %d";
static const char battery_invalid_short[]="[ring.proto]RING_CmdBatteryReport invalid len: %d";
static const char battery_recv[]="RING battery report recv: battery=%u charge=%u";
static const char battery_recv_short[]="[ring.proto]RING battery report recv: battery=%u charge=%u";
static const char wear_fn[]="RING_CmdWearStatus";
static const char wear_on[]="ring wear: ON";
static const char wear_on_short[]="[ring.proto]ring wear: ON";
static const char wear_duration[]="[TP] wear_ring_remove wear_duration=%ums";
static const char wear_duration_short[]="[ring.proto][TP] wear_ring_remove wear_duration=%ums";
static const char disable_fn[]="app_ring_disable_touch";
static const char disable_text[]="RING_DisableTouch";
static const char disable_short[]="[task.ring]RING_DisableTouch";
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
void audio_uart_ring_target_addr_copy_4a2190(uint8_t *address,uint32_t copy_name) {
    static const char name[]="EVEN R1"; /* authenticated ROM 0x78c9cc */
    if(address!=0)(void)audio_queue_copy_bytes(address,audio_ble_master_target_address,6u);
    if(copy_name!=0u)(void)audio_queue_copy_bytes(audio_ble_master_target_name,name,7u);
}
int32_t audio_uart_ring_touch_ack_47263c(const uint8_t *packet) {
    if(packet==0)return -1;
    if(packet[3]==1u && packet[4]==1u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,hid_fn,0x1d5u,hid_msg);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,hid_short,hid_short);
    }
    return 0;
}
int32_t audio_uart_ring_touch_report_47269e(const uint8_t *packet,uint16_t length) {
    if(packet==0)return -1;
    if(length>7u) {
        uint32_t tick=word(packet+7u);
        if(packet[4]!=8u && audio_uart_ring_touch_tick!=0u &&
           tick-audio_uart_ring_touch_tick<100u)return 0;
        audio_uart_ring_touch_tick=tick;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,touch_fn,500u,touch_fmt,tick,packet[4]);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10800000u,touch_short,touch_short,tick,packet[4]);
    }
    if(packet[3]==0u) {
        switch(packet[4]) {
        case 0u: audio_uart_ring_touch_event_4c5916(4u,3u,0u,0u);break;
        case 1u: audio_uart_ring_touch_event_4c5916(4u,0u,0u,0u);break;
        case 2u: audio_uart_ring_touch_event_4c5916(4u,1u,0u,0u);break;
        case 4u: audio_uart_ring_touch_event_4c5916(4u,5u,packet[5],packet[6]);break;
        case 5u: audio_uart_ring_touch_event_4c5916(4u,4u,packet[5],packet[6]);break;
        case 8u: audio_uart_ring_touch_event_4c5916(4u,14u,0u,0u);break;
        default:break;
        }
    }
    return 0;
}
int32_t audio_uart_ring_device_report_4727aa(const uint8_t *packet,uint16_t length) {
    if(packet==0)return -1;
    if(length<6u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,battery_fn,0x22bu,battery_invalid,length);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,battery_invalid_short,battery_invalid_short,length);
        return -1;
    }
    uint8_t event[8]={4u,0u,2u,0u,packet[4],packet[5],0u,0u};
    audio_ble_device_manager_send(event);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,battery_fn,0x237u,battery_recv,packet[4],packet[5]);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c800000u,battery_recv_short,battery_recv_short,
                                    packet[4],packet[5]);
    return 0;
}
void audio_uart_ring_wear_report_4728b2(const uint8_t *packet) {
    uint8_t worn=packet[4]!=0u;
    if(worn==audio_uart_ring_worn)return;
    audio_uart_ring_worn=worn;
    if(worn!=0u) {
        audio_uart_ring_wear_tick=g2_flashdb_candidate_tick();
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,wear_fn,0x24fu,wear_on);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,wear_on_short,wear_on_short);
    } else if(audio_uart_ring_wear_tick!=0u) {
        uint32_t duration=g2_flashdb_candidate_tick()-audio_uart_ring_wear_tick;
        audio_uart_ring_wear_persist_48eb32(0x60102u,1u,&duration);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,wear_fn,0x253u,wear_duration,duration);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c400000u,wear_duration_short,wear_duration_short,duration);
        audio_uart_ring_wear_tick=0u;
    }
}
void audio_uart_ring_disable_touch_4c4fe4(void) {
    static const char task_module[]="task.ring";
    static const char task_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,task_module,task_path,disable_fn,0x103u,disable_text);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,disable_short,disable_short);
    (void)audio_ble_ring_touch_message(0u);
}
