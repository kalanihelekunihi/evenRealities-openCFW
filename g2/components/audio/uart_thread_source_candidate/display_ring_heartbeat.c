/* Native RING_GlassesHeartbeatProcess 0x472244. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void audio_dump_hex(const char *,uint32_t,const uint8_t *,uint32_t); /* selected 0x43dacc */
extern uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *,uint32_t); /* selected */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ring.proto";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_service.c";
static const char function[]="RING_GlassesHeartbeatProcess";
static const char message[]="RING_GlassesHeartbeat send";
static const char compact[]="[ring.proto]RING_GlassesHeartbeat send";
uint32_t audio_uart_ring_heartbeat_472244(void) {
    uint8_t packet[254];
    audio_uart_buffer_zero(packet,sizeof(packet),0u);
    packet[0]=0u;packet[1]=0x1au;packet[2]=0x94u;packet[3]=1u;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x120u,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,compact,compact);
    audio_dump_hex("ring heart",16u,packet,4u);
    (void)audio_uart_ring_ble_send_data_4c4b7e(packet,4u);
    return 0u;
}
