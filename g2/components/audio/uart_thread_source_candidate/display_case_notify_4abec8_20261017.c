/* Stock Main _box_detect_notify_status_change 0x4abec8. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern uint8_t audio_uart_case_soc_4acaa0(void);
extern uint8_t audio_uart_case_charge_4acaac(void);
extern uint8_t audio_uart_case_lid_4acab4(void);
extern uint32_t audio_uart_case_status(void); /* 0x4acad0 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
extern uint32_t audio_ota_transfer_active(void); /* 0x4487ac */
extern void audio_uart_case_send_status_510dec(uint32_t,const uint8_t *);

static const char module[]="box.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\box_detect\\service_box_detect.c";
static const char function_name[]="_box_detect_notify_status_change";
static const char message[]="Notify glasses case status change: soc=%d, charge=%d, lid=%d, in_case=%d";
static const char compact[]="[box.detect]Notify glasses case status change: soc=%d, charge=%d, lid=%d, in_case=%d";

void audio_uart_case_notify_4abec8(void)
{
    uint8_t packet[5];
    audio_uart_buffer_zero(packet,5u,0u);
    packet[0]=audio_uart_case_soc_4acaa0();
    packet[1]=audio_uart_case_charge_4acaac();
    packet[2]=audio_uart_case_lid_4acab4();
    packet[3]=(uint8_t)(audio_uart_case_status()==1u);
    if (audio_log_level()&2u)
        audio_log_extended(3u,module,path,function_name,0x6bu,message,
                           packet[0],packet[1],packet[2],packet[3]);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x0d000000u,compact,compact,
                                    packet[0],packet[1],packet[2],packet[3]);
    if (audio_ota_transfer_active()==0u)
        audio_uart_case_send_status_510dec(0u,packet);
}
