/* Native AttsHashDatabaseString 0x53525c; pinned Cordio atts_main.c. */
#include <stdint.h>
extern uint8_t audio_ble_att_common_state[]; /* native attCb 0x200610ac */
extern uint8_t SecCmac(uint8_t *key,uint8_t *message,uint16_t length,
                       uint8_t handler,uint16_t parameter,uint8_t event);
uint8_t AttsHashDatabaseString(uint8_t *key,uint8_t *message,uint16_t length)
{
    return SecCmac(key,message,length,
                   audio_ble_att_common_state[0x60u],0u,0x24u);
}
