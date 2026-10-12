/* Native 0x52eaf8 HCI vendor register write: packet header, payload,
 * exchange and controller status. Caller supplies a valid <=248-byte input. */
#include <stdint.h>
extern uint64_t audio_ble_radio_exchange_52e612(void *,const void *,uint32_t,
                                                 void *,uint32_t *);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
extern const uint8_t audio_ble_hci_radio_command_error_75d590[];
int32_t audio_ble_radio_write_command_52eaf8(void *context,uint32_t address,
                                              const void *input,uint32_t length) {
    uint8_t packet[0x100u];
    uint8_t response[0x10u];
    uint32_t received=0u;
    __builtin_memset(packet,0,sizeof(packet));
    packet[0]=1u;packet[1]=3u;packet[2]=0xfdu;packet[3]=(uint8_t)(length+4u);
    packet[4]=(uint8_t)address;packet[5]=(uint8_t)(address>>8u);
    packet[6]=(uint8_t)(address>>16u);packet[7]=(uint8_t)(address>>24u);
    __builtin_memcpy(packet+8u,input,(uint8_t)length);
    __builtin_memset(response,0,sizeof(response));
    int32_t result=(int32_t)audio_ble_radio_exchange_52e612(
        context,packet,(uint8_t)length+8u,response,&received);
    if(result==0 && response[6]!=0u) {
        audio_ble_hci_boot_log_4733ee((const char *)audio_ble_hci_radio_command_error_75d590,
                                       response[6]);
        return 15;
    }
    return result;
}
