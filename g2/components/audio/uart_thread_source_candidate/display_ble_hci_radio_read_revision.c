/* Native radio revision read 0x52eeea and request/response transfer 0x52ea28.
 * The 0x52f298 ROM word authenticates command 0x00402000. */
#include <stdint.h>

extern uint64_t audio_ble_radio_exchange_52e612(void *context,const void *command,
                                                 uint32_t length,void *response,
                                                 uint32_t *received);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern const uint8_t audio_ble_hci_radio_command_error_75d590[];

int32_t audio_ble_radio_read_command_52ea28(void *context,uint32_t command,
                                              void *output,uint32_t length) {
    uint8_t packet[0x100u];
    uint8_t response[0x104u];
    __builtin_memset(packet,0,sizeof(packet));
    if(context==0||output==0)return 1;
    packet[0]=1u;packet[1]=1u;packet[2]=0xfdu;packet[3]=5u;
    packet[4]=(uint8_t)command;packet[5]=(uint8_t)(command>>8);
    packet[6]=(uint8_t)(command>>16);packet[7]=(uint8_t)(command>>24);
    packet[8]=(uint8_t)length;
    __builtin_memset(response,0,sizeof(response));
    uint32_t received=0u;
    int32_t result=(int32_t)audio_ble_radio_exchange_52e612(context,packet,9u,response,&received);
    if(result==0) {
        if(response[6]==0u)__builtin_memcpy(output,response+7u,(uint8_t)length);
        else {
            audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_command_error_75d590,response[6]);
            result=15;
        }
    }
    return result;
}

int32_t audio_ble_radio_read_revision_52eeea(void *context,volatile uint32_t *output) {
    return audio_ble_radio_read_command_52ea28(context,0x00402000u,(void *)output,4u);
}
