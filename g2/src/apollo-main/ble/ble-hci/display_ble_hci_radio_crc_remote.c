/* Native 0x52e6ac HCI CRC32 request and response decode. */
#include <stdint.h>
extern uint64_t audio_ble_radio_exchange_52e612(void *,const void *,uint32_t,
                                                 void *,uint32_t *);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
static const char crc_fail[]="send crc32 calc fail, status: 0x%x, start addr:%x\r\n";
int32_t audio_ble_radio_crc_remote_52e6ac(void *context,uint32_t start,
                                           uint32_t end,uint32_t *result_crc) {
    uint8_t packet[0x100u];
    uint8_t response[0x10u];
    __builtin_memset(packet,0,sizeof(packet));
    __builtin_memset(response,0,sizeof(response));
    packet[0]=1u;packet[1]=0x4eu;packet[2]=0xfcu;packet[3]=8u;
    for(unsigned i=0u;i<4u;i++) {
        packet[4u+i]=(uint8_t)(start>>(8u*i));
        packet[8u+i]=(uint8_t)(end>>(8u*i));
    }
    uint32_t received=0u;
    int32_t status=(int32_t)audio_ble_radio_exchange_52e612(
        context,packet,12u,response,&received);
    if(status==0) {
        if(response[6]==0u) {
            *result_crc=(uint32_t)response[7]|((uint32_t)response[8]<<8u)|
                        ((uint32_t)response[9]<<16u)|((uint32_t)response[10]<<24u);
        } else {
            audio_ble_hci_boot_log_4733ee(crc_fail,response[6],start);
            status=15;
        }
    }
    return status;
}
