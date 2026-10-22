/* Native 0x46dc74/0x46dca4/0x46dc14/0x46dccc advertising data children. */
#include <stdint.h>
extern int32_t audio_ble_format_to_buffer(char *,const char *,...); /* native sprintf 0x4b4728 */
extern uint32_t g2_log_module_length(const char *); /* selected strlen 0x44a43c */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern uint32_t audio_uart_command_pending(void); /* productModeGet 0x4abe60 */
extern int32_t audio_ble_parse_version(const char *,const char *,uint32_t *,uint32_t *,uint32_t *); /* native 0x475fc0 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint8_t audio_ble_adv_name_buffer[]; /* product RAM 0x200003ec */
static const char module[]="ble.Slave";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
/* Stock 0x46DC74 (dmSlaveAdvFormatData) */
void audio_ble_adv_format_data(uint8_t value) {
    char text[8];
    (void)audio_ble_format_to_buffer(text,"%02d",(uint32_t)value%100u);
    (void)audio_queue_copy_bytes(audio_ble_adv_name_buffer+8u,text,g2_log_module_length(text));
}
/* Stock 0x46DCA4 (dmSlaveAdvSetScanRsp) */
uint8_t audio_ble_adv_set_scan_response(uint8_t *address) {
    uint8_t first=address[0];
    (void)audio_ble_format_to_buffer((char *)audio_ble_adv_name_buffer+13u,
      "%02X%02X%02X",address[2],address[1],address[0]);
    (void)audio_queue_copy_bytes(audio_ble_adv_name_buffer+49u,address,6u);
    return first;
}
/* Stock 0x46DC14 (_blePsnIntoADV) */
void audio_ble_psn_into_advertisement(uint8_t *psn) {
    if(audio_log_level()&2u)
      audio_log_extended(4u,module,source,"_blePsnIntoADV",0xe3u,"PSN = %s",psn);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x10400000u,"[ble.Slave]PSN = %s","[ble.Slave]PSN = %s",psn);
    (void)audio_queue_copy_bytes(audio_ble_adv_name_buffer+35u,psn,g2_log_module_length((const char *)psn));
}
/* Stock 0x46DCCC (ble_Slave_handler_1) */
void audio_ble_slave_adv_handler_prepare(void) {
    if(audio_uart_command_pending()==1u) {
      uint32_t major=0u,minor=0u,patch=0u;
      (void)audio_ble_parse_version("2.2.6.10","%d.%d.%d",&major,&minor,&patch);
      (void)audio_ble_format_to_buffer((char *)audio_ble_adv_name_buffer+19u,
        "_V%d%d%d",major,minor,patch);
      audio_ble_adv_name_buffer[56u]=(uint8_t)(g2_log_module_length((const char *)audio_ble_adv_name_buffer)+1u);
    } else {
      audio_ble_adv_name_buffer[19u]=0u;
      audio_ble_adv_name_buffer[56u]=0x14u;
    }
    (void)audio_queue_copy_bytes(audio_ble_adv_name_buffer+58u,audio_ble_adv_name_buffer,
      g2_log_module_length((const char *)audio_ble_adv_name_buffer)+1u);
}
