/* Native 0x52e8be: enter radio configuration mode. The status register and
 * response are live inputs; the original routine has no artificial timeout. */
#include <stdint.h>

extern void audio_ble_hci_radio_reset_52e8a4(void);
extern void audio_ble_radio_wait_pulse_52e854(uint32_t);
extern int32_t audio_ble_radio_exchange_receive_52e1ea(void *,void *,uint32_t *);
extern int32_t g2_lfs_memcmp(const void *,const void *,uint32_t);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern const uint8_t audio_ble_radio_stop_start_log_751638[];
extern const uint8_t audio_ble_radio_stop_retry_log_730e84[];
extern const uint8_t audio_ble_radio_stop_done_log_75d570[];

int32_t audio_ble_radio_recover_stop_52e8be(void *context) {
    const uint8_t expected[4]={4u,0xffu,1u,3u}; /* ROM 0x78ee30 */
    uint8_t response[16];
    uint32_t received=0u;
    __builtin_memset(response,0,sizeof(response));
    audio_ble_hci_boot_log_4733ee(audio_ble_radio_stop_start_log_751638);
    audio_ble_hci_radio_reset_52e8a4();
    for(;;) {
        audio_ble_radio_wait_pulse_52e854(40u);
        if((*(volatile uint32_t *)(uintptr_t)0x40010410u&0x00200000u)==0u)
            continue;
        int32_t result=audio_ble_radio_exchange_receive_52e1ea(context,response,&received);
        if(result!=0) {
            audio_ble_hci_boot_log_4733ee(audio_ble_radio_stop_retry_log_730e84,result);
            audio_ble_hci_radio_reset_52e8a4();
            continue;
        }
        if(g2_lfs_memcmp(response,expected,4u)!=0)
            continue;
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_stop_done_log_75d570);
        return 0;
    }
}
