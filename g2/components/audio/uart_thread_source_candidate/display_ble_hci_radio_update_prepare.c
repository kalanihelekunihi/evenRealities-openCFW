/* Native 0x52ed34 conditional PMIC pump register rewrite. */
#include <stdint.h>
extern int32_t audio_ble_radio_read_command_52ea28(void *,uint32_t,void *,uint32_t);
extern int32_t audio_ble_radio_write_command_52eaf8(void *,uint32_t,const void *,uint32_t);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
static const char success[]="Pump TO 1.9V\r\n";
static const char write_second_fail[]="write register 0xF0041C failed, status:%d\r\n";
static const char read_second_fail[]="read register 0xF0041C failed, status:%d\r\n";
static const char write_first_fail[]="write register 0xF0040C failed, status:%d\r\n";
static const char read_first_fail[]="read register 0xF0040C failed, status:%d\r\n";
int32_t audio_ble_radio_update_prepare_52ed34(void *context) {
    uint32_t value=0u;
    int32_t result=audio_ble_radio_read_command_52ea28(context,0x00f0040cu,&value,4u);
    if(result!=0) {audio_ble_hci_boot_log_4733ee(read_first_fail,result);return result;}
    value &=0xffffe0ffu;
    result=audio_ble_radio_write_command_52eaf8(context,0x00f0040cu,&value,4u);
    if(result!=0) {audio_ble_hci_boot_log_4733ee(write_first_fail,result);return result;}
    result=audio_ble_radio_read_command_52ea28(context,0x00f0041cu,&value,4u);
    if(result!=0) {audio_ble_hci_boot_log_4733ee(read_second_fail,result);return result;}
    value=0x000f0b02u;
    result=audio_ble_radio_write_command_52eaf8(context,0x00f0041cu,&value,4u);
    if(result!=0) audio_ble_hci_boot_log_4733ee(write_second_fail,result);
    else audio_ble_hci_boot_log_4733ee(success);
    return result;
}
