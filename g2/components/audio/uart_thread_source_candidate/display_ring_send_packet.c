/* Native RING_CmdPackageParse dispatcher 0x472988. Deeper command effects
 * remain genuine typed child imports until their own bodies are reduced. */
#include <stdint.h>
extern int32_t audio_uart_ring_touch_report_47269e(const uint8_t *,uint16_t); /* 0x47269e */
extern int32_t audio_uart_ring_touch_ack_47263c(const uint8_t *); /* 0x47263c */
extern int32_t audio_uart_ring_device_report_4727aa(const uint8_t *,uint16_t); /* 0x4727aa */
extern void audio_uart_ring_wear_report_4728b2(const uint8_t *); /* 0x4728b2 */
extern void audio_uart_ring_target_addr_copy_4a2190(uint8_t *,uint32_t); /* 0x4a2190 */
extern void audio_ble_master_cleanup_ring_unpair_4a2c9c(const uint8_t *); /* 0x4a2c9c */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void)); /* selected 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* selected 0x47697e */
extern uint32_t audio_ble_master_success_delayed(uint32_t); /* selected 0x4bc418 */
extern void audio_uart_ring_status_delayed_4a285c(void); /* selected */
extern void audio_uart_ring_disable_touch_4c4fe4(void); /* native callback */
extern void audio_ble_master_followup_delayed(void); /* selected 0x4c4ee4 */
extern uint32_t audio_uart_ring_active(void); /* selected 0x4a2914 */
extern void audio_uart_ring_publish_link_ready_4a271e(void); /* selected */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ring.proto";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_service.c";
static const char function[]="RING_CmdPackageParse";
static const char touch_time[]="RING TOUCH_ALGO_REPORT_TIME ok";
static const char touch_time_short[]="[ring.proto]RING TOUCH_ALGO_REPORT_TIME ok";
static const char alp_error[]="RING TOUCH_EVENT_ALP_ATI_ERROR";
static const char alp_error_short[]="[ring.proto]RING TOUCH_EVENT_ALP_ATI_ERROR";
static const char ati_error[]="RING TOUCH_EVENT_ATI_ERROR";
static const char ati_error_short[]="[ring.proto]RING TOUCH_EVENT_ATI_ERROR";
static const char heartbeat[]="RING_GlassesHeartbeat recv ok";
static const char heartbeat_short[]="[ring.proto]RING_GlassesHeartbeat recv ok";
static const char bad_mac[]="RING_INVALID_GLASSES_MAC: ring rejected this glasses, cleanup ring unpair and disconnect, ringMac=%02X:%02X:%02X:%02X:%02X:%02X";
static const char bad_mac_short[]="[ring.proto]RING_INVALID_GLASSES_MAC: ring rejected this glasses, cleanup ring unpair and disconnect, ringMac=%02X:%02X:%02X:%02X:%02X:%02X";
static void log_message(uint8_t severity,uint32_t line,uint32_t mask,const char *plain,const char *compact) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(severity,module,path,function,line,plain);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(mask,compact,compact);
}
static void reschedule(void (*callback)(void),uint32_t delay) {
    (void)audio_event_loop_remove_delayed(callback);
    audio_event_loop_push_delayed(callback,0u,delay);
}
void audio_uart_ring_send_packet_472988(const uint8_t *packet,uint32_t length) {
    switch(packet[2]) {
    case 0x61u:
        (void)audio_uart_ring_touch_report_47269e(packet,(uint16_t)length);
        break;
    case 0x85u:
        (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_success_delayed);
        (void)audio_event_loop_remove_delayed(audio_uart_ring_status_delayed_4a285c);
        if(audio_uart_ring_active()==0u)(void)audio_ble_master_success_delayed(0u);
        else audio_uart_ring_publish_link_ready_4a271e();
        (void)audio_uart_ring_touch_ack_47263c(packet);
        break;
    case 0x8au:
        log_message(3u,0x272u,0x0c000000u,touch_time,touch_time_short);
        break;
    case 0x8bu:
        (void)audio_uart_ring_device_report_4727aa(packet,(uint16_t)length);
        break;
    case 0x8cu:
        audio_uart_ring_wear_report_4728b2(packet);
        break;
    case 0x94u:
        if(packet[4]==0x20u || packet[4]==0x40u) {
            if(packet[4]==0x20u)
                log_message(1u,0x282u,0x04000000u,alp_error,alp_error_short);
            else
                log_message(1u,0x286u,0x04000000u,ati_error,ati_error_short);
            reschedule(audio_uart_ring_disable_touch_4c4fe4,100u);
            reschedule(audio_ble_master_followup_delayed,500u);
        } else {
            log_message(4u,0x28fu,0x10000000u,heartbeat,heartbeat_short);
        }
        break;
    case 0x96u: {
        uint8_t address[6];
        audio_uart_buffer_zero(address,6u,0u);
        audio_uart_ring_target_addr_copy_4a2190(address,0u);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x2aau,bad_mac,
                               address[5],address[4],address[3],address[2],address[1],address[0]);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x09800000u,bad_mac_short,bad_mac_short,
                                        address[5],address[4],address[3],address[2],address[1],address[0]);
        audio_ble_master_cleanup_ring_unpair_4a2c9c(address);
        break;
    }
    default:break;
    }
}
