/* Native 0x52e612. ROM slots 0x52eba4/0x52f20c authenticate
 * hardware status 0x40010410 and the 5,000,000 poll limit. */
#include <stdint.h>

extern int32_t audio_ble_radio_exchange_begin_52e0d2(void *,const void *,uint32_t);
extern int32_t audio_ble_radio_exchange_receive_52e1ea(void *,void *,uint32_t *);
extern void audio_ble_hci_boot_delay_491102(uint32_t);

uint64_t audio_ble_radio_exchange_52e612(void *context,const void *command,
                                          uint32_t length,void *response,
                                          uint32_t *received) {
    uint32_t status;
    if(command==0||response==0||received==0)status=12u;
    else {
        status=(uint32_t)audio_ble_radio_exchange_begin_52e0d2(context,command,length);
        if(status==0u) {
            uint32_t poll=0u;
            volatile uint32_t *const hardware=(volatile uint32_t *)(uintptr_t)0x40010410u;
            while((*hardware&0x00200000u)==0u) {
                if(poll==5000000u)break;
                audio_ble_hci_boot_delay_491102(1u);
                ++poll;
            }
            if(poll==5000000u)status=10u;
            else {
                const uint8_t *sent=(const uint8_t *)command;
                uint8_t *reply=(uint8_t *)response;
                do {
                    status=(uint32_t)audio_ble_radio_exchange_receive_52e1ea(context,response,received);
                    if(status!=0u)break;
                } while(reply[4]!=sent[1]||reply[5]!=sent[2]);
            }
        }
    }
    return ((uint64_t)(uint32_t)(uintptr_t)response<<32)|status;
}
