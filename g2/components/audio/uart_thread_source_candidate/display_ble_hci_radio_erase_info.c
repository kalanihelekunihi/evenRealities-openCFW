/* Native 0x52e948 erase NVM info-page vendor command and response status. */
#include <stdint.h>
extern uint64_t audio_ble_radio_exchange_52e612(void *,const void *,uint32_t,
                                                 void *,uint32_t *);
int32_t audio_ble_radio_erase_info_52e948(void *context,uint32_t page,
                                           uint32_t count) {
    uint8_t packet[0x100u];
    uint8_t response[0x10u];
    __builtin_memset(packet,0,sizeof(packet));
    __builtin_memset(response,0,sizeof(response));
    packet[0]=1u;packet[1]=7u;packet[2]=0xfdu;packet[3]=2u;
    packet[4]=(uint8_t)page;packet[5]=(uint8_t)count;
    uint32_t received=0u;
    int32_t status=(int32_t)audio_ble_radio_exchange_52e612(
        context,packet,6u,response,&received);
    if(status==0 && response[6]!=0u) return 15;
    return status;
}
