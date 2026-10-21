/* Native ring message encoders 0x472378/0x4723d6/0x4722d8. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ring.proto";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_service.c";
static const char fn[]="RING_TouchAlgoReportTimeProcess";
static const char message[]="RING_TouchAlgoReportTime send";
static const char short_message[]="[ring.proto]RING_TouchAlgoReportTime send";
uint32_t audio_uart_ring_message_80_472378(uint8_t value) {
    uint8_t frame[254];audio_uart_buffer_zero(frame,254u,0u);
    frame[0]=0u;frame[1]=0x1au;frame[2]=0x85u;frame[3]=1u;
    frame[4]=value==0u?0xffu:0u;
    frame[5]=frame[6]=frame[7]=0xaau;
    (void)audio_uart_ring_ble_send_data_4c4b7e(frame,8u);
    return 0u;
}
uint32_t audio_uart_ring_message_400_4723d6(uint8_t first,uint8_t second) {
    uint8_t frame[254];audio_uart_buffer_zero(frame,254u,0u);
    frame[0]=0u;frame[1]=0x1au;frame[2]=0x89u;frame[3]=1u;
    audio_uart_buffer_zero(frame+4u,4u,0u);
    frame[4]=(uint8_t)((second<<6)|(first<<7));
    (void)audio_uart_ring_ble_send_data_4c4b7e(frame,8u);
    return 0u;
}
uint32_t audio_uart_ring_message_1000_4722d8(uint16_t value) {
    uint8_t frame[254];audio_uart_buffer_zero(frame,254u,0u);
    frame[0]=0u;frame[1]=0x1au;frame[2]=0x8au;frame[3]=1u;
    frame[4]=(uint8_t)value;frame[5]=(uint8_t)(value>>8);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,fn,312u,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_message,short_message);
    (void)audio_uart_ring_ble_send_data_4c4b7e(frame,6u);
    return 0u;
}
