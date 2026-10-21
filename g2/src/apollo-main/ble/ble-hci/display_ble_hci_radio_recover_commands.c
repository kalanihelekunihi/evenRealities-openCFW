/* Native radio recovery command wrappers 0x52f094/0x52ef74/0x52efba/
 * 0x52efec. ROM templates at 0x789fb0/0x789fbc/0x78c974/0x6d40e0
 * authenticate these protocol fields; zero-filled tails are generated. */
#include <stdint.h>

extern uint64_t audio_ble_radio_exchange_52e612(void *,const void *,uint32_t,
                                                 void *,uint32_t *);
extern uint32_t codec_crc32(const uint8_t *,uint32_t,const uint32_t *);

static uint32_t exchange(void *context,const uint8_t *command,uint32_t length,
                         uint8_t *response) {
    uint32_t received=0u;
    __builtin_memset(response,0,16u);
    return (uint32_t)audio_ble_radio_exchange_52e612(context,command,length,response,&received);
}

uint32_t audio_ble_radio_recover_read_52f094(void *context,void *output) {
    const uint8_t command[12]={1u,1u,0xfdu,5u,0x88u,0x4bu,0xf0u,0u,8u,0u,0u,0u};
    uint8_t response[16];
    uint32_t result=exchange(context,command,9u,response);
    __builtin_memcpy(output,response+7u,8u);
    return result;
}

uint32_t audio_ble_radio_recover_set_52ef74(void *context,void *output) {
    const uint8_t command[12]={1u,1u,0xfdu,5u,0xa0u,0x7cu,0x40u,0u,8u,0u,0u,0u};
    uint8_t response[16];
    uint32_t result=exchange(context,command,9u,response);
    __builtin_memcpy(output,response+7u,8u);
    return result;
}

uint32_t audio_ble_radio_recover_special_52efba(void *context) {
    const uint8_t command[8]={1u,7u,0xfdu,2u,1u,2u,0u,0u};
    uint8_t response[16];
    return exchange(context,command,6u,response);
}

uint32_t audio_ble_radio_recover_commit_52efec(void *context,const uint8_t *mode) {
    uint8_t command[0x8cu];
    __builtin_memset(command,0,sizeof(command));
    command[0]=1u;command[1]=3u;command[2]=0xfdu;command[3]=0x14u;
    command[4]=0x80u;command[5]=0x5cu;command[6]=0x40u;
    command[8]=2u;
    uint32_t checksum=codec_crc32(mode,8u,0);
    __builtin_memcpy(command+12u,&checksum,4u);
    __builtin_memcpy(command+16u,mode,8u);
    uint8_t response[16];
    return exchange(context,command,0x18u,response);
}
