/* Native 0x52eefa reads the NVM info page, erases it and writes back the
 * 248-byte page with its first word replaced by the caller's value. */
#include <stdint.h>
extern int32_t audio_ble_radio_read_command_52ea28(void *,uint32_t,void *,uint32_t);
extern int32_t audio_ble_radio_erase_info_52e948(void *,uint32_t,uint32_t);
extern int32_t audio_ble_radio_write_command_52eaf8(void *,uint32_t,const void *,uint32_t);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
static const char write_fail[]="Write NVM INFO Page 1 failed, status:%d\r\n";
static const char erase_fail[]="Erase NVM INFO Page 1 failed, status:%d\r\n";
static const char read_fail[]="read NVM INFO Page 1 failed, status:%d\r\n";
int32_t audio_ble_radio_commit_52eefa(void *context,uint32_t value) {
    uint8_t page[248u];
    __builtin_memset(page,0,sizeof(page));
    int32_t status=audio_ble_radio_read_command_52ea28(context,0x402000u,page,248u);
    if(status!=0) {audio_ble_hci_boot_log_4733ee(read_fail,status);return status;}
    status=audio_ble_radio_erase_info_52e948(context,1u,1u);
    if(status!=0) {audio_ble_hci_boot_log_4733ee(erase_fail,status);return status;}
    __builtin_memcpy(page,&value,4u);
    status=audio_ble_radio_write_command_52eaf8(context,0x402000u,page,248u);
    if(status!=0) audio_ble_hci_boot_log_4733ee(write_fail,status);
    return status;
}
