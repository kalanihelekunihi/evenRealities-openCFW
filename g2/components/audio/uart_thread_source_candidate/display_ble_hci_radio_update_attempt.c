/* Native 0x52edf0 radio firmware update attempt. Child operations preserve
 * their own error codes; live configuration cells are read at call time. */
#include <stdint.h>
extern uint32_t audio_ble_radio_io_mode_52dd1c(uint32_t); /* native call writes r0=0 */
extern void audio_ble_radio_alt_mode_52dd24(void);
extern int32_t audio_ble_radio_recover_stop_52e8be(void *);
extern int32_t audio_ble_radio_update_current_52e7c0(void *);
extern int32_t audio_ble_radio_update_prepare_52ed34(void *);
extern int32_t audio_ble_radio_update_erase_52e9b4(void *);
extern int32_t audio_ble_radio_update_write_52ebca(void *,uint32_t);
extern int32_t audio_ble_radio_update_check_52ec84(void *);
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* native 0x480f0c */
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
/* Exact NUL-terminated image literals 0x75d5b0, 0x768b38, 0x746e8c,
 * 0x73b92c, 0x774b34, 0x75d5d0, 0x75d5f0 and 0x774b4c. */
static const char enter_failed[]="Enter CM failed, status:%d\r\n";
static const char in_progress[]="Updating in progress ...\r\n";
static const char erase_failed[]="Erase NVM main area failed, status:%d\r\n";
static const char written[]="Successfully written %d bytes, seconds\r\n";
static const char check_success[]="Check data success\r\n";
static const char write_failed[]="Write data failed, status:%d\r\n";
static const char check_failed[]="Check data failed, status:%d\r\n";
static const char up_to_date[]="Already up to date\r\n";
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
int32_t audio_ble_radio_attempt_52edf0(void *context,uint32_t force) {
    uint32_t size;
    if(audio_ble_radio_io_mode_52dd1c(0u)==0u) {
        size=W(0x20074230u);
    } else {
        audio_ble_radio_alt_mode_52dd24();
        size=W(0x20074240u);
    }
    int32_t result=audio_ble_radio_recover_stop_52e8be(context);
    if(result!=0) {
        audio_ble_hci_boot_log_4733ee(enter_failed,result);
    } else if((uint8_t)force==0u && audio_ble_radio_update_current_52e7c0(context)!=0) {
        audio_ble_hci_boot_log_4733ee(up_to_date);
    } else {
        audio_ble_hci_boot_log_4733ee(in_progress);
        if(B(0x20074f51u)!=0u) (void)audio_ble_radio_update_prepare_52ed34(context);
        result=audio_ble_radio_update_erase_52e9b4(context);
        if(result==0) {
            result=audio_ble_radio_update_write_52ebca(context,size);
            if(result==0) {
                audio_ble_hci_boot_log_4733ee(written,size);
                result=audio_ble_radio_update_check_52ec84(context);
                if(result==0) audio_ble_hci_boot_log_4733ee(check_success);
                else audio_ble_hci_boot_log_4733ee(check_failed,result);
            } else audio_ble_hci_boot_log_4733ee(write_failed,result);
        } else audio_ble_hci_boot_log_4733ee(erase_failed,result);
    }
    if(result==0) (void)g2_codec_pin_function(0xfu,0x93u);
    return result;
}
