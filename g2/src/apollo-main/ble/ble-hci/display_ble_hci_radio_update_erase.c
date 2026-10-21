/* Native 0x52e9b4 NVM main-area erase vendor command. */
#include <stdint.h>
extern uint64_t audio_ble_radio_exchange_52e612(void *,const void *,uint32_t,
                                                 void *,uint32_t *);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
static const char erase_start[]="Erasing NVM main area...\r\n"; /* 0x768b00 */
int32_t audio_ble_radio_update_erase_52e9b4(void *context) {
    uint8_t packet[0x100u];
    uint8_t response[0x10u];
    __builtin_memset(packet,0,sizeof(packet));
    __builtin_memset(response,0,sizeof(response));
    audio_ble_hci_boot_log_4733ee(erase_start);
    packet[0]=1u;packet[1]=6u;packet[2]=0xfdu;packet[3]=0u;
    uint32_t received=0u;
    int32_t result=(int32_t)audio_ble_radio_exchange_52e612(
        context,packet,4u,response,&received);
    if(result==0 && response[6]!=0u) return 15;
    return result;
}
