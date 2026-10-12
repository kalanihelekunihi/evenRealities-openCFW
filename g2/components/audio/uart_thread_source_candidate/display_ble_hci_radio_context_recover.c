/* Native radio context recovery 0x52f0f8. Its child command bodies and
 * authenticated product log strings remain independently attributable. */
#include <stdint.h>

extern int32_t audio_ble_radio_recover_read_52f094(void *,uint32_t *);
extern int32_t audio_ble_radio_recover_stop_52e8be(void *);
extern int32_t audio_ble_radio_recover_set_52ef74(void *,uint32_t *);
extern int32_t audio_ble_radio_recover_special_52efba(void *);
extern int32_t audio_ble_radio_recover_commit_52efec(void *,uint32_t *);
extern int32_t audio_ble_radio_context_check_52e4b4(void *);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern const uint8_t audio_ble_radio_recover_log_start_774b64[];
extern const uint8_t audio_ble_radio_recover_log_read_fail_746eb4[];
extern const uint8_t audio_ble_radio_recover_log_compare_730eb4[];
extern const uint8_t audio_ble_radio_recover_log_match_746edc[];
extern const uint8_t audio_ble_radio_recover_log_skip_774b7c[];
extern const uint8_t audio_ble_radio_recover_log_stop_fail_768b54[];
extern const uint8_t audio_ble_radio_recover_log_set_fail_746f04[];
extern const uint8_t audio_ble_radio_recover_log_special_fail_768b70[];
extern const uint8_t audio_ble_radio_recover_log_commit_fail_768b8c[];
extern const uint8_t audio_ble_radio_recover_log_check_fail_784be0[];

uint64_t audio_ble_radio_context_recover_52f0f8(void *context,uint32_t requested,
                                                 uint32_t skip_read,uint32_t unused) {
    (void)unused;
    uint32_t response[2]={0u,0u};
    uint32_t result=0u;
    if((uint8_t)skip_read==0u) {
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_start_774b64);
        int32_t read=audio_ble_radio_recover_read_52f094(context,response);
        if(read!=0) {
            audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_read_fail_746eb4);
            return ((uint64_t)response[0]<<32u)|result;
        }
        uint32_t old=((response[0]>>8u)&0x1fu)<<1u;
        old|=(response[0]>>7u)&1u;
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_compare_730eb4,
                                      old,(uint8_t)requested);
        if(old==(uint8_t)requested) {
            audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_match_746edc);
            return ((uint64_t)response[0]<<32u)|result;
        }
    } else {
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_skip_774b7c);
    }
    if(audio_ble_radio_recover_stop_52e8be(context)!=0) {
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_stop_fail_768b54);
        result=1u;
    } else if(audio_ble_radio_recover_set_52ef74(context,response)!=0) {
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_set_fail_746f04);
    } else {
        response[1]&=0xffffe07fu;
        uint8_t *mode=(uint8_t *)&response[1];
        mode[0]|=(uint8_t)(requested<<7u);
        mode[1]|=(uint8_t)((requested&0x3fu)>>1u);
        if(audio_ble_radio_recover_special_52efba(context)!=0) {
            audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_special_fail_768b70);
        } else if(audio_ble_radio_recover_commit_52efec(context,response)!=0) {
            audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_commit_fail_768b8c);
        } else if(audio_ble_radio_context_check_52e4b4(context)!=0) {
            audio_ble_hci_boot_log_4733ee(audio_ble_radio_recover_log_check_fail_784be0);
            result=5u;
        }
    }
    return ((uint64_t)response[0]<<32u)|result;
}
