/* Native _bleAdvNameSet 0x46dd44, including authenticated invalid-state fault. */
#include <stdint.h>
extern uint8_t audio_ble_adv_name_buffer[]; /* product RAM 0x200003ec */
extern uint8_t audio_ble_adv_config_state[]; /* product RAM 0x20003838 */
extern uint8_t *audio_ble_slave_mode_context; /* product pointer cell 0x20074330 */
extern uint32_t audio_uart_service_mode(void); /* native 0x45a570 */
extern void audio_ble_adv_format_data(uint8_t); /* native 0x46dc74 */
extern uint8_t audio_ble_adv_set_scan_response(uint8_t *); /* native 0x46dca4 */
extern void audio_ble_psn_into_advertisement(uint8_t *); /* native 0x46dc14 */
extern void audio_ble_slave_adv_handler_prepare(void); /* native 0x46dccc */
extern uint32_t audio_wsf_interrupt_mask_set(void); /* native 0x5fa0a4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern uint32_t audio_ble_hci_set_custom_bdaddr(const uint8_t *); /* native 0x4b4cd2 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.Slave";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c";
static const char function[]="_bleAdvNameSet";
static uint8_t *word_ptr(uint32_t offset) {
    return *(uint8_t **)(void *)(audio_ble_adv_config_state+offset);
}
void audio_ble_adv_name_set(void) {
    audio_ble_adv_name_buffer[11u]=audio_uart_service_mode()==1u?'R':'L';
    uint8_t *number=word_ptr(12u)+1u;
    audio_ble_adv_format_data(word_ptr(8u)[1u]);
    (void)audio_ble_adv_set_scan_response(number);
    audio_ble_psn_into_advertisement(word_ptr(4u)+1u);
    audio_ble_slave_adv_handler_prepare();
    if(audio_ble_slave_mode_context==0) {
      (void)audio_wsf_interrupt_mask_set();
      *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
      for(;;) { __asm volatile("" ::: "memory"); }
    }
    uint8_t *ctx=audio_ble_slave_mode_context;
    (void)audio_queue_copy_bytes(ctx+15u,number,6u);
    if(audio_log_level()&2u)
      audio_log_extended(3u,module,source,function,0x11du,
        "ble name = %s",audio_ble_adv_name_buffer);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x0c400000u,
        "[ble.Slave]ble name = %s","[ble.Slave]ble name = %s",audio_ble_adv_name_buffer);
    if(audio_log_level()&2u)
      audio_log_extended(3u,module,source,function,0x11eu,
        "ble addr %02X:%02X:%02X:%02X:%02X:%02X",
        ctx[20],ctx[19],ctx[18],ctx[17],ctx[16],ctx[15]);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x0d800000u,
        "[ble.Slave]ble addr %02X:%02X:%02X:%02X:%02X:%02X",
        "[ble.Slave]ble addr %02X:%02X:%02X:%02X:%02X:%02X",
        ctx[20],ctx[19],ctx[18],ctx[17],ctx[16],ctx[15]);
    audio_ble_hci_set_custom_bdaddr(ctx+15u);
}
